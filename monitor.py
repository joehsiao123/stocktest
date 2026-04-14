import os
import requests
import json
from fugle_marketdata import RestClient

# 1. 讀取環境變數 (從 GitHub Secrets 傳入)
FUGLE_API_KEY = os.getenv('FUGLE_API_KEY')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')

# 2. 監控設定
TARGET_SYMBOL = "2330"  # 想監控的股票代碼
NOTIFY_PRICE = 1050.0   # 觸發通知的價格

def send_discord_message(symbol, price):
    """發送 Discord 通知"""
    payload = {
        "username": "富果股價助手",
        "embeds": [{
            "title": f"🔔 股價達標通知: {symbol}",
            "color": 15158332,
            "fields": [
                {"name": "當前成交價", "value": f"**{price}**", "inline": True},
                {"name": "設定目標", "value": f">= {NOTIFY_PRICE}", "inline": True}
            ],
            "footer": {"text": "由 GitHub Actions 自動執行"}
        }]
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

def main():
    if not FUGLE_API_KEY or not DISCORD_WEBHOOK_URL:
        print("❌ 錯誤: 缺少環境變數設定")
        return

    try:
        # 3. 呼叫富果 API 獲取即時快照
        client = RestClient(api_key=FUGLE_API_KEY)
        stock = client.stock
        snapshot = stock.intraday.quote(symbol=TARGET_SYMBOL)
        
        current_price = snapshot.get('lastPrice')
        print(f"檢查 {TARGET_SYMBOL}: 目前價格 {current_price}")

        # 4. 判斷邏輯
        if current_price and current_price >= NOTIFY_PRICE:
            send_discord_message(TARGET_SYMBOL, current_price)
            print("✅ 已發送 Discord 通知")
        else:
            print("💡 尚未達標，不發送通知")

    except Exception as e:
        print(f"❌ 執行出錯: {e}")

if __name__ == "__main__":
    main()
