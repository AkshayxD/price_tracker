import os, requests
from lxml import html

SCRAPERAPI_KEY = os.getenv("SCRAPERAPI_KEY")

MAIN_PRICE_XPATH = "//div[contains(@id, 'corePriceDisplay_desktop_feature_div')]//span[contains(@class, 'a-price-whole')]/text()"

def get_price(product):
    url = f"http://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}&url={product['url']}"
    try:
        response = requests.get(url)
        print(f"🔍 {product['name']}")
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            raise Exception(f"Non-200 response: {Exception}")

        tree = html.fromstring(response.content)
        rqd__main_price_xpath = MAIN_PRICE_XPATH

        main_price_elements = tree.xpath(rqd__main_price_xpath)
        print(f"Main Price Element: {main_price_elements}")
        if main_price_elements:
            main_price = main_price_elements[0].strip()
            return int(main_price.replace("₹", "").replace(",", ""))
            
    except Exception as e:
        print(f"❌ Failed to scrape {product['name']}: {e}")
    return None