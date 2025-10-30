#!/usr/bin/env python3
"""
Test real form submissions on 5 random dealerships with Chrome Canary-like profile.
This test uses your real email (migueljmontoya@protonmail.com) to verify actual submissions.
"""

import asyncio
import csv
import random
import sys
from pathlib import Path
from datetime import datetime

# Add project paths
ROOT = Path(__file__).resolve().parent
SRC_ROOT = ROOT / 'src'
for candidate in (ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.append(str(candidate))

from src.automation.forms.form_submitter import FormSubmissionRunner, ContactPayload


def get_random_dealerships(count: int = 5, seed: int = None) -> list:
    """Get random dealerships from CSV."""
    if seed:
        random.seed(seed)

    dealerships = []
    try:
        with open('Dealerships.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            valid_dealers = []

            for row in reader:
                website = row.get('website', '').strip()
                dealer_name = row.get('dealer_name', '').strip()

                if (website and website not in ['', 'N/A', 'None'] and
                    website.startswith('http') and dealer_name):
                    valid_dealers.append({
                        'name': dealer_name,
                        'website': website,
                        'city': row.get('city', ''),
                        'state': row.get('state', ''),
                        'phone': row.get('phone', '')
                    })

            return random.sample(valid_dealers, min(count, len(valid_dealers)))

    except Exception as e:
        print(f"Error reading dealerships: {e}")
        # Fallback to known working sites
        return [
            {
                'name': 'Capital City CDJR',
                'website': 'https://www.capcitycdjr.com/contact-us/',
                'city': 'Jefferson City',
                'state': 'MO',
                'phone': '573-635-6137'
            }
        ]


async def test_real_submissions():
    """Test real form submissions on random dealerships."""
    print("🔥 REAL FORM SUBMISSION TEST")
    print("📧 Using REAL email: migueljmontoya@protonmail.com")
    print("🎯 Check your email for confirmation messages!")
    print("=" * 70)

    # Get 5 random dealerships
    dealerships = get_random_dealerships(5, seed=951)

    # Real test data - using your actual email for real confirmations
    test_payload = ContactPayload(
        first_name="Miguel",
        last_name="Montoya",
        email="migueljmontoya@protonmail.com",  # REAL EMAIL
        phone="6503320719",
        zip_code="90066",
        message="Hi, I am interested in leasing a new SUV. Who do I need to talk to for what options are available. Best, Miguel"
    )

    print(f"📋 Test Data:")
    print(f"   👤 Name: {test_payload.first_name} {test_payload.last_name}")
    print(f"   📧 Email: {test_payload.email}")
    print(f"   📞 Phone: {test_payload.phone}")
    print(f"   📮 Zip: {test_payload.zip_code}")
    print(f"   💬 Message: {test_payload.message[:50]}...")
    print()

    # Use enhanced stealth without conflicting profile
    runner = FormSubmissionRunner(
        headless=False,  # Keep visible for monitoring
        use_cloudflare_stealth=True
    )

    results = []

    for i, dealer in enumerate(dealerships, 1):
        print(f"🎯 TEST {i}/5: {dealer['name']}")
        print(f"   🌐 URL: {dealer['website']}")
        print(f"   📍 Location: {dealer['city']}, {dealer['state']}")
        print("   ⚠️ Using REAL email - expect confirmation if successful!")

        try:
            result = await runner.run(
                dealer_name=dealer['name'],
                url=dealer['website'],
                payload=test_payload
            )

            print(f"   📊 Status: {result.status}")
            print(f"   ✅ Fields filled: {len(result.fields_filled)}")
            if result.fields_filled:
                print(f"      {', '.join(result.fields_filled)}")

            print(f"   ☑️ Checkboxes: {len(result.checkboxes_checked)}")
            print(f"   🔽 Dropdowns: {len(result.dropdown_choices)}")

            if result.confirmation_text:
                print(f"   🎉 Confirmation: {result.confirmation_text}")

            if result.errors:
                print(f"   ❌ Errors: {len(result.errors)}")
                for error in result.errors[:2]:  # Show first 2 errors
                    print(f"      - {error}")

            results.append({
                'dealer': dealer['name'],
                'url': dealer['website'],
                'status': result.status,
                'fields_filled': len(result.fields_filled),
                'confirmation': bool(result.confirmation_text),
                'errors': len(result.errors)
            })

        except Exception as e:
            print(f"   💥 Failed: {e}")
            results.append({
                'dealer': dealer['name'],
                'url': dealer['website'],
                'status': 'error',
                'fields_filled': 0,
                'confirmation': False,
                'errors': 1
            })

        print(f"   ⏱️ Waiting 10 seconds before next test...")
        print()

        # Pause between tests to avoid rate limiting
        if i < len(dealerships):
            await asyncio.sleep(10)

    print("🏆 FINAL RESULTS SUMMARY:")
    print("=" * 70)

    successful = sum(1 for r in results if r['status'] == 'submission_success')
    with_fields = sum(1 for r in results if r['fields_filled'] > 0)
    with_confirmation = sum(1 for r in results if r['confirmation'])

    print(f"📊 Tests completed: {len(results)}")
    print(f"✅ Submission success: {successful}/{len(results)}")
    print(f"📝 Forms filled: {with_fields}/{len(results)}")
    print(f"🎉 Confirmations: {with_confirmation}/{len(results)}")

    print(f"\n📧 EMAIL CHECK:")
    print(f"   📬 Check migueljmontoya@protonmail.com for confirmation emails")
    print(f"   ⏰ Emails may take 1-15 minutes to arrive")
    print(f"   🔍 Check spam folder if not in inbox")

    if with_confirmation > 0:
        print(f"   🎉 {with_confirmation} confirmations detected - emails should arrive!")
    else:
        print(f"   ⚠️ No confirmations detected - check if forms actually submitted")

    print("\n📋 Detailed Results:")
    for r in results:
        status_icon = "✅" if r['status'] == 'submission_success' else "❌"
        print(f"   {status_icon} {r['dealer']}: {r['status']} "
              f"({r['fields_filled']} fields, {'✓' if r['confirmation'] else '✗'} confirmation)")

    return results


async def main():
    """Main execution."""
    print("🔧 STARTING REAL SUBMISSION TESTS...")
    print("🚨 WARNING: Using real email address for actual submissions!")
    print("📧 You should receive confirmation emails if forms submit successfully")
    print("👀 Browser will stay open for visual verification\n")

    try:
        results = await test_real_submissions()

        successful = sum(1 for r in results if r['status'] == 'submission_success')
        if successful > 0:
            print(f"\n🎉 {successful} successful submissions - check your email!")
        else:
            print(f"\n⚠️ No successful submissions detected")

    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as exc:
        print(f"\n💥 Test failed: {exc}")


if __name__ == "__main__":
    asyncio.run(main())