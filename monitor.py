import os
import requests
from datetime import datetime, timedelta, timezone
# 💡 修改匯入項目，直接使用 FuturesClient
from fugle_marketdata import FuturesClient 

# --- 設定區 ---
FUGLE_API_KEY = os.getenv('FUGLE_API_KEY')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
TARGET_SYMBOL = "WTX&" 
PRICE_FILE = "last_f_price.txt"

def get_taiwan_time():
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime('%H:%M:%S')

def main():
    if not FUGLE_API_KEY or not DISCORD_WEBHOOK_URL:
        print("❌ 錯誤：環境變數讀取失敗")
        return

    # 💡 修正初始化方式
    client = FuturesClient(api_key=FUGLE_API_KEY)
    
    try:
        # 💡 在 FuturesClient 中，路徑通常直接是 .intraday.quote
        snapshot = client.intraday.quote(symbol=TARGET_SYMBOL)
        
        current_price = snapshot.get('lastPrice') or snapshot.get('close')
        
        if current_price is None:
            print(f"[{get_taiwan_time()}] 暫無 {TARGET_SYMBOL} 資料")
            return

        # 讀取快取
        last_price = None
        if os.path.exists(PRICE_FILE):
            with open(PRICE_FILE, "r") as f:
                try:
                    last_price = float(f.read().strip())
                except:
                    last_price = None

        print(f"[{get_taiwan_time()}] 目前: {current_price}, 上次: {last_price}")

        # 邏輯判斷
        if last_price and last_price > 0:
            change_percent = ((current_price - last_price) / last_price) * 100
            
            # 這裡設 1.0% 為門檻
            if abs(change_percent) >= 1.0: 
                direction = "🚀 期指急拉" if change_percent > 0 else "📉 期指急殺"
                payload = {
                    "username": "台指期監控",
                    "content": f"### {direction}: {TARGET_SYMBOL}\n- **目前價格**: `{current_price}`\n- **變動幅度**: `{change_percent:.2f}%`\n- **偵測時間**: `{get_taiwan_time()}`"
                }
                requests.post(DISCORD_WEBHOOK_URL, json=payload)

        # 寫入檔案
        with open(PRICE_FILE, "w") as f:
            f.write(str(current_price))

    except Exception as e:
        print(f"API 執行錯誤: {e}")

if __name__ == "__main__":
    main()
