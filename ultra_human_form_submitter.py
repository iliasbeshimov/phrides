#!/usr/bin/env python3
"""
Ultra-human form submission with advanced behavioral simulation.
Implements realistic pre-submission behavior that mimics actual human patterns.
"""

import asyncio
import random
import sys
from pathlib import Path

# Add project paths
ROOT = Path(__file__).resolve().parent
SRC_ROOT = ROOT / 'src'
for candidate in (ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.append(str(candidate))

from src.automation.forms.form_submitter import FormSubmissionRunner, ContactPayload

class UltraHumanFormSubmitter(FormSubmissionRunner):
    """Enhanced form submitter with ultra-realistic human behavior simulation."""

    async def _ultra_human_navigation(self, page, target_url: str, log_lines):
        """Navigate like a real human - through homepage, not direct URL."""

        # Extract homepage from contact URL
        from urllib.parse import urlparse
        parsed = urlparse(target_url)
        homepage = f"{parsed.scheme}://{parsed.netloc}"

        log_lines.append(f"[human] Starting natural navigation from homepage: {homepage}")

        # 1. Go to homepage first
        await page.goto(homepage)
        await asyncio.sleep(random.uniform(2, 4))

        # 2. Scroll around homepage like browsing
        await page.evaluate("""
            window.scrollTo(0, Math.random() * 500);
        """)
        await asyncio.sleep(random.uniform(1, 2))

        # 3. Look for contact links
        contact_selectors = [
            'a[href*="contact"]',
            'a:has-text("Contact")',
            'a:has-text("Contact Us")',
            'a:has-text("Get in Touch")',
            '[class*="nav"] a:has-text("Contact")',
            '[class*="menu"] a:has-text("Contact")'
        ]

        found_link = False
        for selector in contact_selectors:
            try:
                link = page.locator(selector).first
                if await link.is_visible(timeout=1000):
                    log_lines.append(f"[human] Found contact link: {selector}")
                    # Hover before clicking like a human
                    await link.hover()
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                    await link.click()
                    found_link = True
                    break
            except:
                continue

        if not found_link:
            # Fallback to direct navigation
            log_lines.append("[human] No contact link found, navigating directly")
            await page.goto(target_url)

        await asyncio.sleep(random.uniform(2, 4))
        return page.url

    async def _human_form_review_and_submit(self, page, log_lines):
        """Implement ultra-realistic form review and submission behavior."""

        log_lines.append("[human] Beginning realistic form review sequence")

        # Phase 1: Scroll to see entire form like reviewing
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(random.uniform(1, 2))

        # Gradually scroll down to review fields
        await page.evaluate("""
            const totalHeight = document.body.scrollHeight;
            let currentPos = 0;
            const scrollStep = totalHeight / 4;

            async function smoothScroll() {
                for (let i = 0; i < 4; i++) {
                    currentPos += scrollStep;
                    window.scrollTo(0, currentPos);
                    await new Promise(resolve => setTimeout(resolve, 800));
                }
            }
            smoothScroll();
        """)
        await asyncio.sleep(4)

        # Phase 2: "Double-check" some fields by clicking in them
        log_lines.append("[human] Double-checking form fields")

        check_selectors = [
            'input[type="email"]',
            'input[name*="name"]',
            'textarea',
            'input[type="tel"]'
        ]

        for selector in check_selectors:
            try:
                field = page.locator(selector).first
                if await field.is_visible(timeout=1000):
                    # Move mouse to field and click (like checking input)
                    await field.hover()
                    await asyncio.sleep(random.uniform(0.3, 0.8))
                    await field.click()
                    await asyncio.sleep(random.uniform(0.5, 1.2))
                    # Maybe make a small "correction"
                    if random.random() < 0.3:  # 30% chance to make small edit
                        await page.keyboard.press('End')
                        await asyncio.sleep(0.2)
                        await page.keyboard.press('Backspace')
                        await asyncio.sleep(0.3)
                        await page.keyboard.type('a')  # Type and delete a character
                        await asyncio.sleep(0.2)
                        await page.keyboard.press('Backspace')
                        log_lines.append(f"[human] Made small correction in field")
                    break
            except:
                continue

        # Phase 3: Scroll to submit button area
        submit_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("Submit")',
            'button:has-text("Send")',
            'button:has-text("Contact Us")'
        ]

        submit_button = None
        for selector in submit_selectors:
            try:
                button = page.locator(selector).first
                if await button.is_visible(timeout=1000):
                    submit_button = button
                    break
            except:
                continue

        if not submit_button:
            log_lines.append("[human] No submit button found")
            return False

        # Scroll submit button into view
        await submit_button.scroll_into_view_if_needed()
        await asyncio.sleep(random.uniform(1, 2))

        # Phase 4: Human-like submission hesitation sequence
        log_lines.append("[human] Implementing realistic submission hesitation")

        # Hover over submit button (like reading it)
        await submit_button.hover()
        await asyncio.sleep(random.uniform(2, 4))

        # Move mouse away (like hesitating)
        await page.mouse.move(
            random.randint(100, 300),
            random.randint(100, 300)
        )
        await asyncio.sleep(random.uniform(1, 3))

        # Hover again (like final decision)
        await submit_button.hover()
        await asyncio.sleep(random.uniform(1, 2))

        # Final hesitation before click
        await asyncio.sleep(random.uniform(1, 3))

        # Phase 5: Human-like click sequence
        log_lines.append("[human] Executing human-like submit click")

        # Some humans click and hold briefly
        await submit_button.click()

        return True

    async def ultra_human_run(self, dealer_name: str, url: str, payload: ContactPayload):
        """Complete form submission with ultra-realistic human behavior."""

        from datetime import datetime
        import re
        from playwright.async_api import async_playwright
        from src.automation.forms.form_submitter import SubmissionArtifacts, SubmissionStatus

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        slug = re.sub(r"[^a-z0-9]+", "_", dealer_name.lower()).strip("_") or "dealer"
        artifact_dir = self.screenshot_root / timestamp / slug

        artifacts = SubmissionArtifacts(base_dir=artifact_dir)
        artifacts.ensure_dirs()

        status = SubmissionStatus(dealer=dealer_name, url=url)
        log_lines = []

        async with async_playwright() as pw:
            # Use enhanced stealth configuration
            if self.cloudflare_stealth:
                browser, context, page = await self.cloudflare_stealth.create_stealth_session(
                    pw, headless=self.headless
                )
            else:
                browser, context = await self.browser_manager.open_context(pw, headless=self.headless)
                page = await self.browser_manager.create_enhanced_stealth_page(context)

            try:
                # Ultra-human navigation
                final_url = await self._ultra_human_navigation(page, url, log_lines)
                status.url = final_url

                # Handle cookie consent
                dismissed_consents = await self._handle_cookie_consent(page, log_lines)
                if dismissed_consents > 0:
                    log_lines.append(f"[human] Dismissed {dismissed_consents} cookie consent popup(s)")
                    await asyncio.sleep(random.uniform(1, 2))

                # Take screenshot of detected page
                detection_path = artifact_dir / "detected.png"
                await page.screenshot(path=str(detection_path), full_page=True)
                artifacts.detection = detection_path
                status.artifacts["detected"] = str(detection_path)

                # Enhanced form detection
                detection = await self.detector.detect_contact_form(page)

                if not detection.success:
                    status.status = "detection_failed"
                    status.errors.append("Form detection failed")
                    return status

                log_lines.append(f"[human] Form detected with {len(detection.fields)} fields")

                # Human-like form filling with longer delays
                log_lines.append("[human] Starting ultra-slow form filling with human patterns")

                # Use parent class populate_fields method
                for field in detection.fields:
                    if field.field_type in ["first_name", "last_name", "email", "phone", "zip", "message"]:
                        await self._fill_field(page, field, payload, log_lines)
                        # Extra long delays between fields (human thinking time)
                        await asyncio.sleep(random.uniform(3, 8))

                # Handle checkboxes
                checked_boxes = []
                if detection.checkboxes:
                    checked_boxes = await self._handle_checkboxes(page, detection, log_lines)

                # Handle dropdowns
                dropdown_choices = {}
                if detection.selects:
                    dropdown_choices = await self._handle_dropdowns(page, detection, log_lines)

                # Update status
                status.fields_filled = [f.field_type for f in detection.fields if f.field_type in ["first_name", "last_name", "email", "phone", "zip", "message"]]
                status.checkboxes_checked = checked_boxes
                status.dropdown_choices = dropdown_choices

                # Take screenshot after filling
                filled_path = artifact_dir / "filled.png"
                await page.screenshot(path=str(filled_path), full_page=True)
                artifacts.filled = filled_path
                status.artifacts["filled"] = str(filled_path)

                # Ultra-human form review and submission
                submission_success = await self._human_form_review_and_submit(page, log_lines)

                if not submission_success:
                    status.status = "submission_failed"
                    status.errors.append("Could not complete submission")
                    return status

                # Wait for response and check for confirmation
                await asyncio.sleep(random.uniform(3, 6))

                # Take final screenshot
                submitted_path = artifact_dir / "submitted.png"
                await page.screenshot(path=str(submitted_path), full_page=True)
                artifacts.submitted = submitted_path
                status.artifacts["submitted"] = str(submitted_path)

                # Check for confirmation or blocking
                page_content = await page.content()

                if "blocked" in page_content.lower() or "cloudflare" in page_content.lower():
                    status.status = "blocked"
                    status.errors.append("Submission blocked by security system")
                elif any(word in page_content.lower() for word in ["thank", "confirm", "success", "received"]):
                    status.status = "submission_success"
                    status.confirmation_text = "submission confirmed"
                    log_lines.append("[human] Submission appears successful!")
                else:
                    status.status = "submission_uncertain"
                    status.errors.append("Submission result unclear")

                return status

            except Exception as e:
                status.status = "error"
                status.errors.append(str(e))
                return status

            finally:
                # Save log
                log_path = artifact_dir / "run.log"
                log_path.write_text('\n'.join(log_lines), encoding="utf-8")
                artifacts.log = log_path
                status.artifacts["log"] = str(log_path)


