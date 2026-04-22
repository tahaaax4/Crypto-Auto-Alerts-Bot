import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import time

load_dotenv()

coins_data = Path("coins_data.json")

# store alerted coins (anti-spam)
alerted_coins = set()

#Get data from API
def get_data():
    url = "https://openapiv1.coinstats.app/coins?limit=100"
    API_KEY = os.getenv("API_KEY")

    headers = {
        "X-API-KEY": API_KEY
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            print("API Error")
            return None
    except requests.exceptions.RequestException:
        print("Network Error")
        return None


def save_data(data):
    cleaned_data = []

    for coin in data['result']:
        coin_info = {
            "Symbol": coin['symbol'],
            "Price": round(coin['price'], 3)
        }
        cleaned_data.append(coin_info)

    with open(coins_data, 'w') as f:
        json.dump(cleaned_data, f, indent=4)


def load_data():
    if not coins_data.exists():
        return []

    try:
        with open(coins_data, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

#Telegram Message Send 
def send_telegram(message):
    TOKEN = os.getenv("Telegram_Api")
    CHAT_ID = os.getenv("CHAT_ID")

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=data, timeout=5)
    except requests.exceptions.RequestException:
        print("Telegram Error")


def calculate_change():
    change_result = []

    old_data = load_data()
    new_data = get_data()

    if not new_data or not old_data:
        return []

    # convert old_data into dictionary for fast lookup
    old_prices = {coin["Symbol"]: coin["Price"] for coin in old_data}

    for coin in new_data['result']:
        symbol = coin['symbol']
        new_price = coin['price']

        if symbol in old_prices:
            old_price = old_prices[symbol]

            if old_price == 0:
                continue

            change = round(((new_price - old_price) / old_price) * 100, 2)

            change_result.append({
                "Symbol": symbol,
                "Change": change
            })

    return change_result

#Alerts
def check_alerts(change_result):
    global alerted_coins

    for coin in change_result:
        name = coin['Symbol']
        change = coin['Change']

        #Pump
        if change >= 2:
            if name not in alerted_coins:
                send_telegram(f"🚀 {name} +{change}%")
                alerted_coins.add(name)

        #Dump
        elif change <= -2:
            if name not in alerted_coins:
                send_telegram(f"⚠️ {name} {change}%")
                alerted_coins.add(name)

        elif -1 < change < 1:
            if name in alerted_coins:
                alerted_coins.remove(name)

#Run Actual Bot
def run_bot():
    print("Bot started...\n")

    #Get new Data
    data = get_data()
    if data:
        save_data(data)

    while True:
        try:
            print("Running cycle...")

            change_result = calculate_change()

            if change_result:
                check_alerts(change_result)

            new_data = get_data()
            if new_data:
                save_data(new_data)

            print("Waiting 5 minutes...\n")
            time.sleep(5 * 60)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)


run_bot()