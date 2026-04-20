import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv

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
            "Symbnol" : coin['symbol'],
            "Rank" : coin['rank'],
            "Price" : round(coin['price'], 3),
            "Change 1H" : coin['priceChange1h'],
            "Change 1D" : coin['priceChange1d'],
            "Change 1W" : coin['priceChange1w']
        }
        cleaned_data.append(coin_info)

        with open (coins_data, 'w') as f:
            json.dump(cleaned_data, f, indent=4)

data = get_data()
save_data(data)
