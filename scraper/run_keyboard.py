"""
只跑折疊式藍牙鍵盤比價
"""
import pchome, shopee, coolpc, report
from config import PRODUCTS, TOP_N, MAX_PRICE, MIN_PRICE, EXCLUDE_KEYWORDS

category = "折疊式藍牙鍵盤"
keywords = PRODUCTS[category]
results = report.collect(category, keywords)
md = report.render({category: results})
print(md)

output = "report_keyboard.md"
with open(output, "w") as f:
    f.write(md)
print(f"\n報告已寫入：{output}")
