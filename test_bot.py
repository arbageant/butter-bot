"""
Test suite for Butter & Crumble Bot
"""

import pytest
from playwright.sync_api import Page, expect


def test_hotplate_loads(page: Page) -> None:
    """Test that the Hotplate Butter & Crumble page loads successfully."""
    page.goto("https://www.hotplate.com/butterandcrumble")

    # Wait for page to load
    page.wait_for_load_state("networkidle")

    # Check that we're on the right page
    assert "butterandcrumble" in page.url.lower()


def test_page_has_content(page: Page) -> None:
    """Test that the page has expected content."""
    page.goto("https://www.hotplate.com/butterandcrumble")
    page.wait_for_load_state("networkidle")

    # The page should have some content
    body_text = page.inner_text("body")
    assert len(body_text) > 0


@pytest.mark.skip(reason="Requires actual Order button to be present on page")
def test_order_button_exists(page: Page) -> None:
    """Test that an order button can be found."""
    page.goto("https://www.hotplate.com/butterandcrumble")
    page.wait_for_load_state("networkidle")

    # This will need to be updated with the actual selector
    order_button = page.locator('button:has-text("Order")')
    expect(order_button).to_be_visible()
