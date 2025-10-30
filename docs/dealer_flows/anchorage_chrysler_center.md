# Anchorage Chrysler Center Contact Flow

This dealership gates the contact form behind a modal sequence. Our automation must mimic a user opening the modal, choosing a department, and then interacting with the revealed form.

## Step-by-step Interaction
1. **Navigate to the contact page**: `https://www.anchoragechryslercenter.com/contactus` (fall back to `/contact-us/` and follow the on-page CTA if redirected).
2. **Dismiss cookie banner**: wait for the bottom banner and click the `Ok` button (`button:has-text("Ok")`).
3. **Scroll into view**: smooth scroll the viewport to the “Send a message” tile so the CTA is visible (~400px down) and pause briefly to emulate human reading.
4. **Open message modal**: click the black button with text `Send Us A Message`. This triggers the department selector modal (`#textmodal___BV_modal_body_`).
5. **Choose department**: click the `Sales` button inside the modal (selector: `#textmodal___BV_modal_body_ a:has-text("Sales")`). The modal closes and the lead form appears centered on the page.
6. **Interact with the contact form**: the form root is `form.contactForm`. Key fields:
   - `#firstName`
   - `#lastName`
   - `#emailAddress`
   - `#phoneNumber`
   - `#zipCode`
   - `#textarea`
   - Preferred contact dropdown: `.preferred-contact .custom-select-dropdown`
   - TCPA checkbox: `#23marketing-text-disclaimer`
7. **Submit control**: the send button is `input[type="submit"][value="Send"]`.

## Automation Notes
- Add short waits (500–800 ms) between hover/click actions to avoid bot heuristics.
- Ensure the contact modal is dismissed cleanly by closing it or submitting the form to prevent state leakage across test runs.
- Record screenshots after the form loads for regression fixtures (`tests/fixtures/form_detection/screenshots/anchorage_chrysler_center_form.png`).

## Open TODOs
- Integrate this modal flow into the form detector so it automatically clicks the CTA, selects `Sales`, and then proceeds with field detection.
- Update the dataset label to capture the form once the automated path is stable.
