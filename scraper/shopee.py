"""
蝦皮 (shopee.tw) 搜尋爬蟲
需先執行 shopee_login.py 建立 Chrome profile，後續自動沿用。
流程：Chrome 自己開搜尋頁載入結果 → 等待完成 → Playwright 連入讀 DOM
"""

import os, re, subprocess, time, urllib.parse, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

CHROME_PROFILE = Path(__file__).parent / ".chrome_profile"
CDP_PORT = 19223
CDP_URL  = f"http://localhost:{CDP_PORT}"
DISPLAY  = os.environ.get("DISPLAY", ":98")
CHROME   = "/opt/google/chrome/chrome"


def _is_up():
    try:
        urllib.request.urlopen(f"{CDP_URL}/json/version", timeout=2)
        return True
    except Exception:
        return False


def search(keyword: str, size: int = 10, **_) -> list[dict]:
    try:
        return _fetch(keyword, size)
    except Exception as e:
        print(f"  [蝦皮] 搜尋「{keyword}」失敗：{e}")
        return []


def _parse_price(text: str) -> int:
    m = re.search(r"[\d,]+", text.replace(",", ""))
    return int(m.group()) if m else 0


def _fetch(keyword: str, size: int) -> list[dict]:
    if not CHROME_PROFILE.exists():
        raise FileNotFoundError("找不到 Chrome profile，請先執行 shopee_login.py")

    search_url = f"https://shopee.tw/search?keyword={urllib.parse.quote(keyword)}"
    (CHROME_PROFILE / "Default" / "LOCK").unlink(missing_ok=True)

    # Chrome 自己開搜尋頁，不透過 Playwright 導覽（避免 SecureKit 偵測 CDP）
    proc = subprocess.Popen(
        [CHROME,
         f"--remote-debugging-port={CDP_PORT}",
         f"--user-data-dir={CHROME_PROFILE}",
         "--no-first-run", "--no-default-browser-check", "--no-sandbox",
         search_url],
        env={**os.environ, "DISPLAY": DISPLAY},
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    for _ in range(15):
        time.sleep(1)
        if _is_up():
            break
    else:
        proc.terminate()
        raise RuntimeError("Chrome 啟動逾時")

    # 等 Chrome 自己把搜尋結果跑完，再連入
    time.sleep(10)

    results = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(CDP_URL)
            ctx = browser.contexts[0]
            page = next(
                (pg for pg in ctx.pages if "shopee.tw/search" in pg.url),
                ctx.pages[0],
            )

            cards = page.query_selector_all('[data-sqe="item"]')
            for card in cards:
                try:
                    img = card.query_selector("img[alt]")
                    name = img.get_attribute("alt").strip() if img else ""
                    link = card.query_selector("a[href]")
                    href = link.get_attribute("href") if link else ""
                    # 取第一個純數字價格文字（已排除 id/參數）
                    html = card.inner_html()
                    price_match = re.search(r">(\d{1,3}(?:,\d{3})+|\d{4,})<", html)
                    price = int(price_match.group(1).replace(",", "")) if price_match else 0

                    if not name or price <= 0:
                        continue

                    # 從 href 解析 shop_id / item_id
                    id_match = re.search(r"i\.(\d+)\.(\d+)", href)
                    if id_match:
                        shop_id, item_id = id_match.group(1), id_match.group(2)
                        url = f"https://shopee.tw/product/{shop_id}/{item_id}"
                    else:
                        url = f"https://shopee.tw{href.split('?')[0]}"

                    results.append({
                        "name": name,
                        "price": price,
                        "origin_price": price,
                        "url": url,
                        "source": "蝦皮",
                    })
                except Exception:
                    continue

                if len(results) >= size:
                    break
    finally:
        proc.terminate()

    return results
