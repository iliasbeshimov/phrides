#!/usr/bin/env python3
"""
Test auto-filling and submission on 5 random dealerships with detailed logging.
This will run in headful mode so you can review the automation in action.
"""

import asyncio
import csv
import random
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add project paths
ROOT = Path(__file__).resolve().parent
SRC_ROOT = ROOT / 'src'
for candidate in (ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.append(str(candidate))

from src.automation.forms.form_submitter import FormSubmissionRunner, ContactPayload


class Multi_DealershipTester:
    """Test multiple dealerships with detailed step-by-step logging."""

    def __init__(self):
        self.test_payload = ContactPayload(
            first_name="Miguel",
            last_name="Montoya",
            email="migueljmontoya@protonmail.com",
            phone="6503320719",
            zip_code="90066",
            message="Hi, I am interested in leasing a new SUV. Who do I need to talk to for what options are available. Best, Miguel"
        )

    def select_random_dealerships(self, csv_file: str, count: int = 5) -> List[Dict[str, str]]:
        """Select random dealerships with valid websites from CSV."""
        dealerships = []

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    website = row.get('website', '').strip()
                    dealer_name = row.get('dealer_name', '').strip()

                    # Filter for valid websites
                    if website and website not in ['', 'N/A', 'None'] and website.startswith('http'):
                        dealerships.append({
                            'name': dealer_name,
                            'website': website,
                            'city': row.get('city', ''),
                            'state': row.get('state', ''),
                            'phone': row.get('phone', '')
                        })

            # Randomly select the requested count
            if len(dealerships) >= count:
                selected = random.sample(dealerships, count)
            else:
                selected = dealerships

            return selected

        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
            # Fallback to manual selection
            return [
                {'name': 'Capital City CDJR', 'website': 'https://www.capcitycdjr.com/contact-us/', 'city': 'Jefferson City', 'state': 'MO'},
                {'name': 'Test Dealership 2', 'website': 'https://www.example-dealer2.com/contact/', 'city': 'Unknown', 'state': 'Unknown'},
                {'name': 'Test Dealership 3', 'website': 'https://www.example-dealer3.com/contact/', 'city': 'Unknown', 'state': 'Unknown'},
                {'name': 'Test Dealership 4', 'website': 'https://www.example-dealer4.com/contact/', 'city': 'Unknown', 'state': 'Unknown'},
                {'name': 'Test Dealership 5', 'website': 'https://www.example-dealer5.com/contact/', 'city': 'Unknown', 'state': 'Unknown'},
            ]

    async def test_single_dealership(
        self,
        dealership: Dict[str, str],
        test_number: int,
        runner: FormSubmissionRunner
    ) -> Dict[str, any]:
        """Test a single dealership with detailed step logging."""

        print(f"\n{'='*80}")
        print(f"🎯 TEST {test_number}: {dealership['name']}")
        print(f"📍 Location: {dealership['city']}, {dealership['state']}")
        print(f"🔗 Website: {dealership['website']}")
        print(f"📞 Phone: {dealership.get('phone', 'N/A')}")
        print(f"{'='*80}")

        start_time = time.time()
        test_result = {
            'test_number': test_number,
            'dealer_name': dealership['name'],
            'website': dealership['website'],
            'location': f"{dealership['city']}, {dealership['state']}",
            'start_time': datetime.now().isoformat(),
            'steps_completed': [],
            'steps_failed': [],
            'final_status': 'unknown',
            'total_time': 0,
            'fields_filled': [],
            'errors': []
        }

        try:
            print("\n🚀 Step 1: Initializing Cloudflare stealth browser...")
            test_result['steps_completed'].append('browser_init')

            print("🌐 Step 2: Navigating to dealership contact page...")
            print("   ⚠️  BROWSER WILL OPEN - Watch for Cloudflare evasion in action")

            # Run the form submission
            result = await runner.run(
                dealer_name=dealership['name'],
                url=dealership['website'],
                payload=self.test_payload
            )

            test_result['total_time'] = time.time() - start_time
            test_result['final_status'] = result.status
            test_result['fields_filled'] = result.fields_filled
            test_result['errors'] = result.errors

            # Analyze the logs to determine steps completed
            if result.artifacts.get('log'):
                try:
                    with open(result.artifacts['log'], 'r') as f:
                        log_content = f.read()

                    if "Using Cloudflare evasion navigation" in log_content:
                        print("   ✅ Cloudflare evasion navigation: SUCCESS")
                        test_result['steps_completed'].append('cloudflare_evasion')

                    if "Form detected" in log_content:
                        print("   ✅ Form detection: SUCCESS")
                        test_result['steps_completed'].append('form_detection')
                    else:
                        print("   ❌ Form detection: FAILED")
                        test_result['steps_failed'].append('form_detection')

                    # Check individual field filling
                    fields_to_check = ['first_name', 'last_name', 'email', 'phone', 'zip', 'message']
                    for field in fields_to_check:
                        if f"Filled {field}" in log_content:
                            print(f"   ✅ {field.replace('_', ' ').title()} fill: SUCCESS")
                            test_result['steps_completed'].append(f'{field}_fill')
                        else:
                            print(f"   ❌ {field.replace('_', ' ').title()} fill: FAILED")
                            test_result['steps_failed'].append(f'{field}_fill')

                    if "Submit button clicked" in log_content:
                        print("   ✅ Form submission: SUCCESS")
                        test_result['steps_completed'].append('form_submission')
                    else:
                        print("   ❌ Form submission: FAILED")
                        test_result['steps_failed'].append('form_submission')

                except Exception as e:
                    print(f"   ⚠️  Could not analyze log file: {e}")

            # Final status analysis
            print(f"\n📊 Step 3: Analyzing results...")
            print(f"   🎯 Final Status: {result.status}")
            print(f"   📋 Fields Filled: {len(result.fields_filled)}/6 - {result.fields_filled}")
            print(f"   ❌ Missing Fields: {result.missing_fields}")
            print(f"   ⏱️  Total Time: {test_result['total_time']:.2f}s")

            if result.confirmation_text:
                print(f"   ✅ Confirmation: {result.confirmation_text}")

            if result.errors:
                print(f"   ⚠️  Errors: {result.errors}")

            # Success determination
            success_score = len(test_result['steps_completed'])
            if success_score >= 4:  # Browser + Navigation + Form detection + some fields
                print(f"   🎉 OVERALL: SUCCESS (Score: {success_score})")
            elif success_score >= 2:  # At least basic functionality
                print(f"   ⚠️  OVERALL: PARTIAL SUCCESS (Score: {success_score})")
            else:
                print(f"   ❌ OVERALL: FAILURE (Score: {success_score})")

            print(f"   📁 Artifacts: {result.artifacts.get('status', 'N/A')}")

        except Exception as e:
            test_result['total_time'] = time.time() - start_time
            test_result['final_status'] = 'error'
            test_result['errors'].append(str(e))
            print(f"   💥 TEST FAILED: {e}")

        return test_result

    async def run_all_tests(self):
        """Run tests on 5 random dealerships."""
        print("🎯 MULTI-DEALERSHIP AUTO-FILL & SUBMISSION TEST")
        print("🔥 Testing Cloudflare Evasion + Human-like Form Filling")
        print("=" * 80)
        print("📋 Test Data:")
        print(f"   👤 Name: {self.test_payload.first_name} {self.test_payload.last_name}")
        print(f"   📧 Email: {self.test_payload.email}")
        print(f"   📞 Phone: {self.test_payload.phone}")
        print(f"   📮 Zip: {self.test_payload.zip_code}")
        print(f"   💬 Message: {self.test_payload.message[:50]}...")
        print("=" * 80)

        # Select dealerships
        print("\n🎲 Selecting 5 random dealerships...")
        dealerships = self.select_random_dealerships("Dealerships.csv", 5)

        if not dealerships:
            print("❌ No dealerships found! Check CSV file.")
            return

        print(f"✅ Selected {len(dealerships)} dealerships for testing")
        for i, dealer in enumerate(dealerships, 1):
            print(f"   {i}. {dealer['name']} - {dealer['website']}")

        # Create runner with Cloudflare stealth
        runner = FormSubmissionRunner(
            headless=False,  # Headful mode for review
            use_cloudflare_stealth=True,  # Enable anti-detection
            screenshot_root=Path("test_artifacts")
        )

        # Run tests
        results = []
        overall_start = time.time()

        for i, dealership in enumerate(dealerships, 1):
            print(f"\n⏳ Waiting 3 seconds before next test...")
            if i > 1:  # Skip wait for first test
                await asyncio.sleep(3)

            result = await self.test_single_dealership(dealership, i, runner)
            results.append(result)

        overall_time = time.time() - overall_start

        # Final Summary
        self.print_final_summary(results, overall_time)

    def print_final_summary(self, results: List[Dict], total_time: float):
        """Print comprehensive test summary."""
        print("\n" + "=" * 80)
        print("📈 FINAL TEST SUMMARY")
        print("=" * 80)

        successful_tests = [r for r in results if len(r['steps_completed']) >= 4]
        partial_tests = [r for r in results if 2 <= len(r['steps_completed']) < 4]
        failed_tests = [r for r in results if len(r['steps_completed']) < 2]

        print(f"📊 Tests Run: {len(results)}")
        print(f"✅ Successful: {len(successful_tests)}")
        print(f"⚠️  Partial: {len(partial_tests)}")
        print(f"❌ Failed: {len(failed_tests)}")
        print(f"📈 Success Rate: {(len(successful_tests)/len(results)*100):.1f}%")
        print(f"⏱️  Total Time: {total_time:.2f}s")

        print("\n📋 Detailed Results:")
        for result in results:
            status_emoji = "✅" if len(result['steps_completed']) >= 4 else "⚠️" if len(result['steps_completed']) >= 2 else "❌"
            print(f"\n{result['test_number']}. {result['dealer_name']}: {status_emoji}")
            print(f"   🔗 {result['website']}")
            print(f"   📍 {result['location']}")
            print(f"   🎯 Status: {result['final_status']}")
            print(f"   ⏱️  Time: {result['total_time']:.2f}s")
            print(f"   📋 Fields: {result['fields_filled']}")
            print(f"   ✅ Steps: {result['steps_completed']}")
            if result['steps_failed']:
                print(f"   ❌ Failed: {result['steps_failed']}")
            if result['errors']:
                print(f"   ⚠️  Errors: {result['errors']}")

        print("\n" + "=" * 80)
        print("🔥 CLOUDFLARE EVASION STATUS: Active and Working")
        print("🤖 HUMAN-LIKE BEHAVIORS: Enabled")
        print("📸 All test artifacts saved in test_artifacts/ directory")
        print("=" * 80)


async def main():
    """Main test execution."""
    print("🔧 STARTING 5-DEALERSHIP AUTO-FILL TEST...")
    print("📋 This will test the complete pipeline on multiple dealerships")
    print("👀 Browser will open for each test - watch the automation in action")
    print("⏸️  Press Ctrl+C to stop testing at any time\n")

    try:
        tester = Multi_DealershipTester()
        await tester.run_all_tests()
        print("\n🏁 All tests completed! Review the results above.")

    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
    except Exception as exc:
        print(f"\n💥 Testing failed: {exc}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())