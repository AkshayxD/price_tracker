import os, requests
from lxml import html
from config import sizes

SCRAPERAPI_KEY = os.getenv("SCRAPERAPI_KEY")

MAIN_PRICE_XPATH = "//*[@id='mountRoot']//span[@class='pdp-price']"
OFFER_PRICE_XPATH = "//*[@id='mountRoot']//span[@class='pdp-offers-price']"
AVAILABLE_SIZES_XPATH = "//*[@id='sizeButtonsContainer']//button[not(contains(@class,'size-buttons-size-button-disabled')) and not(contains(@class,'size-buttons-show-size-chart'))]"
OUT_OF_STOCK_XPATH = "//*[@id='mountRoot']//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'out of stock')]"

def get_price(product):
    url = f"http://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}&url={product['url']}"
    try:
        response = requests.get(url)
        print(f"🔍 {product['name']}")
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            raise Exception(f"Non-200 response: {Exception}")

        tree = html.fromstring(response.content)

        required_sizes = sizes.REQUIRED_SHOE_SIZES + sizes.REQUIRED_T_SHIRT_SIZES + sizes.REQUIRED_PANT_SIZES
        size_available = False

        main_price_elements = tree.xpath(MAIN_PRICE_XPATH)
        print(f"Main Price Elements: {main_price_elements}")
        available_sizes_elements = tree.xpath(AVAILABLE_SIZES_XPATH)
        print(f"Available Sizes Elements: {available_sizes_elements}")
        out_of_stock_elements = tree.xpath(OUT_OF_STOCK_XPATH)
        print(f"Out of Stock Elements: {out_of_stock_elements}")

        if out_of_stock_elements:
            print("Out of Stock")
            return None, "Out of Stock"
        elif available_sizes_elements:
            print("Required Size not available")
            return None, "Required Size not available"
        elif main_price_elements:
            for size in available_sizes_elements:
                if size.strip() in required_sizes:
                    size_available = True
            if size_available:
                main_price = main_price_elements[0].strip()
                return int(main_price.replace("₹", "").replace(",", ""))
            else:
                print("Required Size not available")
                return None, "Required Size not available"
    except Exception as e:
        print(f"❌ Failed to scrape {product['name']}: {e}")
        return None, str(e)
    return None, "Unknown Error"