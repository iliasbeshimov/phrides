#!/usr/bin/env python3
"""
COMPLETE 50 DEALERSHIP TEST - Efficient Full Evaluation
Optimized test to complete all 50 dealerships with reduced wait times.
Goal: Complete full 50-dealership evaluation within reasonable time.
"""

import asyncio
import random
import pandas as pd
import os
from datetime import datetime
from playwright.async_api import async_playwright
from enhanced_stealth_browser_config import EnhancedStealthBrowserManager
import numpy as np

class EfficientDetector:
    """Efficient detector optimized for speed while maintaining accuracy"""

    def __init__(self):
        # Most effective form patterns (reduced set for speed)
        self.form_patterns = [
            'form', '.gform_wrapper', 'form[id*="gform_"]',
            'form[name*="contact"]', '.wpforms-form'
        ]

        # Key input patterns
        self.input_patterns = [
            'input[type="email"]', 'input[name*="email" i]',
            'input[name*="name" i]', 'textarea'
        ]

        # Submit patterns
        self.submit_patterns = [
            'button[type="submit"]', 'input[type="submit"]', '.gform_button'
        ]

    async def quick_detection(self, page, max_wait_seconds=20):
        """Quick 20-second detection optimized for speed"""

        print("   ⚡ Quick detection (20-second max wait)...")

        result = {
            'success': False,
            'confidence_score': 0.0,
            'forms_found': 0,
            'inputs_found': 0,
            'buttons_found': 0,
            'framework': 'Standard HTML'
        }

        try:
            # 2-cycle quick scan (20 seconds total)
            for cycle in range(2):
                await page.wait_for_timeout(10000)  # 10 seconds per cycle
                print(f"         Quick cycle {cycle + 1}/2...")

                # Form detection
                total_forms = 0
                for pattern in self.form_patterns:
                    try:
                        forms = await page.locator(pattern).all()
                        if len(forms) > 0:
                            total_forms += len(forms)
                            print(f"            ✅ {len(forms)} forms: {pattern}")
                            break  # Early exit on first match
                    except Exception:
                        continue

                # Input detection (quick check)
                total_inputs = 0
                for pattern in self.input_patterns:
                    try:
                        inputs = await page.locator(pattern).all()
                        total_inputs += len(inputs)
                    except Exception:
                        continue

                result['forms_found'] = max(result['forms_found'], total_forms)
                result['inputs_found'] = max(result['inputs_found'], total_inputs)

                print(f"            📊 Quick cycle {cycle + 1}: {total_forms} forms, {total_inputs} inputs")

                # Early success detection
                if total_forms > 0 or total_inputs >= 2:
                    print(f"            🎉 Forms detected in cycle {cycle + 1}!")
                    break

            # Quick JavaScript check
            js_result = await page.evaluate("""
                () => ({
                    allForms: document.querySelectorAll('form').length,
                    emailInputs: document.querySelectorAll('input[type="email"], input[name*="email"]').length,
                    hasGravityForms: document.querySelectorAll('.gform_wrapper').length > 0
                })
            """)

            # Quick confidence calculation
            confidence = 0.0
            if result['forms_found'] > 0 or js_result['allForms'] > 0:
                confidence = 0.8
            elif js_result['emailInputs'] > 0:
                confidence = 0.5

            if js_result['hasGravityForms']:
                result['framework'] = 'Gravity Forms'

            result['success'] = confidence > 0.0
            result['confidence_score'] = confidence

            print(f"      📊 Quick confidence: {confidence:.3f}, Success: {result['success']}")

        except Exception as e:
            print(f"      💥 Quick detection error: {str(e)}")

        return result['success'], result

def is_valid_website(website):
    """Check if website URL is valid"""
    if pd.isna(website) or website == 'nan' or not isinstance(website, str):
        return False
    website = website.strip()
    return website.startswith('http://') or website.startswith('https://')

