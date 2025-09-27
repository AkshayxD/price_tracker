import os, requests
from lxml import html
from config import sizes

SCRAPERAPI_KEY = os.getenv("SCRAPERAPI_KEY")

MAIN_PRICE_XPATH = "//*[@id='mountRoot']/div/div[1]/main/div[2]/div[2]/div[1]/div/p[1]/span[1]/strong"
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
        main_price_xpath = MAIN_PRICE_XPATH
        available_sizes_xpath = AVAILABLE_SIZES_XPATH
        out_of_stock_xpath = OUT_OF_STOCK_XPATH
        required_sizes = sizes.REQUIRED_SHOE_SIZES + sizes.REQUIRED_T_SHIRT_SIZES + sizes.REQUIRED_PANT_SIZES

        main_price_elements = tree.xpath(main_price_xpath)
        print(f"Main Price Element: {main_price_elements}")
        if main_price_elements:
            main_price = main_price_elements[0].strip()

        available_sizes_elements = tree.xpath(available_sizes_xpath)
        print(f"Available Sizes Element: {available_sizes_elements}")
        if available_sizes_elements:
            available_sizes = available_sizes_elements[0].strip()

        out_of_stock_elements = tree.xpath(out_of_stock_xpath)
        print(f"Out of Stock Element: {out_of_stock_elements}")
        if out_of_stock_elements and out_of_stock_elements[0].strip().lower() == 'out of stock':
            print("Out of Stock")
            return None, 'Out of Stock'
        elif (available_sizes_elements and (available_sizes not in required_sizes)):
            print("Required Size not available")
            return None, 'Required Size not available'
        else:
            return int(main_price.replace("₹", "").replace(",", ""))
    except Exception as e:
        print(f"❌ Failed to scrape {product['name']}: {e}")
    return None