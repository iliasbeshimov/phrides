#!/usr/bin/env python3

import asyncio
import random
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
from src.automation.forms.form_submitter import FormSubmissionRunner, ContactPayload

async def test_batch_submissions():
    """Test form submissions on 5 random dealerships"""

    # Load dealership data
    csv_path = Path("Dealerships.csv")
    if not csv_path.exists():
        csv_path = Path("frontend/Dealerships.csv")

    if not csv_path.exists():
        print("ERROR: Could not find Dealerships.csv")
        return

    df = pd.read_csv(csv_path)

    # Filter to dealerships with contact pages
    contact_dealers = df[df['website'].notna() & df['website'].str.contains('http', na=False)]

    # Select 5 random dealerships
    random_dealers = contact_dealers.sample(n=min(5, len(contact_dealers)))

    print(f"Testing form submissions on {len(random_dealers)} random dealerships...")
    print("=" * 60)

    results = []

    for idx, dealer in random_dealers.iterrows():
        dealer_name = dealer['dealer_name']
        website = dealer['website']

        # Try to construct contact URL
        contact_url = website.rstrip('/') + '/contact-us/'

        print(f"\n[{idx+1}/5] Testing: {dealer_name}")
        print(f"Contact URL: {contact_url}")
        print("-" * 40)

        try:
            # Create form submitter
            submitter = FormSubmissionRunner(
                headless=False,  # Run visible due to Chrome headless deprecation
                use_cloudflare_stealth=True
            )

            # Test data
            contact_payload = ContactPayload(
                first_name='Miguel',
                last_name='Montoya',
                email='migueljmontoya@protonmail.com',
                phone='555-123-4567',
                zip_code='90210',
                message='I am interested in learning more about your vehicle inventory and leasing options. Please contact me with available deals.'
            )

            # Submit form
            result = await submitter.run(
                dealer_name=f"{dealer_name} (Batch Test)",
                url=contact_url,
                payload=contact_payload
            )

            results.append({
                'dealer': dealer_name,
                'url': contact_url,
                'status': result.status,
                'fields_filled': len(result.fields_filled),
                'confirmation_text': result.confirmation_text or 'none',
                'errors': result.errors
            })

            print(f"Status: {result.status}")
            print(f"Fields filled: {len(result.fields_filled)}")
            print(f"Confirmation: {result.confirmation_text or 'none'}")

            if result.errors:
                print(f"Errors: {result.errors}")

        except Exception as e:
            print(f"ERROR: {str(e)}")
            results.append({
                'dealer': dealer_name,
                'url': contact_url,
                'status': 'error',
                'fields_filled': 0,
                'confirmation_text': 'none',
                'errors': [str(e)]
            })

        # Brief pause between submissions
        await asyncio.sleep(2)

    # Summary
    print("\n" + "=" * 60)
    print("BATCH TEST SUMMARY")
    print("=" * 60)

    success_count = sum(1 for r in results if r['status'] == 'submission_success')

    for i, result in enumerate(results, 1):
        status_emoji = "✅" if result['status'] == 'submission_success' else "❌"
        print(f"{i}. {status_emoji} {result['dealer']}")
        print(f"   Status: {result['status']}")
        print(f"   Fields: {result['fields_filled']}")
        print(f"   Confirmation: {result['confirmation_text']}")
        if result['errors']:
            print(f"   Errors: {result['errors']}")
        print()

    print(f"SUCCESS RATE: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    results_file = f"batch_test_results_{timestamp}.json"

    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'total_tests': len(results),
            'successful_submissions': success_count,
            'success_rate': success_count/len(results),
            'results': results
        }, f, indent=2)

    print(f"\nDetailed results saved to: {results_file}")
    return results

if __name__ == "__main__":
    asyncio.run(test_batch_submissions())