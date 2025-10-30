"""
Enhanced human-like form filling to avoid Cloudflare detection.
Implements realistic typing patterns, timing, and interaction behaviors.
"""

import asyncio
import random
import re
from typing import List, Optional
from playwright.async_api import Page, Locator


class HumanFormFiller:
    """Fills forms with realistic human-like behavior to avoid detection."""

    def __init__(self):
        self.typing_speed_range = (80, 180)  # WPM equivalent in ms
        self.pause_after_word = (200, 500)   # Natural pause between words
        self.pause_between_fields = (800, 2000)  # Time to "think" between fields
        self.error_rate = 0.02  # 2% chance of typos that get corrected

    async def fill_field_naturally(
        self,
        page: Page,
        selector: str,
        value: str,
        field_name: str
    ) -> bool:
        """Fill a field with human-like typing behavior."""
        try:
            locator = page.locator(selector)
            await locator.wait_for(timeout=4000)

            # Step 1: Move mouse to field area (not exact center)
            await self._move_to_field_naturally(locator)

            # Step 2: Click and focus with realistic behavior
            await self._click_and_focus(locator)

            # Step 3: Clear field safely (if needed)
            await self._clear_field_naturally(locator)

            # Step 4: Type with human-like patterns
            await self._type_like_human(locator, value)

            # Step 5: Brief pause to "verify" what was typed
            await asyncio.sleep(random.uniform(0.3, 0.8))

            return True

        except Exception as exc:
            print(f"[error] Failed to fill {field_name}: {exc}")
            return False

    async def _move_to_field_naturally(self, locator: Locator) -> None:
        """Move mouse to field with natural cursor movement."""
        # Get field bounding box
        box = await locator.bounding_box()
        if not box:
            return

        # Calculate target point (slightly off-center for realism)
        target_x = box['x'] + box['width'] * random.uniform(0.3, 0.7)
        target_y = box['y'] + box['height'] * random.uniform(0.3, 0.7)

        # Start from nearby position (Playwright doesn't track mouse position)
        # Start from 100-200px away from field for realistic movement
        start_x = target_x - random.uniform(100, 200)
        start_y = target_y - random.uniform(50, 150)

        # Move in slightly curved path (not straight line)
        await self._move_mouse_naturally(
            locator.page,
            start_x, start_y,
            target_x, target_y
        )

    async def _move_mouse_naturally(self, page: Page, start_x: float, start_y: float, end_x: float, end_y: float):
        """Move mouse in realistic curved path with varying speed."""
        steps = random.randint(8, 15)  # Number of intermediate points

        for i in range(steps + 1):
            progress = i / steps

            # Add slight curve randomness
            curve_offset = random.uniform(-10, 10) * (1 - abs(2 * progress - 1))

            x = start_x + (end_x - start_x) * progress + curve_offset
            y = start_y + (end_y - start_y) * progress + curve_offset

            await page.mouse.move(x, y)

            # Variable speed - slower at start/end, faster in middle
            speed_factor = 1 - abs(2 * progress - 1) * 0.5
            delay = random.uniform(10, 30) * speed_factor
            await asyncio.sleep(delay / 1000)

    async def _click_and_focus(self, locator: Locator) -> None:
        """Click and focus field with realistic behavior."""
        # Hover briefly before clicking (humans do this)
        await locator.hover()
        await asyncio.sleep(random.uniform(0.1, 0.3))

        # Click with slight randomness in timing
        await locator.click()

        # Brief pause for focus to register
        await asyncio.sleep(random.uniform(0.05, 0.15))

    async def _clear_field_naturally(self, locator: Locator) -> None:
        """Clear field contents if present, using realistic methods."""
        try:
            # Check if field has content
            current_value = await locator.input_value()
            if not current_value:
                return

            # Use Ctrl+A, Delete (like humans do)
            await locator.press('Control+a')
            await asyncio.sleep(random.uniform(0.05, 0.1))
            await locator.press('Delete')
            await asyncio.sleep(random.uniform(0.1, 0.2))

        except Exception:
            # Fallback: use backspace multiple times
            for _ in range(20):  # Clear up to 20 characters
                await locator.press('Backspace')
                await asyncio.sleep(random.uniform(0.02, 0.05))

    async def _type_like_human(self, locator: Locator, text: str) -> None:
        """Type text with realistic human patterns."""
        words = text.split(' ')

        for word_index, word in enumerate(words):
            # Type each word with character-by-character timing
            await self._type_word_naturally(locator, word)

            # Add space between words (except last word)
            if word_index < len(words) - 1:
                await locator.type(' ')
                # Natural pause between words
                await asyncio.sleep(random.uniform(*self.pause_after_word) / 1000)

    async def _type_word_naturally(self, locator: Locator, word: str) -> None:
        """Type a single word with realistic character timing."""
        for char_index, char in enumerate(word):
            # Simulate occasional typos and corrections
            if random.random() < self.error_rate and char_index > 0:
                await self._simulate_typo_correction(locator, char)
            else:
                await locator.type(char)

            # Realistic typing speed variation
            char_delay = self._calculate_char_delay(char, char_index, len(word))
            await asyncio.sleep(char_delay / 1000)

    async def _simulate_typo_correction(self, locator: Locator, correct_char: str) -> None:
        """Simulate a typo followed by correction."""
        # Type wrong character (usually adjacent key)
        typos = {
            'e': ['r', 'w'], 'r': ['e', 't'], 't': ['r', 'y'], 'a': ['s', 'q'],
            's': ['a', 'd'], 'd': ['s', 'f'], 'n': ['b', 'm'], 'm': ['n', 'k']
        }
        wrong_char = random.choice(typos.get(correct_char.lower(), [correct_char]))
        await locator.type(wrong_char)

        # Brief pause as human realizes mistake
        await asyncio.sleep(random.uniform(0.1, 0.3))

        # Correct the typo
        await locator.press('Backspace')
        await asyncio.sleep(random.uniform(0.05, 0.1))
        await locator.type(correct_char)

    def _calculate_char_delay(self, char: str, position: int, word_length: int) -> float:
        """Calculate realistic delay for character based on human typing patterns."""
        base_delay = random.uniform(*self.typing_speed_range)

        # Slower for first/last characters of words
        if position == 0 or position == word_length - 1:
            base_delay *= 1.2

        # Slower for uppercase letters
        if char.isupper():
            base_delay *= 1.3

        # Slower for numbers and special characters
        if char.isdigit() or not char.isalnum():
            base_delay *= 1.4

        # Common letter combinations are faster
        fast_combos = ['th', 'he', 'in', 'er', 'an', 're', 'ed', 'nd', 'ha', 'et']
        # This would need context of previous char for full implementation

        return base_delay

    async def pause_between_fields(self, field_name: str) -> None:
        """Natural pause between fields as human thinks about next input."""
        # Longer pauses for complex fields like messages
        if 'message' in field_name.lower() or 'comment' in field_name.lower():
            pause = random.uniform(1500, 3500)  # 1.5-3.5 seconds to "think"
        else:
            pause = random.uniform(*self.pause_between_fields)

        await asyncio.sleep(pause / 1000)


