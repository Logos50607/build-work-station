"""
debug 蝦皮爬蟲：記錄 headful 模式下的網路請求與回應
"""
import json, urllib.parse
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIE_FILE = Path(__file__).parent / "shopee_session.json"
LOG_FILE = Path(__file__).parent / "debug_shopee.log"

cookies = json.loads(COOKIE_FILE.read_text())
csrf = next((c["value"] for c in cookies if c["name"] == "csrftoken"), "")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
keyword = "折疊藍牙鍵盤"

log = []

def on_response(response):
    if "shopee.tw/api" in response.url:
        entry = {"url": response.url[:120], "status": response.status}
        if "search_items" in response.url:
            try:
                data = response.json()
                entry["items"] = len(data.get("items") or [])
                entry["error"] = data.get("error")
                entry["is_login"] = data.get("is_login")
            except Exception as e:
                entry["parse_error"] = str(e)
        log.append(entry)
        LOG_FILE.write_text(json.dumps(log, indent=2, ensure_ascii=False))

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=["--disable-blink-features=AutomationControlled"],
    )
    ctx = browser.new_context(user_agent=UA, locale="zh-TW")
    ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    ctx.add_cookies(cookies)
    ctx.on("response", on_response)

    page = ctx.new_page()
    page.goto(
        f"https://shopee.tw/search?keyword={urllib.parse.quote(keyword)}",
        wait_until="domcontentloaded",
        timeout=20000,
    )
    page.wait_for_timeout(5000)

    final_url = page.url
    log.append({"final_url": final_url})
    LOG_FILE.write_text(json.dumps(log, indent=2, ensure_ascii=False))
    browser.close()

print(f"debug log 已寫入：{LOG_FILE}")
print(f"final url: {final_url}")
