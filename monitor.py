import os
import requests
import random
from fugle_marketdata import RestClient

# 讀取環境變數
FUGLE_API_KEY = os.getenv('FUGLE_API_KEY')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')

# 測試用股票清單 (隨機抽 10 檔)
TEST_POOL = [
    "2330", "2317", "2454", "2308", "2881", "2882", "2303", "3711", "2412", "2886",
    "1301", "1303", "2884", "2885", "2002", "2382", "3231", "2357", "2603", "2609"
]

def send_test_to_discord(data_list):
    """將 10 檔股票報價整合成一條訊息發送"""
    fields = []
    for item in data_list:
        fields.append({
            "name": f"股票: {item['symbol']}",
            "value": f"💰 價格: **{item['price']}**",
            "inline": True
        })

    payload = {
        "username": "API 測試助手",
        "embeds": [{
            "title": "🧪 每分鐘隨機股價測試",
            "description": "目前隨機抽選 10 檔股票報價如下：",
            "color": 3447003, # 藍色
            "fields": fields,
            "footer": {"text": "GitHub Actions 測試運行中"}
        }]
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

def main():
    if not FUGLE_API_KEY or not DISCORD_WEBHOOK_URL:
        print("❌ 缺少環境變數")
        return

    client = RestClient(api_key=FUGLE_API_KEY)
    stock = client.stock
    
    # 隨機挑選 10 檔
    selected_symbols = random.sample(TEST_POOL, 10)
    results = []

    print(f"開始抓取: {selected_symbols}")

    for symbol in selected_symbols:
        try:
            snapshot = stock.intraday.quote(symbol=symbol)
            price = snapshot.get('lastPrice') or "無成交"
            results.append({"symbol": symbol, "price": price})
        except Exception as e:
            print(f"抓取 {symbol} 失敗: {e}")

    if results:
        send_test_to_discord(results)
        print("✅ 測試資料已發送至 Discord")

if __name__ == "__main__":
    main()
