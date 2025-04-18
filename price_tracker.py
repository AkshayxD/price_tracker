import os
import json
import requests
from lxml import html

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SCRAPERAPI_KEY = os.getenv("SCRAPERAPI_KEY")

PRODUCTS_FILE = "products.json"
LAST_PRICES_FILE = "last_prices.json"

AMAZON_XPATH = "//div[contains(@id, 'corePriceDisplay_desktop_feature_div')]//span[contains(@class, 'a-price-whole')]/text()"
FLIPKART_XPATH = "//div[contains(@class, 'Nx9bqj') and contains(@class, 'CxhGGd')]/text()"


def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Missing Telegram credentials")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})


def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}


def save_json(data, filepath):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def get_price(product):
    url = f"http://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}&url={product['url']}"
    try:
        response = requests.get(url)
        print(f"🔍 {product['name']} — Status Code: {response.status_code}")
        if response.status_code != 200:
            raise Exception("Non-200 response")

        tree = html.fromstring(response.content)

        if 'amazon' in product['name'].lower():
            rqd_xpath = AMAZON_XPATH
        elif 'flipkart' in product['name'].lower():
            rqd_xpath = FLIPKART_XPATH
        else:
            print("⚠️ Website name not present in product['name']")
            return None

        price_elements = tree.xpath(rqd_xpath)
        if price_elements:
            price_text = price_elements[0].strip()
            return int(price_text.replace("₹", "").replace(",", ""))
    except Exception as e:
        print(f"❌ Failed to scrape {product['name']}: {e}")
    return None


def main():
    products = load_json(PRODUCTS_FILE)
    last_prices = load_json(LAST_PRICES_FILE)

    for product in products:
        current_price = get_price(product)
        name = product["name"]

        if current_price is None:
            send_telegram_message(f"⚠️ Could not fetch price for the product: {name}")
            continue

        last_price = last_prices.get(name)
        if last_price is None:
            send_telegram_message(f"💡 New Product Added: {name}\nPrice: ₹{current_price}")
        elif current_price < last_price:
            drop_percent = int(((last_price - current_price) / last_price) * 100)
            send_telegram_message(
                f"✅⬇️ Price Drop Alert: {name}\nNew Price: ₹{current_price}\nOld Price: ₹{last_price}\nThat's a {drop_percent}% price decrease!"
            )
            last_prices[name] = current_price  # Save only if price dropped
        elif current_price > last_price:
            send_telegram_message(
                f"❌🔺 Price Increase Alert: {name}\nNew Price: ₹{current_price}\nOld Price: ₹{last_price}"
            )
        else:
            print(f"⚠️ No Price Change: {name} — ₹{current_price}")

    save_json(last_prices, LAST_PRICES_FILE)


if __name__ == "__main__":
    main()
