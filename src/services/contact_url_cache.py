"""
Contact URL cache to remember successfully found contact pages.
Prevents re-discovery on future visits to same dealership.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
from dataclasses import dataclass, asdict

from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ContactPageEntry:
    """Cached contact page information"""
    website: str
    contact_url: str
    has_form: bool
    field_count: int
    field_types: list
    discovered_date: str
    last_verified: str
    success_count: int  # How many times successfully used
    form_type: Optional[str] = None  # e.g., "gravity_forms", "dealer.com", "standard"


class ContactURLCache:
    """Cache for successfully discovered contact page URLs"""

    def __init__(self, cache_file: str = "data/contact_url_cache.json"):
        self.cache_file = Path(cache_file)
        self.logger = logger
        self._ensure_cache_file()

    def _ensure_cache_file(self):
        """Create cache file if it doesn't exist"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.cache_file.exists():
            self._save_data({"entries": [], "stats": {"total": 0}})

    def _load_data(self) -> Dict:
        """Load cache data from file"""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load contact URL cache: {str(e)}")
            return {"entries": [], "stats": {"total": 0}}

    def _save_data(self, data: Dict):
        """Save cache data to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save contact URL cache: {str(e)}")

    def get_contact_url(self, website: str) -> Optional[ContactPageEntry]:
        """
        Get cached contact URL for a website.

        Args:
            website: Base website URL (e.g., "https://example.com")

        Returns:
            ContactPageEntry if found in cache, None otherwise
        """
        # Normalize website URL
        website = website.rstrip('/')

        data = self._load_data()

        for entry_dict in data["entries"]:
            if entry_dict["website"] == website:
                self.logger.info(f"Found cached contact URL for {website}: {entry_dict['contact_url']}")
                return ContactPageEntry(**entry_dict)

        return None

    def add_contact_url(self, website: str, contact_url: str, has_form: bool = True,
                       field_count: int = 0, field_types: list = None,
                       form_type: Optional[str] = None):
        """
        Add or update contact URL in cache.

        Args:
            website: Base website URL
            contact_url: Contact page URL
            has_form: Whether page has a contact form
            field_count: Number of fields detected
            field_types: List of field type names
            form_type: Type of form (e.g., "gravity_forms", "dealer.com")
        """
        # Normalize URLs
        website = website.rstrip('/')

        if field_types is None:
            field_types = []

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data = self._load_data()

        # Check if entry already exists
        existing_idx = None
        for idx, entry in enumerate(data["entries"]):
            if entry["website"] == website:
                existing_idx = idx
                break

        if existing_idx is not None:
            # Update existing entry
            entry = data["entries"][existing_idx]
            entry["contact_url"] = contact_url
            entry["has_form"] = has_form
            entry["field_count"] = field_count
            entry["field_types"] = field_types
            entry["last_verified"] = now
            entry["success_count"] = entry.get("success_count", 0) + 1
            if form_type:
                entry["form_type"] = form_type

            self.logger.info(f"Updated cached contact URL for {website}")
        else:
            # Add new entry
            entry = ContactPageEntry(
                website=website,
                contact_url=contact_url,
                has_form=has_form,
                field_count=field_count,
                field_types=field_types,
                discovered_date=now,
                last_verified=now,
                success_count=1,
                form_type=form_type
            )
            data["entries"].append(asdict(entry))
            data["stats"]["total"] += 1

            self.logger.info(f"Added new contact URL to cache: {website} -> {contact_url}")

        self._save_data(data)

    def increment_success_count(self, website: str):
        """Increment success count when cached URL is successfully used"""
        website = website.rstrip('/')

        data = self._load_data()

        for entry in data["entries"]:
            if entry["website"] == website:
                entry["success_count"] = entry.get("success_count", 0) + 1
                entry["last_verified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_data(data)
                self.logger.debug(f"Incremented success count for {website}")
                return

    def remove_entry(self, website: str):
        """Remove entry from cache (if URL no longer works)"""
        website = website.rstrip('/')

        data = self._load_data()

        original_count = len(data["entries"])
        data["entries"] = [e for e in data["entries"] if e["website"] != website]

        if len(data["entries"]) < original_count:
            data["stats"]["total"] = len(data["entries"])
            self._save_data(data)
            self.logger.info(f"Removed cache entry for {website}")
            return True

        return False

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        data = self._load_data()

        stats = {
            "total_cached": len(data["entries"]),
            "with_forms": sum(1 for e in data["entries"] if e["has_form"]),
            "without_forms": sum(1 for e in data["entries"] if not e["has_form"]),
            "by_form_type": {}
        }

        # Count by form type
        for entry in data["entries"]:
            form_type = entry.get("form_type", "unknown")
            stats["by_form_type"][form_type] = stats["by_form_type"].get(form_type, 0) + 1

        return stats

    def export_to_csv(self, output_file: str = "data/contact_url_cache.csv"):
        """Export cache to CSV for manual review"""
        import csv

        data = self._load_data()

        if not data["entries"]:
            self.logger.info("No cached entries to export")
            return

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'website', 'contact_url', 'has_form', 'field_count', 'field_types',
                'form_type', 'discovered_date', 'last_verified', 'success_count'
            ])
            writer.writeheader()

            for entry in data["entries"]:
                writer.writerow({
                    **entry,
                    'field_types': ', '.join(entry.get('field_types', []))
                })

        self.logger.info(f"Exported {len(data['entries'])} entries to {output_path}")
        return str(output_path)

    def print_summary(self):
        """Print cache summary to console"""
        stats = self.get_stats()

        print("\n" + "="*80)
        print("CONTACT URL CACHE - SUMMARY")
        print("="*80)
        print(f"\nTotal Cached Sites: {stats['total_cached']}")
        print(f"  - With Forms: {stats['with_forms']}")
        print(f"  - Without Forms: {stats['without_forms']}")

        if stats['by_form_type']:
            print("\nBy Form Type:")
            for form_type, count in stats['by_form_type'].items():
                print(f"  - {form_type}: {count}")

        print("\n" + "="*80 + "\n")
