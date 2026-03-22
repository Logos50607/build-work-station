"""
原價屋 (coolpc.com.tw) 比價爬蟲
產品資料直接從 evaluate.php 的 <select> option text 解析，不需進入 iframe
"""

import re
from browser import new_page

PAGE_URL = "https://www.coolpc.com.tw/evaluate.php"

# 採購品類 → select name 對照表
CATEGORY_SELECT = {
    "Mini PC": "n1",     # 品牌小主機、AIO
    "5G CPE":  "n19",    # IP分享器｜網卡｜網通設備
    "UPS":     "n26",    # UPS不斷電
}

_cached_options: dict[str, list[dict]] = {}


def _load_all(page) -> dict[str, list[dict]]:
    """一次性載入所有目標 select 的 options"""
    result = page.evaluate(f"""() => {{
        const targets = {list(CATEGORY_SELECT.values())};
        const out = {{}};
        for (const name of targets) {{
            const sel = document.querySelector(`select[name="${{name}}"]`);
            if (!sel) {{ out[name] = []; continue; }}
            out[name] = [...sel.options].slice(1).map(o => o.text.trim()).filter(t => t.includes('$'));
        }}
        return out;
    }}""")
    return result


def _parse_option(text: str) -> dict | None:
    """從 option text 解析產品名稱和價格
    格式：產品名稱, $價格 ◆ ★ 熱賣
    """
    m = re.search(r',\s*\$(\d[\d,]*)', text)
    if not m:
        return None
    price = int(m.group(1).replace(',', ''))
    name = text[:m.start()].strip()
    if not name:
        return None
    return {
        "name": name,
        "price": price,
        "origin_price": price,
        "url": PAGE_URL,
        "source": "原價屋",
    }


def _get_options(select_name: str) -> list[str]:
    """取得（快取）指定 select 的 option texts"""
    if not _cached_options:
        try:
            with new_page() as page:
                page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(1500)
                data = _load_all(page)
                _cached_options.update(data)
        except Exception as e:
            print(f"  [原價屋] 頁面載入失敗：{e}")
    return _cached_options.get(select_name, [])


def search(keyword: str, size: int = 10, **_) -> list[dict]:
    """搜尋原價屋，回傳標準化產品清單
    比對邏輯：keyword 的每個 token 都必須出現在 option text 中
    """
    select_name = _infer_select(keyword)
    if not select_name:
        return []

    tokens = [t.lower() for t in keyword.split() if len(t) > 1]
    results = []
    for text in _get_options(select_name):
        text_lower = text.lower()
        if all(t in text_lower for t in tokens):
            item = _parse_option(text)
            if item:
                results.append(item)
                if len(results) >= size:
                    break
    return results


def search_by_category(category: str, size: int = 20) -> list[dict]:
    """直接取得整個類別的所有產品"""
    select_name = CATEGORY_SELECT.get(category)
    if not select_name:
        return []
    results = []
    for text in _get_options(select_name):
        item = _parse_option(text)
        if item:
            results.append(item)
            if len(results) >= size:
                break
    return results


def _infer_select(keyword: str) -> str | None:
    """從關鍵字推斷要查的 select"""
    kw = keyword.lower()
    if any(k in kw for k in ["ups", "apc", "cyberpower", "不斷電"]):
        return CATEGORY_SELECT["UPS"]
    if any(k in kw for k in ["5g", "cpe", "sim", "deco", "nr5103", "router", "路由"]):
        return CATEGORY_SELECT["5G CPE"]
    if any(k in kw for k in ["rtx", "gpu", "主機", "gtx"]):
        return CATEGORY_SELECT["GPU 主機"]
    return None
