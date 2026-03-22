#!/bin/sh
# 執行比價爬蟲（PChome + 原價屋），輸出 report.md
set -e
cd "$(dirname "$0")"

# 確認 Playwright 瀏覽器已安裝
python3 -m playwright install chromium --with-deps 2>/dev/null || true

python3 report.py "${1:-report.md}"
