"""
Butter & Crumble Preorder Bot
Monitors the Hotplate shop and checks if the Order button is active.
"""

import logging
import sys
from typing import Optional
from datetime import datetime
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


def parse_drop_date(date_text: str) -> Optional[datetime]:
    """
    Parse the drop date from text like 'Dropped on February 10, 2026'.

    Args:
        date_text: Text containing the drop date

    Returns:
        datetime object or None if parsing fails
    """
    try:
        # Extract date from "Dropped on February 10, 2026" format
        if "Dropped on" in date_text:
            date_part = date_text.replace("Dropped on ", "").strip()
            return datetime.strptime(date_part, "%B %d, %Y")
    except Exception as e:
        logger.debug(f"Failed to parse date '{date_text}': {e}")
    return None


def find_and_click_drop_card(page: Page, title_search: str = "Thurs - Sun") -> bool:
    """
    Find and click on the drop card that contains the specified text in its title.

    Args:
        page: Playwright page object
        title_search: Text to search for in the drop card title (default: "Thurs - Sun")

    Returns:
        True if the drop card was found and clicked, False otherwise
    """
    try:
        logger.info(f"Looking for drop card with title containing '{title_search}'")

        # Wait for page to be fully loaded
        page.wait_for_load_state("networkidle")
        logger.info("Page is in networkidle state")

        # Take a screenshot for debugging
        page.screenshot(path="debug_page.png")
        logger.info("Screenshot saved to debug_page.png")

        # Wait for any drop card container to appear
        logger.info("Waiting for drop cards to load...")
        drop_cards = []

        # Try to find drop cards with different selectors
        selectors_to_try = [
            'div.c-fixGjY.c-fixGjY-icLbouK-css',
            'div.c-fixGjY.c-fixGjY-igxtwkj-css',
            'div[class*="c-fixGjY"]',  # More flexible selector
        ]

        for selector in selectors_to_try:
            try:
                page.wait_for_selector(selector, timeout=3000)
                drop_cards = page.query_selector_all(selector)
                if drop_cards:
                    logger.info(f"Found {len(drop_cards)} elements with selector: {selector}")
                    break
            except PlaywrightTimeoutError:
                logger.debug(f"Selector '{selector}' not found, trying next...")
                continue

        if not drop_cards:
            logger.error("No drop cards found with any selector")
            return False

        logger.info(f"Found {len(drop_cards)} drop cards on the page")

        for idx, card in enumerate(drop_cards):
            try:
                # Get all h2 elements to find titles
                title_element = card.query_selector('h2')
                if not title_element:
                    logger.debug(f"Drop card #{idx + 1}: No h2 title found")
                    continue

                title = title_element.inner_text()
                logger.info(f"Drop card #{idx + 1}: '{title}'")

                # Check if the title contains the search string
                if title_search.lower() in title.lower():
                    logger.info(f"✓ Found matching drop card! '{title}'")

                    # Check if it's sold out
                    sold_out_elements = card.query_selector_all('div:has-text("Sold Out")')
                    is_sold_out = any(elem.is_visible() for elem in sold_out_elements) if sold_out_elements else False

                    if is_sold_out:
                        logger.warning(f"⚠️  Drop card is marked as 'Sold Out'")

                    # Try multiple strategies to find and click the order button
                    clicked = False

                    # Strategy 1: Find button with specific classes
                    order_buttons = card.query_selector_all('div[class*="c-bYwOQu"]')
                    logger.info(f"Found {len(order_buttons)} potential order buttons")

                    for btn in order_buttons:
                        btn_text = btn.inner_text()
                        logger.info(f"Button text: '{btn_text}'")
                        if "Click to order" in btn_text or "order" in btn_text.lower():
                            logger.info("Clicking 'Click to order' button...")
                            btn.scroll_into_view_if_needed()
                            page.wait_for_timeout(500)  # Small delay for scrolling
                            btn.click(force=True)
                            logger.info("🎉 Successfully clicked order button!")
                            clicked = True
                            break

                    if clicked:
                        return True

                    # Strategy 2: Click anything with "Click to order" text
                    order_btn_by_text = card.query_selector('div:has-text("Click to order")')
                    if order_btn_by_text:
                        logger.info("Clicking button found by text...")
                        order_btn_by_text.scroll_into_view_if_needed()
                        page.wait_for_timeout(500)
                        order_btn_by_text.click(force=True)
                        logger.info("🎉 Successfully clicked order button!")
                        return True

                    # Strategy 3: Fallback - click the card itself
                    logger.info("Order button not found, clicking card...")
                    card.scroll_into_view_if_needed()
                    page.wait_for_timeout(500)
                    card.click()
                    logger.info("🎉 Successfully clicked drop card!")
                    return True

            except Exception as e:
                logger.error(f"Error processing drop card #{idx + 1}: {e}", exc_info=True)
                continue

        logger.warning(f"No drop card found with title containing '{title_search}'")
        return False

    except PlaywrightTimeoutError:
        logger.error("Timeout waiting for drop cards to load")
        return False
    except Exception as e:
        logger.error(f"Error finding drop card: {e}", exc_info=True)
        return False


