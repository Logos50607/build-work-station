"""
共用 Playwright browser context
"""

from contextlib import contextmanager
from playwright.sync_api import sync_playwright, Page

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36"


@contextmanager
def new_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        ctx = browser.new_context(user_agent=UA, locale="zh-TW")
        page = ctx.new_page()
        try:
            yield page
        finally:
            browser.close()
