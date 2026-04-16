import os
import requests
from datetime import datetime, timedelta, timezone
# 💡 改為匯入 FuturesClient
from fugle_marketdata import FuturesClient 

# --- 設定區 ---
FUGLE_API_KEY = os.getenv('FUGLE_API_KEY')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
# 台指期近全代碼 (WTX& 代表台指期近月全天盤)
TARGET_SYMBOL = "WTX&" 
PRICE_FILE = "last_f_price.txt"

def get_taiwan_time():
    """取得台灣時區時間"""
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

def main():
    if not FUGLE_API_KEY or not DISCORD_WEBHOOK_URL:
        print("❌ 錯誤：環境變數 FUGLE_API_KEY 或 DISCORD_WEBHOOK 遺失")
        return

    # 💡 初始化專用的期貨 Client
    client = FuturesClient(api_key=FUGLE_API_KEY)
    
    try:
        # 💡 在 FuturesClient 中，直接使用 .intraday.quote
        snapshot = client.intraday.quote(symbol=TARGET_SYMBOL)
        
        # 嘗試取得最新成交價，若無則取收盤價
        current_price = snapshot.get('lastPrice') or snapshot.get('close')
        
        if current_price is None:
            print(f"[{get_taiwan_time()}] 暫無 {TARGET_SYMBOL} 成交資料 (可能非交易時段)")
            return

        # 讀取快取中的上一次價格
        last_price = None
        if os.path.exists(PRICE_FILE):
            with open(PRICE_FILE, "r") as f:
                try:
                    content = f.read().strip()
                    if content:
                        last_price = float(content)
                except ValueError:
                    last_price = None

        print(f"[{get_taiwan_time()}] 目前價格: {current_price}, 前次價格: {last_price}")

        # 計算與判斷漲跌幅
        if last_price and last_price > 0:
            change_percent = ((current_price - last_price) / last_price) * 100
            
            # 判斷門檻：1%
            if abs(change_percent) >= 1.0:
                direction = "🚀 期指急拉" if change_percent > 0 else "📉 期指急殺"
                payload = {
                    "username": "台指期監控",
                    "embeds": [{
                        "title": f"{direction}: {TARGET_SYMBOL}",
                        "color": 16711680 if change_percent > 0 else 65280,
                        "fields": [
                            {"name": "目前價格", "value": f"**{current_price}**", "inline": True},
                            {"name": "一分鐘漲跌", "value": f"`{change_percent:.2f}%`", "inline": True},
                            {"name": "偵測時間", "value": get_taiwan_time(), "inline": False}
                        ],
                        "footer": {"text": "GitHub Actions 自動監控"}
                    }]
                }
                requests.post(DISCORD_WEBHOOK_URL, json=payload)
                print(f"✅ 已發送 Discord 通知，變動幅度: {change_percent:.2f}%")

        # 更新快取檔案
        with open(PRICE_FILE, "w") as f:
            f.write(str(current_price))

    except Exception as e:
        print(f"⚠️ API 執行異常: {e}")

if __name__ == "__main__":
    main()