def find_and_click_product(page: Page, product_name: str = "Small Pastry Box") -> bool:
    """
    Find and click on a product item on the drop page.

    Args:
        page: Playwright page object
        product_name: Name of the product to click (default: "Small Pastry Box")

    Returns:
        True if the product was found and clicked, False otherwise
    """
    try:
        logger.info(f"Looking for product: '{product_name}'")

        # Wait for the page to load
        page.wait_for_load_state("networkidle")
        logger.info("Product page loaded")

        # Take a screenshot for debugging
        page.screenshot(path="debug_product_page.png")
        logger.info("Screenshot saved to debug_product_page.png")

        # Wait for product buttons to appear
        logger.info("Waiting for product items to load...")
        page.wait_for_selector('button.c-ietuGy', timeout=10000)

        # Find all product buttons
        product_buttons = page.query_selector_all('button.c-ietuGy')
        logger.info(f"Found {len(product_buttons)} product items on the page")

        for idx, button in enumerate(product_buttons):
            try:
                # Get the product title
                title_element = button.query_selector('h3')
                if not title_element:
                    logger.debug(f"Product #{idx + 1}: No h3 title found")
                    continue

                title = title_element.inner_text()

                # Get the price
                price_element = button.query_selector('p.c-fFmitg')
                price = price_element.inner_text() if price_element else "N/A"

                # Check if sold out
                data_status = button.query_selector('div[data-status]')
                status = data_status.get_attribute('data-status') if data_status else "unknown"

                sold_out_badge = button.query_selector('div.c-iNPRhU')
                is_sold_out = sold_out_badge.is_visible() if sold_out_badge else False

                logger.info(f"Product #{idx + 1}: '{title}' - {price} - Status: {status}")

                # Check if this is the product we're looking for
                if product_name.lower() in title.lower():
                    logger.info(f"✓ Found matching product! '{title}' - {price}")

                    if is_sold_out:
                        logger.warning(f"⚠️  Product is marked as 'Sold Out'")

                    # Click the product button
                    logger.info(f"Clicking product button for '{title}'...")
                    button.scroll_into_view_if_needed()
                    page.wait_for_timeout(500)
                    button.click(force=True)
                    logger.info("🎉 Successfully clicked product button!")
                    return True

            except Exception as e:
                logger.error(f"Error processing product #{idx + 1}: {e}", exc_info=True)
                continue

        logger.warning(f"No product found with name containing '{product_name}'")
        return False

    except PlaywrightTimeoutError:
        logger.error("Timeout waiting for product items to load")
        return False
    except Exception as e:
        logger.error(f"Error finding product: {e}", exc_info=True)
        return False


