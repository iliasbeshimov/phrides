"""Persistent cache and resolver for dealership contact pages."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING
from urllib.parse import urljoin

from playwright.async_api import BrowserContext, Page

if TYPE_CHECKING:  # pragma: no cover
    from enhanced_stealth_browser_config import EnhancedStealthBrowserManager

# Import DealerInspire bypass
try:
    from src.automation.browser.dealerinspire_bypass import apply_dealerinspire_bypass
except ImportError:
    # Fallback if import fails
    async def apply_dealerinspire_bypass(page, url):
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        return True


def utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def parse_timestamp(value: str | None) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None


def normalize_key(value: str) -> str:
    return value.strip().lower()


@dataclass
class ContactPageRecord:
    dealer_id: str
    dealer_name: str
    website: str
    contact_url: str
    last_verified_at: str
    contact_score: float
    form_type: Optional[str] = None
    total_inputs: Optional[int] = None
    status: str = "active"
    notes: Optional[str] = None
    history: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "ContactPageRecord":
        return cls(
            dealer_id=payload.get("dealer_id", ""),
            dealer_name=payload.get("dealer_name", ""),
            website=payload.get("website", ""),
            contact_url=payload.get("contact_url", ""),
            last_verified_at=payload.get("last_verified_at", ""),
            contact_score=float(payload.get("contact_score", 0.0)),
            form_type=payload.get("form_type"),
            total_inputs=payload.get("total_inputs"),
            status=payload.get("status", "active"),
            notes=payload.get("notes"),
            history=list(payload.get("history", [])),
        )

    def is_stale(self, max_age: timedelta) -> bool:
        verified_at = parse_timestamp(self.last_verified_at)
        if not verified_at:
            return True
        return utc_now() - verified_at >= max_age

    def bump_history(self, source: str, message: str) -> None:
        self.history.append(
            {
                "ts": utc_now().isoformat(),
                "source": source,
                "message": message,
            }
        )


class ContactPageStore:
    """Simple JSON-backed store for dealership contact page metadata."""

    def __init__(self, cache_path: Path | str = "data/contact_page_cache.json") -> None:
        self.path = Path(cache_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._records: Dict[str, ContactPageRecord] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return

        for item in payload:
            record = ContactPageRecord.from_dict(item)
            if record.dealer_id:
                self._records[normalize_key(record.dealer_id)] = record

    def save(self) -> None:
        serialized = [record.to_dict() for record in self._records.values()]
        self.path.write_text(json.dumps(serialized, indent=2, sort_keys=True), encoding="utf-8")

    def get(self, dealer_id: str) -> Optional[ContactPageRecord]:
        return self._records.get(normalize_key(dealer_id))

    def upsert(self, record: ContactPageRecord) -> None:
        self._records[normalize_key(record.dealer_id)] = record

    def mark_inactive(self, dealer_id: str, reason: str) -> None:
        record = self.get(dealer_id)
        if not record:
            return
        record.status = "stale"
        record.notes = reason
        record.bump_history("inactive", reason)
        self.upsert(record)


@dataclass
class ContactPageResolution:
    dealer_id: str
    dealer_name: str
    contact_url: str
    source: str
    contact_score: float
    form_type: Optional[str]
    total_inputs: Optional[int]
    verified_at: str
    homepage_url: Optional[str] = None
    best_form: Optional[Dict[str, Any]] = None
    metadata: Dict[str, object] = field(default_factory=dict)


class ContactPageResolver:
    """Resolve and cache dealership contact pages with discovery fallback."""

    def __init__(
        self,
        browser_manager: "EnhancedStealthBrowserManager",
        detector: object,
        store: ContactPageStore,
        min_score: int = 40,
        refresh_days: int = 30,
        max_contact_links: int = 5,
    ) -> None:
        self.browser_manager = browser_manager
        self.detector = detector
        self.store = store
        self.min_score = min_score
        self.refresh_interval = timedelta(days=refresh_days)
        self.max_contact_links = max_contact_links

    async def resolve(
        self,
        context: BrowserContext,
        *,
        dealer_id: str,
        dealer_name: str,
        homepage_url: str,
        preferred_contact_url: Optional[str] = None,
    ) -> ContactPageResolution:
        record = self.store.get(dealer_id)

        # Check if cached as "no_form" but allow retry if stale (7 days)
        if record and record.status and record.status.lower() == "no_form":
            if not record.is_stale(timedelta(days=7)):
                raise LookupError(f"Contact form unavailable for {dealer_name} (cached as no_form, retry in {7 - (utc_now() - parse_timestamp(record.last_verified_at)).days} days)")
            # Otherwise, fall through to retry discovery
            print(f"   🔄 Retrying {dealer_name} (no_form cache is stale)")

        page = await self.browser_manager.create_enhanced_stealth_page(context)
        try:
            cache_attempted = False
            cache_valid = False
            # Attempt any preferred URL first (e.g., freshly provided by user)
            for label, candidate in self._candidate_urls(preferred_contact_url, record):
                if not candidate:
                    continue
                if label == "cache":
                    cache_attempted = True
                resolution = await self._evaluate_candidate(
                    page,
                    dealer_id=dealer_id,
                    dealer_name=dealer_name,
                    url=candidate,
                    page_label=label,
                    homepage_url=homepage_url,
                )
                if resolution:
                    if label == "cache":
                        cache_valid = True
                    self._persist_resolution(resolution, record)
                    return resolution

            # Only invalidate cache after multiple failures (not just one)
            if record and cache_attempted and not cache_valid:
                failure_count = len([h for h in record.history if "failed verification" in h.get("message", "")])
                if failure_count >= 2:  # Invalidate after 3rd failure
                    self.store.mark_inactive(dealer_id, "cached contact page failed verification (3+ attempts)")
                    self.store.save()
                else:
                    # Just record the failure, keep cache active for retry
                    record.bump_history("validation_failure", f"Validation attempt {failure_count + 1} failed")
                    self.store.save()

            # Discovery fallback
            discovery = await self._discover_contact_page(
                page,
                dealer_id=dealer_id,
                dealer_name=dealer_name,
                homepage_url=homepage_url,
            )
            if discovery:
                self._persist_resolution(discovery, record)
                return discovery

            self.store.mark_inactive(dealer_id, "contact form not detected during discovery")
            self.store.save()
            raise LookupError(f"Unable to locate contact page for {dealer_name}")
        finally:
            await page.close()

    def _candidate_urls(
        self,
        preferred: Optional[str],
        record: Optional[ContactPageRecord],
    ) -> List[Tuple[str, Optional[str]]]:
        candidates: List[Tuple[str, Optional[str]]] = []
        if preferred:
            candidates.append(("preferred", preferred))
        if record and record.contact_url:
            candidates.append(("cache", record.contact_url))
        return candidates

    async def _evaluate_candidate(
        self,
        page: Page,
        *,
        dealer_id: str,
        dealer_name: str,
        url: str,
        page_label: str,
        homepage_url: str,
    ) -> Optional[ContactPageResolution]:
        try:
            # Use DealerInspire bypass if needed
            if 'dealerinspire' in url.lower():
                await apply_dealerinspire_bypass(page, url)
            else:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except Exception:
            return None

        forms = await self._detect_forms(page, page_label, url)
        best_form = self._select_best_form(forms)
        if not best_form:
            return None

        contact_score = best_form.get("relevance_score", 0)
        if contact_score < self.min_score:
            return None

        source = "cache" if page_label == "cache" else page_label
        resolution = self._build_resolution(
            dealer_id=dealer_id,
            dealer_name=dealer_name,
            homepage_url=homepage_url,
            source=source,
            best_form=best_form,
            all_forms=forms,
        )
        resolution.metadata["page_label"] = page_label
        return resolution

    async def _discover_contact_page(
        self,
        page: Page,
        *,
        dealer_id: str,
        dealer_name: str,
        homepage_url: str,
    ) -> Optional[ContactPageResolution]:
        try:
            # Use DealerInspire bypass if needed
            if 'dealerinspire' in homepage_url.lower():
                await apply_dealerinspire_bypass(page, homepage_url)
            else:
                await page.goto(homepage_url, wait_until="domcontentloaded", timeout=30000)
        except Exception:
            return None

        discovered_forms = await self._detect_forms(page, "homepage", homepage_url)
        best_form = self._select_best_form(discovered_forms)
        if best_form and best_form.get("relevance_score", 0) >= self.min_score:
            return self._build_resolution(
                dealer_id=dealer_id,
                dealer_name=dealer_name,
                homepage_url=homepage_url,
                source="discovery",
                best_form=best_form,
                all_forms=discovered_forms,
            )

        contact_links = await self._find_contact_links(page)
        checked_urls = []

        for link in contact_links[: self.max_contact_links]:
            href = link.get("href")
            if not href:
                continue
            candidate_url = self._make_absolute(homepage_url, href)
            if not candidate_url:
                continue
            checked_urls.append(candidate_url)
            try:
                # Use DealerInspire bypass if needed
                if 'dealerinspire' in candidate_url.lower():
                    await apply_dealerinspire_bypass(page, candidate_url)
                else:
                    await page.goto(candidate_url, wait_until="domcontentloaded", timeout=30000)
            except Exception:
                continue
            link_forms = await self._detect_forms(page, link.get("text", "contact"), candidate_url)
            discovered_forms.extend(link_forms)

            best_form = self._select_best_form(discovered_forms)
            if best_form and best_form.get("relevance_score", 0) >= self.min_score:
                resolution = self._build_resolution(
                    dealer_id=dealer_id,
                    dealer_name=dealer_name,
                    homepage_url=homepage_url,
                    source="discovery",
                    best_form=best_form,
                    all_forms=discovered_forms,
                )
                resolution.metadata["contact_links_checked"] = checked_urls
                return resolution

        return None

    async def _detect_forms(self, page: Page, page_name: str, page_url: str) -> List[Dict[str, Any]]:
        forms: List[Dict[str, Any]] = []

        if hasattr(self.detector, "detect_forms_on_page"):
            forms.extend(await self.detector.detect_forms_on_page(page, page_name, page_url))

        # Anchorage-style modal contact forms
        if not forms:
            try:
                modal_trigger = page.locator("a:has-text('Send Us A Message')").first
                if await modal_trigger.count() > 0:
                    await modal_trigger.scroll_into_view_if_needed()
                    await page.wait_for_timeout(500)
                    await modal_trigger.click()
                    await page.wait_for_timeout(800)

                    sales_option = page.locator("a:has-text('Sales')").first
                    if await sales_option.count() > 0:
                        await sales_option.hover()
                        await page.wait_for_timeout(400)
                        await sales_option.click()
                        await page.wait_for_timeout(800)

                        if hasattr(self.detector, "detect_forms_on_page"):
                            forms.extend(
                                await self.detector.detect_forms_on_page(page, f"{page_name} (modal)", page_url)
                            )
            except Exception:
                pass

        return forms

    async def _find_contact_links(self, page: Page) -> List[Dict[str, str]]:
        if hasattr(self.detector, "find_contact_links"):
            return await self.detector.find_contact_links(page)
        return []

    def _select_best_form(self, forms: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not forms:
            return None
        return max(forms, key=lambda item: item.get("relevance_score", 0))

    def _make_absolute(self, base_url: str, href: str) -> Optional[str]:
        if not href:
            return None
        if href.startswith("http://") or href.startswith("https://"):
            return href
        try:
            return urljoin(base_url if base_url.endswith("/") else f"{base_url}/", href)
        except Exception:
            return None

    def _build_resolution(
        self,
        *,
        dealer_id: str,
        dealer_name: str,
        homepage_url: str,
        source: str,
        best_form: Dict[str, Any],
        all_forms: List[Dict[str, Any]],
    ) -> ContactPageResolution:
        contact_score = best_form.get("relevance_score", 0)
        summary = self._summarize_form(best_form)

        metadata: Dict[str, object] = {
            "best_form": best_form,
            "best_form_summary": summary,
            "all_forms": all_forms,
            "contact_links_checked": [],
        }

        return ContactPageResolution(
            dealer_id=dealer_id,
            dealer_name=dealer_name,
            contact_url=best_form.get("page_url") or homepage_url,
            source=source,
            contact_score=contact_score,
            form_type=best_form.get("form_type"),
            total_inputs=best_form.get("total_inputs"),
            verified_at=utc_now().isoformat(),
            homepage_url=homepage_url,
            best_form=best_form,
            metadata=metadata,
        )

    def _summarize_form(self, form: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "contactScore": form.get("relevance_score", 0),
            "totalInputs": form.get("total_inputs", 0),
            "emailFields": form.get("email_inputs", 0),
            "nameFields": form.get("name_inputs", 0),
            "phoneFields": form.get("phone_inputs", 0),
            "messageFields": form.get("textareas", 0),
            "formType": form.get("form_type", "discovered"),
            "pageUrl": form.get("page_url"),
            "pageName": form.get("page_name"),
        }

    def _persist_resolution(
        self,
        resolution: ContactPageResolution,
        existing: Optional[ContactPageRecord],
    ) -> None:
        requires_save = False
        record = existing
        if not record:
            record = ContactPageRecord(
                dealer_id=resolution.dealer_id,
                dealer_name=resolution.dealer_name,
                website=resolution.homepage_url or "",
                contact_url=resolution.contact_url,
                last_verified_at=resolution.verified_at,
                contact_score=resolution.contact_score,
                form_type=resolution.form_type,
                total_inputs=resolution.total_inputs,
                status="active",
            )
            requires_save = True
        else:
            if (
                record.contact_url != resolution.contact_url
                or record.contact_score != resolution.contact_score
            ):
                record.bump_history(
                    resolution.source,
                    f"Updated contact URL from {record.contact_url} to {resolution.contact_url}",
                )
                requires_save = True
            record.contact_url = resolution.contact_url
            record.contact_score = resolution.contact_score
            record.form_type = resolution.form_type
            record.total_inputs = resolution.total_inputs
            record.last_verified_at = resolution.verified_at
            record.status = "active"
            record.notes = None

        self.store.upsert(record)
        if requires_save or resolution.source != "cache":
            self.store.save()
