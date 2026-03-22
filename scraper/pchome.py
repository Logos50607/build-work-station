"""
PChome 24h 搜尋 API 封裝
純函式，不含 I/O 以外的副作用
"""

import urllib.request
import urllib.parse
import json

BASE_URL = "https://ecshweb.pchome.com.tw/search/v3.3/all/results"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "Accept": "application/json",
}


def fetch_raw(keyword: str, size: int = 10) -> dict:
    """呼叫 PChome API，回傳原始 JSON dict"""
    params = urllib.parse.urlencode({"q": keyword, "page": 1, "sort": "rnk", "size": size})
    req = urllib.request.Request(f"{BASE_URL}?{params}", headers=HEADERS)
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read())


def parse_products(raw: dict) -> list[dict]:
    """從原始回應萃取標準化產品清單"""
    return [
        {
            "name": p.get("name", ""),
            "price": p.get("price", 0),
            "origin_price": p.get("originPrice", 0),
            "url": f"https://24h.pchome.com.tw/prod/{p.get('Id', '')}",
            "source": "PChome",
        }
        for p in raw.get("prods", [])
        if p.get("price", 0) > 0
    ]


def search(keyword: str, size: int = 10, **_) -> list[dict]:
    """搜尋並回傳標準化產品清單"""
    try:
        raw = fetch_raw(keyword, size)
        return parse_products(raw)
    except Exception as e:
        print(f"  [PChome] 搜尋「{keyword}」失敗：{e}")
        return []
