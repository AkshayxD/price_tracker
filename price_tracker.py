from utils import json, price_fetch, telegram

PRODUCTS_FILE = "assets/products.json"
LAST_PRICES_FILE = "last_prices.json"

def main():
    products = json.load_json(PRODUCTS_FILE)
    last_prices = json.load_json(LAST_PRICES_FILE)

    for product in products:
        current_price = price_fetch.get_price(product)
        name = product["name"]

        if current_price is None:
            telegram.send_telegram_message(f"⚠️ Could not fetch price for the product: {name}")
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
            print(f"ℹ️ {name} is ₹{current_price} (Lowest Ever: ₹{lowest_price})")

    # Save only lowest prices
    json.save_json(last_prices, LAST_PRICES_FILE)


if __name__ == "__main__":
    main()
