import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import time

load_dotenv()
coins_data = Path("coins_data.json")


def get_data():
    url = "https://openapiv1.coinstats.app/coins?limit=100"
    API_KEY = os.getenv("API_KEY")

    headers  = {
        "X-API-KEY" : API_KEY
    }

    response = requests.get(url, headers= headers)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("API Error")

def save_data(data):
    cleaned_data = []

    for coin in data['result']:
        coin_info = {
            "Name" : coin['id'],
            "Symbol" : coin['symbol'],
            "Rank" : coin['rank'],
            "Price" : round(coin['price'], 3),
            "Change 1H" : coin['priceChange1h'],
            "Change 1D" : coin['priceChange1d'],
            "Change 1W" : coin['priceChange1w']
        }
        cleaned_data.append(coin_info)

    with open (coins_data, 'w') as f:
        json.dump(cleaned_data, f, indent=4)

def load_data(coins_data):
    if not coins_data.exists():
        return []
    
    try:
        with open(coins_data, 'r') as f:
            data = json.load(f)
            return data
    except json.JSONDecodeError:
        return []

def send_telegram(message):
    
    Token = os.getenv("Telegram_Api")
    Chat_id = os.getenv("CHAT_ID")

    url = f"https://api.telegram.org/bot{Token}/sendMessage"

    data = {
        "chat_id": Chat_id,
        "text" : message
    }

    try:
        requests.post(url, data=data, timeout=5)
    except requests.exceptions.Timeout:
        print("The Request Timed OUT...")

def caluclate_change():
    change_result = []

    old_data = load_data(coins_data)
    new_data = get_data()

    for coins in new_data['result']:
        new_symbol = coins['symbol']
        new_Price = coins['price']

        for coin in old_data:
            old_Symbol = coin["Symbol"]
            old_price = coin["Price"]

            if new_symbol == old_Symbol:
                try:
                    calculate = round(((new_Price - old_price) / old_price) * 100, 2)
                    new_data = {
                        "Symbol" : new_symbol,
                        "Change" : calculate
                    }
                    change_result.append(new_data)  
                    
                except ZeroDivisionError:
                    pass
                break

    with open("result.json", 'w') as f:
        json.dump(change_result, f , indent=4)
    
    return change_result

def check_alerts(change_result):

    for coin in change_result:

        name = coin['Symbol']

        if coin['Change'] >= 2:
            send_telegram(f"🚀 {name} +{coin['Change']}%")
        elif coin['Change'] <= -2:
            send_telegram(f"⚠️  {name} {coin['Change']}%")


# data = get_data()
# save_data(data)

# print(caluclate_change())
data2 = caluclate_change()
while True:
    check_alerts(data2)
    time.sleep(5 * 60)

