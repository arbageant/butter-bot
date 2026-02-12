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


def test_drop_cards_exist(page: Page) -> None:
    """Test that drop cards can be found on the page."""
    page.goto("https://www.hotplate.com/butterandcrumble")
    page.wait_for_load_state("networkidle")

    # Check that drop card containers exist
    drop_cards = page.locator('.c-fixGjY.c-fixGjY-igxtwkj-css')
    expect(drop_cards.first).to_be_visible(timeout=10000)
