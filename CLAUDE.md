CLAUDE.md for Butter & Crumble Preorder Bot
Project Overview
A Python-based automation tool designed to monitor the Butter and Crumble shop, wait for a specific drop time, and programmatically add items to the cart.

Build & Setup Commands
Install Dependencies: pip install playwright pytest-playwright

Install Browser Binaries: playwright install chromium

Run Bot: python main.py

Testing Commands
Run All Tests: pytest

Run with Headless Browser Off (Debug): pytest --headed

Logic & Guidelines
Browser Engine: Use Playwright (Python) for its superior handling of modern web components and faster execution in WSL.

Timing: Use the apscheduler or schedule library for precision timing.

Stealth: Implement playwright-stealth or realistic user-agent headers to avoid being flagged by Hotplate’s bot detection.

Error Handling: If an item is "Sold Out" or the button isn't clickable yet, the script should retry every 500ms until the timeout is reached.

Environment: Store sensitive data (email, phone, item names) in a .env file; do not hardcode them.

Style Preferences
Type Hinting: Use Python type hints for all function signatures.

Logging: Use the logging module instead of print() for better tracking of timestamps during high-stakes drops.

Wait Strategies: Prefer page.wait_for_selector() over time.sleep().