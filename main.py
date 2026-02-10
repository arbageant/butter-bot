"""
Butter & Crumble Preorder Bot
Monitors the Hotplate shop and checks if the Order button is active.
"""

import logging
import sys
from typing import Optional
from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)


def load_config() -> dict[str, str]:
    """Load configuration from environment variables."""
    load_dotenv()

    config = {
        'url': os.getenv('HOTPLATE_URL', 'https://www.hotplate.com/butterandcrumble'),
        'headless': os.getenv('HEADLESS', 'true').lower() == 'true',
        'retry_interval_ms': int(os.getenv('RETRY_INTERVAL_MS', '500')),
        'timeout_seconds': int(os.getenv('TIMEOUT_SECONDS', '30')),
    }

    logger.info(f"Configuration loaded: URL={config['url']}, Headless={config['headless']}")
    return config


def check_order_button(page: Page) -> bool:
    """
    Check if the Order button is active and clickable.

    Args:
        page: Playwright page object

    Returns:
        True if the button is active and clickable, False otherwise
    """
    try:
        # Common selectors for order/add to cart buttons on e-commerce sites
        # We'll need to inspect the actual page to get the exact selector
        selectors = [
            'button:has-text("Order")',
            'button:has-text("Add to Cart")',
            'button:has-text("Pre-order")',
            '[data-testid*="order"]',
            '[data-testid*="cart"]',
            '.order-button',
            '.add-to-cart',
        ]

        for selector in selectors:
            try:
                # Wait for the element with a short timeout
                element = page.wait_for_selector(selector, timeout=2000)
                if element:
                    # Check if the button is enabled
                    is_disabled = element.is_disabled()
                    is_visible = element.is_visible()

                    if is_visible and not is_disabled:
                        logger.info(f"✓ Order button found and active! Selector: {selector}")
                        return True
                    else:
                        logger.info(f"Order button found but not active. Selector: {selector}, Disabled: {is_disabled}, Visible: {is_visible}")

            except PlaywrightTimeoutError:
                continue

        logger.warning("Order button not found with any known selector")
        return False

    except Exception as e:
        logger.error(f"Error checking order button: {e}")
        return False


def run_bot() -> None:
    """Main bot execution function."""
    config = load_config()

    logger.info("Starting Butter & Crumble Bot...")
    logger.info(f"Target URL: {config['url']}")

    with sync_playwright() as playwright:
        # Launch browser with stealth settings
        browser: Browser = playwright.chromium.launch(
            headless=config['headless'],
            args=[
                '--disable-blink-features=AutomationControlled',
            ]
        )

        # Create context with realistic user agent
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
        )

        # Add stealth scripts
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        page: Page = context.new_page()

        try:
            logger.info(f"Navigating to {config['url']}...")
            page.goto(config['url'], wait_until='networkidle')
            logger.info("Page loaded successfully")

            # Check if order button is active
            is_active = check_order_button(page)

            if is_active:
                logger.info("🎉 SUCCESS: Order button is ACTIVE!")
            else:
                logger.info("⏳ Order button is not active yet or not found")

            # Keep browser open for a moment so user can see the result
            if not config['headless']:
                logger.info("Browser will remain open for 5 seconds...")
                page.wait_for_timeout(5000)

        except Exception as e:
            logger.error(f"Error during bot execution: {e}", exc_info=True)

        finally:
            browser.close()
            logger.info("Browser closed")


if __name__ == "__main__":
    run_bot()
