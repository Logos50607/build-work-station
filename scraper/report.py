"""
彙整各來源結果並輸出比價報告（Markdown）
"""

import sys
import datetime
import pchome
import coolpc
import shopee
from config import PRODUCTS, TOP_N, MAX_PRICE, MIN_PRICE, EXCLUDE_KEYWORDS

PCHOME_SOURCES = [pchome.search, shopee.search]


def is_valid(item: dict, category: str) -> bool:
    price = item["price"]
    name = item["name"]
    max_p = MAX_PRICE.get(category, 0)
    min_p = MIN_PRICE.get(category, 0)
    excludes = EXCLUDE_KEYWORDS.get(category, [])
    return (
        (not max_p or price <= max_p)
        and (not min_p or price >= min_p)
        and not any(ex in name for ex in excludes)
    )


def collect(category: str, keywords: list[str]) -> list[dict]:
    """彙整所有關鍵字的結果，去重後依價格排序
    - PChome: 走關鍵字搜尋
    - 原價屋: 直接抓整個類別（避免關鍵字格式不符問題）
    """
    seen, results = set(), []

    # PChome + 蝦皮: 關鍵字搜尋
    for kw in keywords:
        print(f"  搜尋：{kw} ...")
        for source in PCHOME_SOURCES:
            for item in source(kw, TOP_N):
                key = (item["source"], item["name"])
                if key not in seen and is_valid(item, category):
                    seen.add(key)
                    results.append(item)

    # 原價屋: 直接取類別全量
    print(f"  原價屋 抓類別：{category} ...")
    for item in coolpc.search_by_category(category, size=TOP_N * 3):
        key = (item["source"], item["name"])
        if key not in seen and is_valid(item, category):
            seen.add(key)
            results.append(item)

    return sorted(results, key=lambda x: x["price"])[:TOP_N * 2]


def render(all_results: dict[str, list[dict]]) -> str:
    date = datetime.date.today().isoformat()
    lines = [f"# 比價報告 {date}\n"]
    for category, items in all_results.items():
        lines.append(f"## {category}\n")
        if not items:
            lines.append("_無結果_\n")
            continue
        lines.append("| 品名 | 售價 | 來源 |")
        lines.append("|------|-----:|------|")
        for item in items:
            name = item["name"][:50].replace("|", "｜")
            price = f"NT$ {item['price']:,}"
            link = f"[{item['source']}]({item['url']})"
            lines.append(f"| {name} | {price} | {link} |")
        lines.append("")
    return "\n".join(lines)


def main(output_file: str = "report.md"):
    all_results = {}
    for category, keywords in PRODUCTS.items():
        print(f"\n[{category}]")
        all_results[category] = collect(category, keywords)

    md = render(all_results)
    with open(output_file, "w") as f:
        f.write(md)
    print(f"\n報告已寫入：{output_file}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "report.md"
    main(out)
