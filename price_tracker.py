import requests
from lxml import html
import os

def get_price():
    API_KEY = os.getenv('SCRAPERAPI_KEY')
    PRODUCT_URL = "https://www.flipkart.com/apple-2024-ipad-air-m2-128-gb-rom-11-0-inch-wi-fi-only-space-grey/p/itm34f4230179cfd"
    scraperapi_url = f'http://api.scraperapi.com/?api_key={API_KEY}&url={PRODUCT_URL}'
    response = requests.get(scraperapi_url)

    tree = html.fromstring(response.content)

    xpath = "//div[contains(@class, 'Nx9bqj') and contains(@class, 'CxhGGd')]/text()"
    price_elements = tree.xpath(xpath)

    if price_elements:
        price_text = price_elements[0].strip()
        price = int(price_text.replace("₹", "").replace(",", ""))
        return price
    return None

def main():
    current_price = get_price()
    if current_price is None:
        print("❌ Could not retrieve price")
        return

    # Load last known price from file
    last_price = None
    if os.path.exists("last_price.txt"):
        with open("last_price.txt", "r") as f:
            try:
                last_price = int(f.read().strip())
            except ValueError:
                pass

    if last_price is not None and current_price >= last_price:
        print(f"ℹ️ Price is ₹{current_price} — no drop.")
        return

    print(f"📉 Price dropped! New price: ₹{current_price}")

    # Send Telegram message
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if bot_token and chat_id:
        message = f"📱 Flipkart Price Drop Alert!\nNew Price: ₹{current_price}"
        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(telegram_url, data={"chat_id": chat_id, "text": message})

    # Save new price to file
    with open("last_price.txt", "w") as f:
        f.write(str(current_price))

if __name__ == "__main__":
    main()
