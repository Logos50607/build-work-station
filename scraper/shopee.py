"""
蝦皮 (shopee.tw) 搜尋爬蟲
需先執行 shopee_login.py 取得 session，再呼叫此模組
"""

import json
import urllib.parse
from pathlib import Path
from browser import new_page

COOKIE_FILE = Path(__file__).parent / "shopee_session.json"
SEARCH_API = "https://shopee.tw/api/v4/search/search_items"


def _load_cookies() -> list[dict]:
    if not COOKIE_FILE.exists():
        raise FileNotFoundError("找不到 shopee_session.json，請先執行 shopee_login.py")
    return json.loads(COOKIE_FILE.read_text())


def search(keyword: str, size: int = 10, **_) -> list[dict]:
    try:
        return _fetch(keyword, size)
    except FileNotFoundError as e:
        print(f"  [蝦皮] {e}")
        return []
    except Exception as e:
        print(f"  [蝦皮] 搜尋「{keyword}」失敗：{e}")
        return []


def _fetch(keyword: str, size: int) -> list[dict]:
    cookies = _load_cookies()
    search_url = f"https://shopee.tw/search?keyword={urllib.parse.quote(keyword)}"

    captured = []

    def handle_response(response):
        if "search_items" in response.url and response.status == 200:
            try:
                data = response.json()
                captured.append(data)
            except Exception:
                pass

    with new_page() as page:
        page.context.add_cookies(cookies)
        page.on("response", handle_response)
        page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(4000)   # 等 API 回應載入

    results = []
    for data in captured:
        for entry in (data.get("items") or []):
            item = entry.get("item_basic", {})
            name = item.get("name", "")
            price = item.get("price", 0) // 100000
            shop_id = item.get("shopid", "")
            item_id = item.get("itemid", "")
            url = f"https://shopee.tw/product/{shop_id}/{item_id}"
            if name and price > 0:
                results.append({
                    "name": name,
                    "price": price,
                    "origin_price": item.get("price_before_discount", price) // 100000,
                    "url": url,
                    "source": "蝦皮",
                })
            if len(results) >= size:
                break
    return results
