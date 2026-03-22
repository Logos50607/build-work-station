"""
採購清單設定
每個類別可設多個搜尋關鍵字，取最低價前 N 筆
"""

PRODUCTS = {
    "Mini PC": [
        "NUC 主機",
        "CUBI 主機",
        "BRIX 主機",
        "迷你主機 i5",
    ],
    "5G CPE": [
        "Deco X50-5G",
        "NR5103",
        "5G CPE 路由器",
        "4G LTE 分享器",
        "Archer MR",
        "LTE CPE",
    ],
    "UPS": [
        "APC Back-UPS",
        "CyberPower UPS",
    ],
}

TOP_N = 5          # 每個關鍵字取幾筆
MAX_PRICE = {      # 各類別價格上限（0 = 不過濾）
    "Mini PC": 45000,
    "5G CPE":   10000,
    "UPS":       6000,
}
MIN_PRICE = {      # 各類別價格下限，濾掉配件
    "Mini PC": 8000,
    "5G CPE":    3000,
    "UPS":       1000,
}
EXCLUDE_KEYWORDS = {   # 品名包含這些字就排除
    "Mini PC": ["顯示卡", "散熱器", "主機板", "記憶體", "電源", "機殼", "充電", "AIO", "一體機"],
    "5G CPE":   ["冰箱", "洗衣機", "電視", "音響"],
    "UPS":      ["管理卡", "RCCARD", "電池", "背板"],
}
