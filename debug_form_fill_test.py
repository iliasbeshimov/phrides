#!/usr/bin/env python3
"""
Debug test for form filling on a known working site to verify the improvements.
"""

import asyncio
import sys
from pathlib import Path

# Add project paths
ROOT = Path(__file__).resolve().parent
SRC_ROOT = ROOT / 'src'
for candidate in (ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.append(str(candidate))

from src.automation.forms.form_submitter import FormSubmissionRunner, ContactPayload, DEFAULT_PLACEHOLDER


async def debug_form_fill():
    """Debug form filling on Capital City CDJR."""
    print("🔧 DEBUG FORM FILL TEST - Capital City CDJR")
    print("🎯 Testing improved anti-detection measures")
    print("=" * 60)

    test_payload = ContactPayload(
        first_name="Miguel",
        last_name="Montoya",
        email="migueljmontoya@protonmail.com",
        phone="6503320719",
        zip_code="90066",
        message="Hi, I am interested in leasing a new SUV. Who do I need to talk to for what options are available. Best, Miguel"
    )

    runner = FormSubmissionRunner(
        headless=False,  # Keep browser open for observation
        use_cloudflare_stealth=True
    )

    try:
        print(f"\n🚀 Testing on Capital City CDJR...")
        print(f"📝 Form filling with: {test_payload.first_name} {test_payload.last_name}")
        print(f"📧 Email: {test_payload.email}")

        result = await runner.run(
            dealer_name="Capital City CDJR (Debug Test)",
            url="https://www.capcitycdjr.com/contact-us/",
            payload=test_payload
        )

        print(f"\n📊 RESULTS:")
        print(f"   🎯 Status: {result.status}")
        print(f"   ✅ Fields filled: {len(result.fields_filled)}")
        if result.fields_filled:
            for field in result.fields_filled:
                print(f"      - {field}")

        print(f"   ❌ Missing fields: {len(result.missing_fields)}")
        if result.missing_fields:
            for field in result.missing_fields:
                print(f"      - {field}")

        print(f"   🔽 Dropdowns: {len(result.dropdown_choices)}")
        if result.dropdown_choices:
            for dropdown, choice in result.dropdown_choices.items():
                print(f"      - {dropdown}: {choice}")

        print(f"   ☑️  Checkboxes: {len(result.checkboxes_checked)}")
        if result.checkboxes_checked:
            for checkbox in result.checkboxes_checked:
                print(f"      - {checkbox[:50]}...")

        if result.confirmation_text:
            print(f"   🎉 Confirmation: {result.confirmation_text}")

        if result.errors:
            print(f"   ⚠️  Errors:")
            for error in result.errors:
                print(f"      - {error}")

        print(f"\n📁 Artifacts:")
        for artifact_type, path in result.artifacts.items():
            print(f"   📸 {artifact_type}: {path}")

        return result.status in ["submission_success"]

    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        return False


async def main():
    print("🔧 STARTING DEBUG FORM FILL TEST...")
    print("🎯 Testing enhanced anti-detection measures on known working site")
    print("👀 Browser will stay open for manual verification\n")

    try:
        success = await debug_form_fill()
        if success:
            print("\n🎉 Form fill test SUCCEEDED!")
        else:
            print("\n⚠️ Form fill test had issues - check logs and screenshots")

    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as exc:
        print(f"\n💥 Test failed: {exc}")


if __name__ == "__main__":
    asyncio.run(main())