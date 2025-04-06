import requests
from lxml import html
import os

def get_price():
    URL = "https://www.flipkart.com/apple-2024-ipad-air-m2-128-gb-rom-11-0-inch-wi-fi-only-space-grey/p/itm34f4230179cfd"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(URL, headers=HEADERS)
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

    # Load the last known price (from env or a file)
    last_price = os.getenv("LAST_PRICE")
    if last_price and (current_price >= int(last_price)):
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

if __name__ == "__main__":
    main()