def find_and_click_checkout_button(page: Page, retry_interval_ms: int = 500, timeout_seconds: int = 30) -> bool:
    """
    Find and click the checkout button at the bottom of the product page.
    Retries until the button is enabled or timeout is reached.

    Args:
        page: Playwright page object
        retry_interval_ms: Time to wait between retries in milliseconds (default: 500)
        timeout_seconds: Maximum time to wait for button to become enabled (default: 30)

    Returns:
        True if the button was found and clicked, False otherwise
    """
    try:
        logger.info("Looking for checkout button at the bottom of the page...")

        # Calculate timeout
        max_attempts = (timeout_seconds * 1000) // retry_interval_ms
        attempts = 0

        while attempts < max_attempts:
            try:
                # Find the large button at the bottom - it has specific size class
                checkout_buttons = page.query_selector_all('button.c-bYwOQu.c-bYwOQu-dWXYMB-size-large')

                if checkout_buttons:
                    for idx, button in enumerate(checkout_buttons):
                        # Get button text
                        button_text_elements = button.query_selector_all('p.c-PJLV')
                        button_texts = [elem.inner_text() for elem in button_text_elements]
                        button_text = " | ".join(button_texts)

                        # Check if button is disabled
                        is_disabled = button.is_disabled()

                        logger.info(f"Checkout button #{idx + 1}: '{button_text}' - Disabled: {is_disabled}")

                        # If button is enabled, click it!
                        if not is_disabled:
                            logger.info(f"✓ Found enabled checkout button! Text: '{button_text}'")
                            logger.info("Clicking checkout button...")
                            button.scroll_into_view_if_needed()
                            page.wait_for_timeout(300)
                            button.click(force=True)
                            logger.info("🎉 Successfully clicked checkout button!")
                            return True
                        else:
                            if attempts == 0:
                                logger.info(f"Button is disabled (likely 'Sold Out'), will retry every {retry_interval_ms}ms...")

                # Wait before next attempt
                attempts += 1
                if attempts < max_attempts:
                    page.wait_for_timeout(retry_interval_ms)

            except Exception as e:
                logger.debug(f"Error checking button on attempt {attempts + 1}: {e}")
                attempts += 1
                page.wait_for_timeout(retry_interval_ms)

        logger.warning(f"Checkout button did not become enabled after {timeout_seconds} seconds")
        return False

    except Exception as e:
        logger.error(f"Error finding checkout button: {e}", exc_info=True)
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

            # Step 1: Find and click the drop card with "Thurs - Sun" in the title
            clicked_drop = find_and_click_drop_card(page, title_search="Thurs - Sun")

            if clicked_drop:
                logger.info("🎉 SUCCESS: Drop card clicked!")
                logger.info("Waiting for product page to load...")
                page.wait_for_timeout(3000)

                # Step 2: Find and click the product
                clicked_product = find_and_click_product(page, product_name="Small Pastry Box")

                if clicked_product:
                    logger.info("🎉 SUCCESS: Product clicked!")
                    logger.info("Waiting for product details to load...")
                    page.wait_for_timeout(2000)

                    # Step 3: Find and click the checkout button
                    clicked_checkout = find_and_click_checkout_button(
                        page,
                        retry_interval_ms=config['retry_interval_ms'],
                        timeout_seconds=config['timeout_seconds']
                    )

                    if clicked_checkout:
                        logger.info("🎉 SUCCESS: Checkout button clicked!")
                        logger.info("Waiting to see checkout result...")
                        page.wait_for_timeout(3000)
                    else:
                        logger.warning("⏳ Checkout button not found or did not become enabled")
                else:
                    logger.warning("⏳ Product not found or could not be clicked")
            else:
                logger.info("⏳ Drop card not found or could not be clicked")

            # Keep browser open for a moment so user can see the result
            if not config['headless']:
                logger.info("Browser will remain open for 10 seconds for inspection...")
                page.wait_for_timeout(10000)

        except Exception as e:
            logger.error(f"Error during bot execution: {e}", exc_info=True)

        finally:
            browser.close()
            logger.info("Browser closed")


if __name__ == "__main__":
    run_bot()
