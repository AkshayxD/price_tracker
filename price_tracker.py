from utils import json, telegram, amazon, flipkart, myntra

PRODUCTS_FILE = "assets/products.json"
LAST_PRICES_FILE = "last_prices.json"

def main():
    products = json.load_json(PRODUCTS_FILE)
    last_prices = json.load_json(LAST_PRICES_FILE)

    for product in products:
        name = product["name"]

        if 'amazon' in product['name'].lower():
            current_price, error = amazon.get_price(product)
        elif 'flipkart' in product['name'].lower():
            current_price, error = flipkart.get_price(product)
        elif 'myntra' in product['name'].lower():
            current_price, error = myntra.get_price(product)
        else:
            print("⚠️ Website name not present in product['name']")
            telegram.send_telegram_message(f"⚠️ Website name not present in product['name']\n{name}")
            return None
        
        if current_price is None:
            telegram.send_telegram_message(f"⚠️ Could not fetch price\n{name}\nReason: {error}")
            continue

        lowest_price = last_prices.get(name)

        if lowest_price is None:
            # First time tracking → treat as lowest
            telegram.send_telegram_message(f"💡 New Product Added: {name}\nCurrent Price: ₹{current_price}")
            last_prices[name] = current_price

        elif current_price < lowest_price:
            # Found a new lowest price → update
            drop_percent = int(((lowest_price - current_price) / lowest_price) * 100)
            telegram.send_telegram_message(
                f"✅⬇️ New Lowest Price for {name}!\n"
                f"New Price: ₹{current_price}\n"
                f"Previous Lowest: ₹{lowest_price}\n"
                f"That's {drop_percent}% lower than before!"
            )
            last_prices[name] = current_price  # update to new lowest

        else:
            # Price is same or higher than lowest → do nothing
            increase_percent = int(((current_price - lowest_price) / lowest_price) * 100)
            telegram.send_telegram_message(
                f"✅⬇️ Price for {name}\n"
                f"New Price: ₹{current_price}\n"
                f"Previous Lowest: ₹{lowest_price}\n"
                f"That's {increase_percent}% more than before"
            )

    # Save only lowest prices
    json.save_json(last_prices, LAST_PRICES_FILE)


if __name__ == "__main__":
    main()
