# Semi-Automated CAPTCHA System Design

## Problem Statement

40% of dealership sites (8/20 in latest test) have CAPTCHA protection. These cannot be fully automated, but we can minimize manual work to just **solving the CAPTCHA and clicking submit**.

## Design Goal

**Automate 95% of the work**, leaving only:
1. Solving CAPTCHA (5-10 seconds)
2. Clicking submit button (1 second)

**Total manual time per site: ~10-15 seconds** instead of 2-3 minutes for full manual form filling.

---

## System Architecture

### Mode 1: Fully Automated (No CAPTCHA)
```
Bot → Find Contact Page → Detect Form → Fill Fields → Submit → Verify
```

### Mode 2: Semi-Automated (CAPTCHA Detected)
```
Bot → Find Contact Page → Detect Form → Fill Fields → PAUSE
Human → Solve CAPTCHA → Click Submit
Bot → Verify Submission → Continue to Next
```

---

## Implementation Design

### 1. CAPTCHA Detection & Pause System

```python
class SemiAutomatedFormSubmitter:
    """Handles forms with CAPTCHA by pausing for human intervention"""

    async def submit_with_human_assist(self, page, form_data, dealership_info):
        """
        1. Automate: Find and fill all form fields
        2. Detect CAPTCHA
        3. If CAPTCHA: Pause, notify human, wait for confirmation
        4. Human: Solve CAPTCHA + click submit
        5. Automate: Verify submission
        """

        # Step 1: Auto-fill all fields
        await self.auto_fill_all_fields(page, form_data)

        # Step 2: Detect CAPTCHA
        has_captcha, captcha_info = await self.detect_captcha(page)

        if not has_captcha:
            # Fully automated - submit directly
            return await self.auto_submit(page)

        # Step 3: CAPTCHA detected - pause for human
        return await self.pause_for_human_captcha(
            page=page,
            dealership=dealership_info,
            captcha_info=captcha_info
        )
```

### 2. Human Pause Interface

