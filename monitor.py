import os
import requests
import json
from datetime import datetime, timedelta, timezone
from fugle_marketdata import RestClient

# --- 設定區 ---
FUGLE_API_KEY = os.getenv('FUGLE_API_KEY')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
TARGET_SYMBOL = "2330"
PRICE_FILE = "last_price.txt"

def get_taiwan_time():
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

def send_discord_alert(symbol, old_price, new_price, change_percent):
    """發送漲幅警告"""
    tw_time = get_taiwan_time()
    payload = {
        "username": "波動監控助手",
        "embeds": [{
            "title": f"⚠️ 急速波動警告：{symbol}",
            "color": 16711680, # 亮紅色
            "fields": [
                {"name": "前次價格", "value": f"{old_price}", "inline": True},
                {"name": "目前價格", "value": f"**{new_price}**", "inline": True},
                {"name": "一分鐘漲幅", "value": f"🚀 {change_percent:.2f}%", "inline": False},
                {"name": "偵測時間", "value": tw_time, "inline": False}
            ]
        }]
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

def main():
    client = RestClient(api_key=FUGLE_API_KEY)
    try:
        # 1. 抓取目前價格
        snapshot = client.stock.intraday.quote(symbol=TARGET_SYMBOL)
        current_price = snapshot.get('lastPrice') or snapshot.get('close')
        
        if not current_price:
            print("無法取得價格，跳過。")
            return

        # 2. 讀取上次儲存的價格
        last_price = None
        if os.path.exists(PRICE_FILE):
            with open(PRICE_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    last_price = float(content)

        # 3. 計算與判斷
        if last_price:
            change_percent = ((current_price - last_price) / last_price) * 100
            print(f"上次: {last_price}, 這次: {current_price}, 漲幅: {change_percent:.2f}%")
            
            if change_percent >= 1.0: # 漲幅超過 1%
                send_discord_alert(TARGET_SYMBOL, last_price, current_price, change_percent)

        # 4. 儲存這次價格供下一分鐘使用
        with open(PRICE_FILE, "w") as f:
            f.write(str(current_price))

    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    main()
