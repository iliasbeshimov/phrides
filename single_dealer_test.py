#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

# Add project paths
ROOT = Path(__file__).resolve().parent
SRC_ROOT = ROOT / 'src'
for candidate in (ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.append(str(candidate))

from src.automation.forms.form_submitter import FormSubmissionRunner, ContactPayload

async def test_single_dealer():
    """Test form submission on a single dealer to verify system is working"""

    print("🧪 SINGLE DEALER VERIFICATION TEST")
    print("=" * 50)

    test_payload = ContactPayload(
        first_name="Miguel",
        last_name="Montoya",
        email="migueljmontoya@protonmail.com",
        phone="555-123-4567",
        zip_code="90210",
        message="I am interested in learning more about your vehicle inventory and leasing options. Please contact me with available deals."
    )

    runner = FormSubmissionRunner(
        headless=False,  # Keep visible to avoid headless issues
        use_cloudflare_stealth=True
    )

    try:
        print("🎯 Testing Capital City CDJR (known working)...")
        print("📧 Using real email for confirmation testing")

        result = await runner.run(
            dealer_name="Capital City CDJR (Cookie Consent Test)",
            url="https://www.capcitycdjr.com/contact-us/",
            payload=test_payload
        )

        print(f"\n📊 RESULTS:")
        print(f"   Status: {result.status}")
        print(f"   Fields filled: {len(result.fields_filled)}")
        for field in result.fields_filled:
            print(f"     - {field}")

        if result.missing_fields:
            print(f"   Missing fields: {len(result.missing_fields)}")
            for field in result.missing_fields:
                print(f"     - {field}")

        if result.dropdown_choices:
            print(f"   Dropdowns: {len(result.dropdown_choices)}")
            for dropdown, choice in result.dropdown_choices.items():
                print(f"     - {dropdown}: {choice}")

        if result.checkboxes_checked:
            print(f"   Checkboxes: {len(result.checkboxes_checked)}")
            for checkbox in result.checkboxes_checked:
                print(f"     - {checkbox}")

        if result.confirmation_text:
            print(f"   🎉 Confirmation: {result.confirmation_text}")

        if result.errors:
            print(f"   ⚠️ Errors:")
            for error in result.errors:
                print(f"     - {error}")

        print(f"\n📁 Artifacts saved to: {result.artifacts}")

        return result.status == "submission_success"

    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_single_dealer())