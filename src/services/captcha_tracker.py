"""
CAPTCHA and manual follow-up tracker.
Tracks sites that require manual intervention due to CAPTCHA or other blockers.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ManualFollowupEntry:
    """Entry for a site requiring manual follow-up"""
    dealer_name: str
    website: str
    contact_url: str
    reason: str  # CAPTCHA, validation_error, etc.
    detected_date: str
    status: str  # pending, completed, skipped
    notes: Optional[str] = None
    captcha_type: Optional[str] = None  # recaptcha_v2, recaptcha_v3, hcaptcha, etc.


class CaptchaTracker:
    """Tracks sites with CAPTCHA and other blockers requiring manual follow-up"""

    def __init__(self, data_file: str = "data/captcha_sites.json"):
        self.data_file = Path(data_file)
        self.logger = logger
        self._ensure_data_file()

    def _ensure_data_file(self):
        """Create data file if it doesn't exist"""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.data_file.exists():
            self._save_data({"sites": [], "summary": {"total": 0, "pending": 0, "completed": 0}})

    def _load_data(self) -> Dict:
        """Load tracking data from file"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load CAPTCHA tracking data: {str(e)}")
            return {"sites": [], "summary": {"total": 0, "pending": 0, "completed": 0}}

    def _save_data(self, data: Dict):
        """Save tracking data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save CAPTCHA tracking data: {str(e)}")

    def add_site(self, dealer_name: str, website: str, contact_url: str,
                 reason: str, captcha_type: Optional[str] = None,
                 notes: Optional[str] = None):
        """Add a site requiring manual follow-up"""

        entry = ManualFollowupEntry(
            dealer_name=dealer_name,
            website=website,
            contact_url=contact_url,
            reason=reason,
            detected_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status="pending",
            notes=notes,
            captcha_type=captcha_type
        )

        data = self._load_data()

        # Check if site already exists
        existing_idx = None
        for idx, site in enumerate(data["sites"]):
            if site["website"] == website:
                existing_idx = idx
                break

        if existing_idx is not None:
            # Update existing entry
            data["sites"][existing_idx] = asdict(entry)
            self.logger.info(f"Updated existing CAPTCHA site: {dealer_name}")
        else:
            # Add new entry
            data["sites"].append(asdict(entry))
            data["summary"]["total"] += 1
            data["summary"]["pending"] += 1
            self.logger.info(f"Added CAPTCHA site: {dealer_name} ({reason})")

        self._save_data(data)

    def mark_completed(self, website: str, notes: Optional[str] = None):
        """Mark a site as manually completed"""

        data = self._load_data()

        for site in data["sites"]:
            if site["website"] == website and site["status"] == "pending":
                site["status"] = "completed"
                if notes:
                    site["notes"] = notes

                data["summary"]["pending"] -= 1
                data["summary"]["completed"] += 1

                self._save_data(data)
                self.logger.info(f"Marked site as completed: {website}")
                return True

        return False

    def mark_skipped(self, website: str, notes: Optional[str] = None):
        """Mark a site as skipped (won't follow up)"""

        data = self._load_data()

        for site in data["sites"]:
            if site["website"] == website and site["status"] == "pending":
                site["status"] = "skipped"
                if notes:
                    site["notes"] = notes

                data["summary"]["pending"] -= 1

                self._save_data(data)
                self.logger.info(f"Marked site as skipped: {website}")
                return True

        return False

    def get_pending_sites(self) -> List[Dict]:
        """Get all sites pending manual follow-up"""

        data = self._load_data()
        return [site for site in data["sites"] if site["status"] == "pending"]

    def get_sites_by_reason(self, reason: str) -> List[Dict]:
        """Get sites filtered by reason"""

        data = self._load_data()
        return [site for site in data["sites"] if site["reason"] == reason]

    def get_captcha_sites(self) -> List[Dict]:
        """Get all sites with CAPTCHA"""

        data = self._load_data()
        return [site for site in data["sites"] if "CAPTCHA" in site["reason"].upper()]

    def get_summary(self) -> Dict:
        """Get summary statistics"""

        data = self._load_data()

        # Count by reason
        reason_counts = {}
        for site in data["sites"]:
            reason = site["reason"]
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

        # Count by captcha type
        captcha_type_counts = {}
        for site in data["sites"]:
            captcha_type = site.get("captcha_type")
            if captcha_type:
                captcha_type_counts[captcha_type] = captcha_type_counts.get(captcha_type, 0) + 1

        return {
            "total_sites": data["summary"]["total"],
            "pending": data["summary"]["pending"],
            "completed": data["summary"]["completed"],
            "skipped": data["summary"]["total"] - data["summary"]["pending"] - data["summary"]["completed"],
            "by_reason": reason_counts,
            "by_captcha_type": captcha_type_counts
        }

    def export_pending_csv(self, output_file: str = "data/pending_manual_followup.csv"):
        """Export pending sites to CSV for manual processing"""

        import csv

        pending = self.get_pending_sites()

        if not pending:
            self.logger.info("No pending sites to export")
            return

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'dealer_name', 'website', 'contact_url', 'reason',
                'captcha_type', 'detected_date', 'notes'
            ])
            writer.writeheader()

            for site in pending:
                writer.writerow({
                    'dealer_name': site['dealer_name'],
                    'website': site['website'],
                    'contact_url': site['contact_url'],
                    'reason': site['reason'],
                    'captcha_type': site.get('captcha_type', ''),
                    'detected_date': site['detected_date'],
                    'notes': site.get('notes', '')
                })

        self.logger.info(f"Exported {len(pending)} pending sites to {output_path}")
        return str(output_path)

    def print_summary(self):
        """Print summary to console"""

        summary = self.get_summary()

        print("\n" + "="*80)
        print("CAPTCHA & MANUAL FOLLOW-UP TRACKER - SUMMARY")
        print("="*80)
        print(f"\nTotal Sites Requiring Manual Follow-up: {summary['total_sites']}")
        print(f"  - Pending: {summary['pending']}")
        print(f"  - Completed: {summary['completed']}")
        print(f"  - Skipped: {summary['skipped']}")

        print("\nBreakdown by Reason:")
        for reason, count in summary['by_reason'].items():
            print(f"  - {reason}: {count}")

        if summary['by_captcha_type']:
            print("\nCAPTCHA Types:")
            for captcha_type, count in summary['by_captcha_type'].items():
                print(f"  - {captcha_type}: {count}")

        pending = self.get_pending_sites()
        if pending:
            print(f"\nPending Sites ({len(pending)}):")
            for site in pending[:10]:  # Show first 10
                print(f"  - {site['dealer_name']} ({site['reason']})")
                print(f"    URL: {site['contact_url']}")

            if len(pending) > 10:
                print(f"  ... and {len(pending) - 10} more")

        print("\n" + "="*80 + "\n")
