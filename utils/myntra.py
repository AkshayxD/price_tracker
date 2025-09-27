import os, requests
from lxml import html
from config import sizes

SCRAPERAPI_KEY = os.getenv("SCRAPERAPI_KEY")

MAIN_PRICE_XPATH = "//*[@id='mountRoot']//span[@class='pdp-price']/strong/text()"
OFFER_PRICE_XPATH = "//*[@id='mountRoot']//span[@class='pdp-offers-price']/text()"
AVAILABLE_SIZES_XPATH = "//*[@id='sizeButtonsContainer']//button[not(contains(@class,'size-buttons-size-button-disabled')) and not(contains(@class,'size-buttons-show-size-chart'))]/p/text()"

def get_price(product):
    url = f"http://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}&url={product['url']}&render=true"
    try:
        response = requests.get(url)
        print(f"🔍 {product['name']}")
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            raise Exception(f"Non-200 response: {Exception}")

        tree = html.fromstring(response.content)
        print(f"Response: {response.content}")
        print(f"Tree: {tree}")

        if 'TopSize' in product['name']:
            required_sizes = sizes.REQUIRED_TOP_SIZES
        elif 'BottomSize' in product['name']:
            required_sizes = sizes.REQUIRED_BOTTOM_SIZES
        elif 'ShoeSize' in product['name']:
            required_sizes = sizes.REQUIRED_SHOE_SIZES
            
        size_available = False
        print(f"Required Sizes: {required_sizes}")

        main_price_elements = tree.xpath(MAIN_PRICE_XPATH)
        print(f"Main Price Elements: {main_price_elements}")
        available_sizes_elements = tree.xpath(AVAILABLE_SIZES_XPATH)
        print(f"Available Sizes Elements: {available_sizes_elements}")

        if main_price_elements:
            for size in available_sizes_elements:
                if size.strip() in required_sizes:
                    size_available = True
                    break
            
            if size_available:
                main_price = main_price_elements[0].strip()
                return int(main_price.replace('â\x82¹', '').replace("₹", "").replace(",", "")), None
            else:
                print("Required Size not available")
                return None, "Required Size not available"
        else:
            print("Product probably out of stock")
            return None, "Product probably out of stock"
    except Exception as e:
        print(f"❌ Failed to scrape {product['name']}: {e}")
        return None, str(e)