**Option A: Visual + Audio Alert**
```python
async def pause_for_human_captcha(self, page, dealership, captcha_info):
    """
    Pause automation and notify human to take over
    """

    # Make browser window prominent
    await page.bring_to_front()

    # Visual alert on page
    await page.evaluate("""
        () => {
            // Create overlay with instructions
            const overlay = document.createElement('div');
            overlay.id = 'captcha-assist-overlay';
            overlay.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #ff9800;
                color: white;
                padding: 20px;
                border-radius: 8px;
                z-index: 999999;
                font-family: Arial;
                font-size: 16px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                max-width: 400px;
            `;
            overlay.innerHTML = `
                <h3 style="margin: 0 0 10px 0;">⚠️ CAPTCHA DETECTED</h3>
                <p><strong>Dealership:</strong> ${document.title}</p>
                <p style="margin: 10px 0;"><strong>Action Required:</strong></p>
                <ol style="margin: 5px 0; padding-left: 20px;">
                    <li>Solve the CAPTCHA below ⬇️</li>
                    <li>Click the SUBMIT button</li>
                    <li>Click "Done" when submitted</li>
                </ol>
                <button id="captcha-done-btn" style="
                    background: #4CAF50;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                    width: 100%;
                    margin-top: 10px;
                ">✅ DONE - I Submitted the Form</button>
            `;
            document.body.appendChild(overlay);

            // Scroll to CAPTCHA
            const captcha = document.querySelector('.g-recaptcha, .h-captcha, [data-sitekey]');
            if (captcha) {
                captcha.scrollIntoView({ behavior: 'smooth', block: 'center' });
                captcha.style.border = '3px solid #ff9800';
            }
        }
    """)

    # Audio alert (system beep)
    print("\a")  # Terminal beep

    # Console alert with dealership info
    logger.info("="*80)
    logger.info("🔔 HUMAN ASSISTANCE REQUIRED")
    logger.info("="*80)
    logger.info(f"Dealership: {dealership['dealer_name']}")
    logger.info(f"Website: {dealership['website']}")
    logger.info(f"CAPTCHA Type: {captcha_info['type']}")
    logger.info("")
    logger.info("⏸️  AUTOMATION PAUSED")
    logger.info("👉 Please:")
    logger.info("   1. Solve the CAPTCHA")
    logger.info("   2. Click SUBMIT button")
    logger.info("   3. Click 'Done' button in orange box")
    logger.info("="*80)

    # Wait for human to click "Done" button
    await page.wait_for_selector("#captcha-done-btn", state="visible")

    # Poll for "Done" button click
    done_clicked = await page.evaluate("""
        () => new Promise((resolve) => {
            const btn = document.getElementById('captcha-done-btn');
            btn.addEventListener('click', () => {
                // Remove overlay
                document.getElementById('captcha-assist-overlay').remove();
                resolve(true);
            });
        })
    """)

    logger.info("✅ Human confirmed submission completed")

    # Verify submission
    await asyncio.sleep(2)
    verification = await self.verify_submission_success(page)

    return SubmissionResult(
        success=verification['success'],
        method='human_assisted',
        verification=verification['method'],
        blocker=None,
        notes='Human solved CAPTCHA and submitted'
    )
```

**Option B: Simple Terminal Prompt (Faster for bulk processing)**
```python
async def pause_for_human_captcha_simple(self, page, dealership, captcha_info):
    """
    Simpler version - just pause and wait for Enter key
    """

    # Highlight CAPTCHA on page
    await page.evaluate("""
        () => {
            const captcha = document.querySelector('.g-recaptcha, .h-captcha');
            if (captcha) {
                captcha.scrollIntoView({ behavior: 'smooth', block: 'center' });
                captcha.style.border = '5px solid red';
                captcha.style.boxShadow = '0 0 20px red';
            }
        }
    """)

    # Console prompt
    print("\n" + "="*80)
    print(f"🔔 CAPTCHA: {dealership['dealer_name']} - {dealership['website']}")
    print("="*80)
    print("👉 Action: Solve CAPTCHA and click SUBMIT")

    # Wait for user to press Enter
    input("\n✅ Press ENTER when you've submitted the form...")

    # Verify
    await asyncio.sleep(2)
    verification = await self.verify_submission_success(page)

    return SubmissionResult(
        success=verification['success'],
        method='human_assisted',
        verification=verification['method']
    )
```

---

## 3. Batch Processing Workflow

```python
class BatchProcessingWithHumanAssist:
    """Process multiple dealerships with human assistance for CAPTCHAs"""

    async def process_batch(self, dealerships, test_data):
        """
        Process dealerships in batches:
        - Fully automated sites: Complete without intervention
        - CAPTCHA sites: Queue for human batch processing
        """

        automated_results = []
        human_assist_queue = []

        for dealership in dealerships:
            result = await self.process_dealership(dealership, test_data)

            if result['requires_human']:
                human_assist_queue.append({
                    'dealership': dealership,
                    'page_state': result['page_state'],
                    'captcha_info': result['captcha_info']
                })
            else:
                automated_results.append(result)

        # Process human-assist queue
        if human_assist_queue:
            logger.info(f"\n{'='*80}")
            logger.info(f"HUMAN ASSISTANCE NEEDED FOR {len(human_assist_queue)} SITES")
            logger.info(f"{'='*80}\n")

            human_results = await self.process_human_assist_queue(human_assist_queue)
            automated_results.extend(human_results)

        return automated_results

    async def process_human_assist_queue(self, queue):
        """
        Process all CAPTCHA sites in sequence with human help
        """
        results = []

        for idx, item in enumerate(queue, 1):
            logger.info(f"\n[{idx}/{len(queue)}] {item['dealership']['dealer_name']}")

            # Already have page loaded and form filled from earlier
            # Just need human to solve CAPTCHA and submit
            result = await self.human_assist_submit(
                page=item['page_state'],
                dealership=item['dealership'],
                captcha_info=item['captcha_info']
            )

            results.append(result)

        return results
```

---

## 4. Smart Queuing Strategy

**Option A: Process CAPTCHAs Immediately (Real-time)**
- Pause automation when CAPTCHA detected
- Human solves immediately
- Continue to next site

**Pros**: Immediate feedback, no context switching
**Cons**: Interrupts flow

**Option B: Queue CAPTCHAs for Batch (Deferred)**
- Automation processes all sites first
- Collect all CAPTCHA sites in queue
- Human processes all CAPTCHAs in one session

**Pros**: Better workflow, fewer interruptions
**Cons**: Need to maintain browser sessions or re-navigate

**Recommended: Hybrid Approach**
```python
class SmartQueueing:
    def __init__(self, mode='batch'):
        self.mode = mode  # 'immediate' or 'batch'
        self.captcha_queue = []

    async def handle_captcha(self, page, dealership, captcha_info):
        if self.mode == 'immediate':
            # Pause now, wait for human
            return await self.pause_for_human(page, dealership)

        else:  # batch mode
            # Save state for later
            screenshot = await page.screenshot()

            self.captcha_queue.append({
                'dealership': dealership,
                'url': page.url,
                'screenshot': screenshot,
                'captcha_info': captcha_info,
                'timestamp': datetime.now()
            })

            return SubmissionResult(
                success=False,
                method='queued_for_human',
                blocker='CAPTCHA_QUEUED'
            )
```

---

## 5. Enhanced User Experience Features

### A. Visual Progress Dashboard
```python
def show_progress_dashboard(stats):
    """
    Display real-time progress:

    ═══════════════════════════════════════════
    AUTOMATION PROGRESS: 15/20 (75%)
    ═══════════════════════════════════════════
    ✅ Fully Automated:     12 sites
    ⏸️  Waiting for Human:   3 sites (queued)
    ❌ Failed:              0 sites
    ⏳ In Progress:         5 sites
    ═══════════════════════════════════════════

    CAPTCHA QUEUE (3):
    1. Brown's Jeep - Ready for submission
    2. Jack CDJR - Ready for submission
    3. Team Chrysler - Ready for submission

    👉 Press 'P' to process CAPTCHA queue now
    """
```

### B. Keyboard Shortcuts
```python
# During batch processing:
# - Press 'P' to pause and process CAPTCHA queue
# - Press 'S' to skip current site
# - Press 'Q' to quit gracefully
```

### C. Session Persistence
```python
# Save state between runs
{
    "session_id": "20251003_120000",
    "dealerships_processed": 15,
    "captcha_queue": [
        {
            "dealer_name": "Brown's Jeep",
            "contact_url": "https://...",
            "form_pre_filled": true,
            "awaiting_human": true
        }
    ]
}

# Resume later:
# python resume_captcha_session.py --session 20251003_120000
```

---

## 6. Implementation Example

```python
# Main automation script with semi-automated CAPTCHA handling

async def main():
    dealerships = load_dealerships()

    # Choose mode
    mode = input("Mode? (1=Immediate CAPTCHA, 2=Batch CAPTCHA): ")
    mode = 'immediate' if mode == '1' else 'batch'

    processor = SemiAutomatedProcessor(mode=mode)

    results = await processor.process_batch(
        dealerships=dealerships[:20],
        test_data=TEST_DATA
    )

    # Summary
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)

    fully_automated = sum(1 for r in results if r['method'] != 'human_assisted')
    human_assisted = sum(1 for r in results if r['method'] == 'human_assisted')
    failed = sum(1 for r in results if not r['success'])

    print(f"✅ Fully Automated:  {fully_automated}/{len(results)}")
    print(f"👤 Human Assisted:   {human_assisted}/{len(results)}")
    print(f"❌ Failed:           {failed}/{len(results)}")
    print(f"")
    print(f"Total Success Rate:  {(fully_automated + human_assisted)/len(results)*100:.1f}%")
    print(f"Time Saved:          ~{human_assisted * 2.5:.0f} minutes")
    print("="*80)
```

---

## 7. Time Savings Calculation

**Manual Form Filling (per site):**
- Find contact page: 30 seconds
- Fill all fields: 60 seconds
- Solve CAPTCHA: 10 seconds
- Submit: 5 seconds
- **Total: ~105 seconds (~2 minutes)**

**Semi-Automated (per site):**
- Bot finds page: 5 seconds (auto)
- Bot fills fields: 8 seconds (auto)
- Human solves CAPTCHA: 10 seconds (manual)
- Human clicks submit: 2 seconds (manual)
- Bot verifies: 3 seconds (auto)
- **Total: ~28 seconds**

**Time Saved: 77 seconds per site = 73% reduction**

**For 8 CAPTCHA sites:**
- Manual: 16 minutes
- Semi-Auto: 4 minutes
- **Saved: 12 minutes**

---

## 8. Recommended Configuration

```python
# config.py

SEMI_AUTO_CONFIG = {
    # Mode: 'immediate' or 'batch'
    'mode': 'batch',  # Batch is more efficient

    # Visual alerts
    'show_overlay': True,
    'audio_alert': True,
    'highlight_captcha': True,

    # Timing
    'pause_before_captcha': 2,  # Seconds to prepare
    'wait_after_submit': 3,     # Seconds to verify

    # Batch settings
    'batch_size': 20,
    'pause_between_batches': 30,  # Seconds

    # Verification
    'screenshot_on_submit': True,
    'require_human_confirmation': True,
}
```

---

## 9. Future Enhancements

### Phase 1: Basic Semi-Automation ✅
- Auto-fill forms
- Detect CAPTCHA
- Pause for human
- Verify submission

### Phase 2: Smart Queuing
- Batch CAPTCHA processing
- Session persistence
- Progress dashboard

### Phase 3: Advanced Features
- 2Captcha API integration (fully automated for $1-3/1000 solves)
- Browser extension for one-click solving
- Mobile app notifications
- Parallel browser sessions (10 sites at once, batch all CAPTCHAs at end)

---

## Conclusion

This semi-automated approach:
- ✅ **Reduces manual work by 73%**
- ✅ **Processes 20 sites in ~10 minutes** (vs 40 minutes manual)
- ✅ **Only requires 10-15 seconds per CAPTCHA site**
- ✅ **Maintains high success rate** (~60-70% with CAPTCHA solving)
- ✅ **User-friendly with visual + audio alerts**
- ✅ **Flexible modes** (immediate or batch)

Would save **hours per day** when processing hundreds of dealerships.