async def test_ultra_human_submission():
    """Test ultra-human form submission."""

    print("🤖→👤 ULTRA-HUMAN FORM SUBMISSION TEST")
    print("🧠 Implementing advanced behavioral mimicry")
    print("=" * 60)

    test_payload = ContactPayload(
        first_name="Miguel",
        last_name="Montoya",
        email="migueljmontoya@protonmail.com",
        phone="555-123-4567",
        zip_code="90210",
        message="I am interested in learning more about your vehicle inventory and leasing options. Please contact me with available deals."
    )

    submitter = UltraHumanFormSubmitter(
        headless=False,
        use_cloudflare_stealth=True
    )

    print("🎯 Testing Capital City CDJR with ultra-human behavior...")
    print("👤 Simulating: natural navigation → form review → hesitation → submission")

    try:
        result = await submitter.ultra_human_run(
            dealer_name="Capital City CDJR (Ultra Human Test)",
            url="https://www.capcitycdjr.com/contact-us/",
            payload=test_payload
        )

        print(f"\n📊 ULTRA-HUMAN TEST RESULTS:")
        print(f"   🤖→👤 Status: {result.status}")
        print(f"   📝 Fields filled: {len(result.fields_filled)}")
        print(f"   ⚙️ Errors: {result.errors}")
        print(f"   📁 Artifacts: {list(result.artifacts.keys())}")

        if result.status == "submission_success":
            print("\n🎉 BREAKTHROUGH: Ultra-human simulation succeeded!")
        elif result.status == "blocked":
            print("\n🚧 Still blocked - need even more advanced evasion")
        else:
            print(f"\n🔍 Result: {result.status}")

        return result.status == "submission_success"

    except Exception as e:
        print(f"\n💥 Ultra-human test failed: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_ultra_human_submission())