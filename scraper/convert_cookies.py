"""
將瀏覽器 Cookie Editor 匯出的 TSV 格式轉成 Playwright JSON
用法：python3 convert_cookies.py < cookies.tsv
"""

import sys, json
from datetime import datetime, timezone

def parse_expires(s: str) -> float:
    if not s or s.strip() == "Session":
        return -1.0
    try:
        dt = datetime.fromisoformat(s.rstrip("Z")).replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except Exception:
        return -1.0

def parse_bool(s: str) -> bool:
    return s.strip() == "✓"

cookies = []
for line in sys.stdin:
    line = line.rstrip("\n")
    if not line.strip():
        continue
    cols = line.split("\t")
    if len(cols) < 6:
        continue
    name     = cols[0].strip()
    value    = cols[1].strip()
    domain   = cols[2].strip()
    path     = cols[3].strip() or "/"
    expires  = parse_expires(cols[4].strip() if len(cols) > 4 else "")
    http_only = parse_bool(cols[6]) if len(cols) > 6 else False
    secure    = parse_bool(cols[7]) if len(cols) > 7 else False
    same_site_raw = cols[8].strip() if len(cols) > 8 else ""
    same_site = same_site_raw if same_site_raw in ("Strict", "Lax", "None") else "Lax"

    if not name or not domain:
        continue

    cookies.append({
        "name": name,
        "value": value,
        "domain": domain,
        "path": path,
        "expires": expires,
        "httpOnly": http_only,
        "secure": secure,
        "sameSite": same_site,
    })

out = "shopee_session.json"
with open(out, "w") as f:
    json.dump(cookies, f, ensure_ascii=False, indent=2)
print(f"儲存 {len(cookies)} 個 cookie → {out}")
