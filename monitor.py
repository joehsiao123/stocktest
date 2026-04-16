import os
import requests
from datetime import datetime, timedelta, timezone
from fugle_marketdata import RestClient

# --- 設定區 ---
FUGLE_API_KEY = os.getenv('FUGLE_API_KEY')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
# 台指期近全代碼 (WTX 為台指期, & 代表近月全)
TARGET_SYMBOL = "WTX&" 
PRICE_FILE = "last_f_price.txt"

def get_taiwan_time():
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime('%H:%M:%S')

def main():
    if not FUGLE_API_KEY or not DISCORD_WEBHOOK_URL:
        print("缺少環境變數")
        return

    client = RestClient(api_key=FUGLE_API_KEY)
    
    try:
        # 獲取期貨報價 (使用期貨專用的行情介面)
        # 注意：台指期全在非交易時段可能無資料
        snapshot = client.stock.intraday.quote(symbol=TARGET_SYMBOL)
        current_price = snapshot.get('lastPrice') or snapshot.get('close')
        
        if current_price is None:
            print(f"[{get_taiwan_time()}] 暫無 {TARGET_SYMBOL} 成交資料")
            return

        # 讀取快取中的上一次價格
        last_price = None
        if os.path.exists(PRICE_FILE):
            with open(PRICE_FILE, "r") as f:
                try:
                    last_price = float(f.read().strip())
                except:
                    last_price = None

        print(f"[{get_taiwan_time()}] 當前: {current_price}, 上次: {last_price}")

        # 計算漲幅判斷
        if last_price and last_price > 0:
            change_percent = ((current_price - last_price) / last_price) * 100
            
            if abs(change_percent) >= 1.0: # 監控漲跌幅超過 1%
                direction = "🚀 急速噴發" if change_percent > 0 else "📉 急速墜落"
                payload = {
                    "username": "期指波動監控",
                    "embeds": [{
                        "title": f"{direction}: {TARGET_SYMBOL}",
                        "color": 16711680 if change_percent > 0 else 65280,
                        "fields": [
                            {"name": "當前價格", "value": f"**{current_price}**", "inline": True},
                            {"name": "一分鐘變動", "value": f"`{change_percent:.2f}%`", "inline": True},
                            {"name": "偵測時間", "value": get_taiwan_time(), "inline": False}
                        ]
                    }]
                }
                requests.post(DISCORD_WEBHOOK_URL, json=payload)

        # 紀錄本次價格供下回合使用
        with open(PRICE_FILE, "w") as f:
            f.write(str(current_price))

    except Exception as e:
        print(f"API 執行錯誤: {e}")

if __name__ == "__main__":
    main()
