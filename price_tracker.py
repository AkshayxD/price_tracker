import requests
from lxml import html
import os
import json
import time

def get_price(product):
    API_KEY = os.getenv("SCRAPERAPI_KEY")
    scraperapi_url = f"http://api.scraperapi.com/?api_key={API_KEY}&url={product['url']}"

    try:
        response = requests.get(scraperapi_url, timeout=20)
        print(f"\n🔍 {product['name']} — Status Code: {response.status_code}")

        if response.status_code != 200:
            return None

        tree = html.fromstring(response.content)

        if product["site"] == "flipkart":
            xpath = "//div[contains(@class, 'Nx9bqj') and contains(@class, 'CxhGGd')]/text()"
        elif product["site"] == "amazon":
            xpath = "//span[@id='priceblock_ourprice' or @id='priceblock_dealprice']/text()"
        else:
            return None

        price_elements = tree.xpath(xpath)
        if price_elements:
            price_text = price_elements[0].strip()
            price = int(price_text.replace("\u20B9", "").replace(",", ""))
            return price

    except Exception as e:
        print(f"⚠️ Error: {e}")
    return None

def send_telegram_message(message):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if bot_token and chat_id:
        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(telegram_url, data={"chat_id": chat_id, "text": message})

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    products = load_json("products.json")
    last_prices = load_json("last_prices.json")
    updated = False

    for product in products:
        current_price = get_price(product)
        time.sleep(2)  # To avoid hitting rate limits

        if current_price is None:
            msg = f"❌ Could not load product: {product['name']}\n{product['url']}"
            print(msg)
            send_telegram_message(msg)
            continue

        last_price = last_prices.get(product['url'])

        if (last_price is None) or (current_price < last_price):
            msg = f"📉 Price Drop Alert for {product['name']}\nNew Price: ₹{current_price}\n{product['url']}"
            print(msg)
            send_telegram_message(msg)
            last_prices[product['url']] = current_price
            updated = True
        else:
            print(f"ℹ️ No drop for {product['name']} (₹{current_price})")

    if updated:
        save_json("last_prices.json", last_prices)

if __name__ == "__main__":
    main()