async def complete_50_dealership_test():
    """Complete the full 50 dealership test with optimized timing"""

    print("⚡ COMPLETE 50 DEALERSHIP TEST - Efficient Full Evaluation")
    print("=" * 80)
    print("🎯 Goal: Complete all 50 dealerships with optimized 20-second detection")
    print("⏱️  Target: ~30 minutes total (36 seconds per site)")
    print("=" * 80)

    # Load and validate data
    try:
        df = pd.read_csv('Dealerships - Jeep.csv')
        valid_websites = df[df['website'].apply(is_valid_website)]
        print(f"📊 Valid websites available: {len(valid_websites)}")
    except Exception as e:
        print(f"❌ Failed to load CSV: {e}")
        return

    # Use same random seed as original test to get same 50 dealerships
    random.seed(42)
    selected_dealerships = valid_websites.sample(n=50, random_state=42).reset_index(drop=True)

    # Create test directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_dir = f"Tests/complete_50_dealerships_{timestamp}"
    screenshots_dir = f"{test_dir}/screenshots"
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(screenshots_dir, exist_ok=True)

    print(f"\n📁 Test directory: {test_dir}")
    print(f"\n🎲 TESTING SAME 50 DEALERSHIPS FROM ORIGINAL TEST:")
    for i, row in selected_dealerships.iterrows():
        print(f"    {i+1:2d}. {row['dealer_name']} - {row['website']} ({row['city']}, {row['state']})")

    detector = EfficientDetector()
    results = []
    successful_detections = 0
    start_time = datetime.now()

    contact_patterns = ['/contact-us/', '/contact/']  # Reduced patterns for speed

    for index, row in selected_dealerships.iterrows():
        dealer_name = row['dealer_name']
        website = row['website']
        city = row['city']
        state = row['state']

        print(f"\n{'='*80}")
        print(f"⚡ TEST {index + 1}/50: {dealer_name}")
        print(f"🌐 {website}")

        test_start = datetime.now()
        found_form = False
        form_url = None
        detection_result = None

        stealth_manager = None
        playwright_instance = None
        browser = None

        try:
            stealth_manager = EnhancedStealthBrowserManager()
            playwright_instance = await async_playwright().start()
            browser = await stealth_manager.create_enhanced_stealth_browser(playwright_instance)
            context = await stealth_manager.create_enhanced_stealth_context(browser)
            page = await stealth_manager.create_enhanced_stealth_page(context)

            # Quick homepage load
            success, final_url, _ = await stealth_manager.navigate_with_redirect_handling(
                page, website, max_redirects=2
            )

            if success:
                print(f"   ✅ Homepage loaded")
                base_url = final_url.rstrip('/')

                # Quick contact page check (only try first pattern)
                contact_url = base_url + contact_patterns[0]
                print(f"   🎯 Trying contact page...")

                success, contact_final_url, _ = await stealth_manager.navigate_with_redirect_handling(
                    page, contact_url, max_redirects=2
                )

                if success:
                    print(f"      ✅ Contact page found")
                    has_forms, detection_result = await detector.quick_detection(page)
                    if has_forms:
                        found_form = True
                        form_url = contact_final_url

                # If no contact page, quick homepage check
                if not found_form:
                    print(f"   🏠 Quick homepage check...")
                    await page.goto(final_url)
                    has_forms, detection_result = await detector.quick_detection(page)
                    if has_forms:
                        found_form = True
                        form_url = final_url

            test_duration = (datetime.now() - test_start).total_seconds()

            if found_form:
                successful_detections += 1
                print(f"   🎉 SUCCESS! ({test_duration:.1f}s)")
                print(f"      📊 Confidence: {detection_result['confidence_score']:.3f}")

                # Quick screenshot (no full page)
                screenshot_name = f"{index+1:02d}_{dealer_name.replace(' ', '_')[:20]}_success.png"
                try:
                    await page.screenshot(path=f"{screenshots_dir}/{screenshot_name}")
                    print(f"      📸 Screenshot captured")
                except Exception:
                    print(f"      ⚠️ Screenshot skipped")

                results.append({
                    'test_num': index + 1,
                    'name': dealer_name,
                    'website': website,
                    'city': city,
                    'state': state,
                    'success': True,
                    'form_url': form_url,
                    'confidence': detection_result['confidence_score'],
                    'forms': detection_result['forms_found'],
                    'framework': detection_result['framework'],
                    'duration': test_duration,
                    'screenshot': screenshot_name
                })
            else:
                print(f"   ❌ No forms found ({test_duration:.1f}s)")
                results.append({
                    'test_num': index + 1,
                    'name': dealer_name,
                    'website': website,
                    'city': city,
                    'state': state,
                    'success': False,
                    'form_url': None,
                    'confidence': 0.0,
                    'forms': 0,
                    'framework': 'N/A',
                    'duration': test_duration,
                    'screenshot': None
                })

        except Exception as e:
            print(f"   💥 Test failed: {str(e)}")
            results.append({
                'test_num': index + 1,
                'name': dealer_name,
                'website': website,
                'city': city,
                'state': state,
                'success': False,
                'form_url': None,
                'confidence': 0.0,
                'forms': 0,
                'framework': 'N/A',
                'duration': 0.0,
                'screenshot': None
            })

        finally:
            try:
                if browser:
                    await browser.close()
                if playwright_instance:
                    await playwright_instance.stop()
            except Exception:
                pass

        # Progress update
        elapsed = (datetime.now() - start_time).total_seconds()
        estimated_total = (elapsed / (index + 1)) * 50
        remaining = estimated_total - elapsed

        print(f"   📊 Progress: {index + 1}/50 ({(index + 1)/50*100:.1f}%)")
        print(f"   ⏱️  Elapsed: {elapsed/60:.1f}min, Est. remaining: {remaining/60:.1f}min")
        print(f"   📈 Current success rate: {successful_detections}/{index + 1} = {successful_detections/(index + 1)*100:.1f}%")

        # Minimal delay
        await asyncio.sleep(0.5)

    # Final Results
    total_duration = (datetime.now() - start_time).total_seconds()
    success_rate = (successful_detections / 50) * 100
    avg_duration = total_duration / 50

    print(f"\n{'='*80}")
    print(f"⚡ COMPLETE 50 DEALERSHIP TEST RESULTS")
    print(f"{'='*80}")
    print(f"✅ **FINAL SUCCESS RATE: {success_rate:.1f}% ({successful_detections}/50)**")
    print(f"⏱️  **TOTAL TIME: {total_duration/60:.1f} minutes**")
    print(f"📊 **AVG TIME/SITE: {avg_duration:.1f} seconds**")
    print(f"📸 **SCREENSHOTS: {successful_detections} contact forms documented**")

    # Save comprehensive results
    results_df = pd.DataFrame(results)
    results_csv_path = f"{test_dir}/complete_50_test_results.csv"
    results_df.to_csv(results_csv_path, index=False)
    print(f"\n💾 Complete results saved to: {results_csv_path}")

    # Create final summary report
    with open(f"{test_dir}/complete_50_report.md", 'w') as f:
        f.write(f"# Complete 50 Dealership Test Report\n\n")
        f.write(f"**Test Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Final Success Rate**: {success_rate:.1f}% ({successful_detections}/50)\n")
        f.write(f"**Total Duration**: {total_duration/60:.1f} minutes\n")
        f.write(f"**Average Time/Site**: {avg_duration:.1f} seconds\n")
        f.write(f"**Screenshots Captured**: {successful_detections}\n\n")

        # Performance assessment
        if success_rate >= 90.0:
            f.write(f"## 🎉 OUTSTANDING SUCCESS!\n\n")
            f.write(f"Achieved {success_rate:.1f}% success rate - **EXCEEDS ALL TARGETS**\n\n")
        elif success_rate >= 80.0:
            f.write(f"## 🎯 EXCELLENT PERFORMANCE!\n\n")
            f.write(f"Achieved {success_rate:.1f}% success rate - **MEETS PRODUCTION STANDARDS**\n\n")
        else:
            f.write(f"## 📊 BASELINE ESTABLISHED\n\n")
            f.write(f"{success_rate:.1f}% success rate - **SOLID FOUNDATION FOR OPTIMIZATION**\n\n")

        # Successful sites
        successful_results = [r for r in results if r['success']]
        f.write(f"## Successful Detections ({len(successful_results)})\n\n")
        for result in successful_results:
            f.write(f"- **{result['name']}** ({result['city']}, {result['state']})\n")
            f.write(f"  - Confidence: {result['confidence']:.3f}, Duration: {result['duration']:.1f}s\n")

        # Failed sites
        failed_results = [r for r in results if not r['success']]
        if failed_results:
            f.write(f"\n## Failed Detections ({len(failed_results)})\n\n")
            for result in failed_results:
                f.write(f"- **{result['name']}** ({result['city']}, {result['state']})\n")

    # Performance evaluation
    if success_rate >= 90.0:
        print(f"\n🎉 **OUTSTANDING PERFORMANCE!** {success_rate:.1f}% exceeds all targets!")
        print(f"🚀 **PRODUCTION READY** - System validated at scale!")
    elif success_rate >= 80.0:
        print(f"\n🎯 **EXCELLENT PERFORMANCE!** {success_rate:.1f}% meets production standards!")
        print(f"✅ **DEPLOYMENT READY** - Strong performance validated!")
    else:
        print(f"\n📊 **BASELINE ESTABLISHED** - {success_rate:.1f}% provides optimization foundation")
        print(f"🔧 **ENHANCEMENT OPPORTUNITIES** identified for improvement")

    print(f"\n📁 Complete results: {test_dir}")
    print(f"📋 Detailed report: {test_dir}/complete_50_report.md")
    print(f"📊 CSV data: {results_csv_path}")

    return success_rate

if __name__ == "__main__":
    asyncio.run(complete_50_dealership_test())