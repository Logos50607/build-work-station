"""
開啟有頭瀏覽器讓使用者手動登入蝦皮，儲存 session cookie 供爬蟲使用
執行：python3 shopee_login.py
"""

import json
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIE_FILE = Path(__file__).parent / "shopee_session.json"
LOGIN_URL = "https://shopee.tw/buyer/login"
CHECK_URL = "https://shopee.tw"


def main():
    print("開啟瀏覽器，請在視窗內登入蝦皮（包含簡訊驗證）...")
    print("登入完成後回到這個終端機按 Enter 繼續。")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36",
            locale="zh-TW",
            viewport={"width": 1280, "height": 800},
        )
        page = ctx.new_page()
        page.goto(LOGIN_URL, timeout=20000)

        print("等待登入完成（偵測到跳轉至首頁後自動儲存，最長等 3 分鐘）...")
        # 等 URL 離開 login 頁，代表登入成功
        page.wait_for_url(lambda url: "login" not in url and "shopee.tw" in url, timeout=180000)
        page.wait_for_timeout(2000)  # 讓 cookie 寫入穩定

        cookies = ctx.cookies()
        COOKIE_FILE.write_text(json.dumps(cookies, ensure_ascii=False, indent=2))
        print(f"Session 已儲存至 {COOKIE_FILE}（共 {len(cookies)} 個 cookie）")
        browser.close()


if __name__ == "__main__":
    main()