class StealthFormSubmissionRunner:
    """Form submission with enhanced stealth and human-like behavior."""

    def __init__(self):
        self.human_filler = HumanFormFiller()

    async def fill_form_stealthily(
        self,
        page: Page,
        form_fields: dict,
        payload: dict
    ) -> dict:
        """Fill entire form with human-like behavior."""
        results = {
            'fields_filled': [],
            'fields_failed': [],
            'total_time': 0
        }

        start_time = asyncio.get_event_loop().time()

        # Randomize field filling order (humans don't always go top-to-bottom)
        field_items = list(form_fields.items())
        random.shuffle(field_items)

        for field_name, field_info in field_items:
            if field_name not in payload:
                continue

            value = payload[field_name]
            if not value:
                continue

            # Natural pause before each field
            await self.human_filler.pause_between_fields(field_name)

            # Fill field with human-like behavior
            success = await self.human_filler.fill_field_naturally(
                page,
                field_info['selector'],
                str(value),
                field_name
            )

            if success:
                results['fields_filled'].append(field_name)
            else:
                results['fields_failed'].append(field_name)

        results['total_time'] = asyncio.get_event_loop().time() - start_time
        return results

    async def submit_form_naturally(self, page: Page, submit_selector: str) -> bool:
        """Submit form with natural human behavior."""
        try:
            submit_button = page.locator(submit_selector)

            # Move to submit button naturally
            await self.human_filler._move_to_field_naturally(submit_button)

            # Brief pause as human reviews form
            await asyncio.sleep(random.uniform(0.8, 2.0))

            # Hover over submit button
            await submit_button.hover()
            await asyncio.sleep(random.uniform(0.2, 0.5))

            # Click submit
            await submit_button.click()

            # Wait for submission to process
            await asyncio.sleep(random.uniform(1.0, 2.5))

            return True

        except Exception as exc:
            print(f"[error] Form submission failed: {exc}")
            return False