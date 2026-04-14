import os
import requests
import random
from fugle_marketdata import RestClient

FUGLE_API_KEY = os.getenv('FUGLE_API_KEY')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')

def main():
    print(f"DEBUG: 檢查環境變數...")
    print(f"API Key 是否存在: {'Yes' if FUGLE_API_KEY else 'No'}")
    print(f"Webhook URL 是否存在: {'Yes' if DISCORD_WEBHOOK_URL else 'No'}")

    if not FUGLE_API_KEY or not DISCORD_WEBHOOK_URL:
        return

    client = RestClient(api_key=FUGLE_API_KEY)
    stock = client.stock
    
    # 測試抓取台積電 (2330)
    try:
        print("DEBUG: 正在呼叫富果 API...")
        snapshot = stock.intraday.quote(symbol="2330")
        print(f"DEBUG: API 原始回傳內容: {snapshot}")
        
        price = snapshot.get('lastPrice')
        print(f"DEBUG: 解析出的價格: {price}")

        # 嘗試發送一則簡單的測試訊息，不判斷價格
        test_payload = {"content": f"🛠️ API 測試連線成功！台積電現價: {price}"}
        resp = requests.post(DISCORD_WEBHOOK_URL, json=test_payload)
        print(f"DEBUG: Webhook 回傳狀態碼: {resp.status_code}")

    except Exception as e:
        print(f"❌ 發生異常: {str(e)}")

if __name__ == "__main__":
    main()
