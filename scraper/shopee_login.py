"""
以真實 Google Chrome 開啟蝦皮登入頁，保留 profile 供後續爬蟲使用。
執行：uv run --with playwright python3 shopee_login.py
需要 DISPLAY（ssh -X）
"""

import subprocess, time, urllib.request, os
from pathlib import Path
from playwright.sync_api import sync_playwright

CHROME_PROFILE = Path(__file__).parent / ".chrome_profile"
CDP_PORT = 19222
CDP_URL  = f"http://localhost:{CDP_PORT}"
LOGIN_URL = "https://shopee.tw/buyer/login"


def _is_up():
    try:
        urllib.request.urlopen(f"{CDP_URL}/json/version", timeout=2)
        return True
    except Exception:
        return False


def main():
    CHROME_PROFILE.mkdir(exist_ok=True)
    (CHROME_PROFILE / "Default" / "LOCK").unlink(missing_ok=True)

    display = os.environ.get("DISPLAY", ":0")
    proc = subprocess.Popen(
        ["google-chrome-stable",
         f"--remote-debugging-port={CDP_PORT}",
         f"--user-data-dir={CHROME_PROFILE}",
         "--no-first-run", "--no-default-browser-check",
         LOGIN_URL],
        env={**os.environ, "DISPLAY": display},
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    print("等待 Chrome 啟動...")
    for _ in range(15):
        time.sleep(1)
        if _is_up():
            break
    else:
        raise RuntimeError("Chrome 啟動逾時")

    print("請在瀏覽器視窗完成登入（包含驗證碼）...")
    input("登入完成後，回到這裡按 Enter 關閉瀏覽器...")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0]
        cookies = ctx.cookies()
        spc_u = next((c["value"] for c in cookies if c["name"] == "SPC_U"), None)
        if spc_u and spc_u not in ("0", "-1", ""):
            print(f"確認已登入（SPC_U={spc_u}）")
        else:
            print("警告：未偵測到有效登入 session，請確認是否登入成功")

    proc.terminate()
    print(f"Chrome profile 已保存至：{CHROME_PROFILE}")
    print("後續爬蟲會自動沿用此 profile，不需要重新登入。")


if __name__ == "__main__":
    main()
