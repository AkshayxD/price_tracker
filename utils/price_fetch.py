import os, requests
from lxml import html

SCRAPERAPI_KEY = os.getenv("SCRAPERAPI_KEY")

AMAZON_XPATH = "//div[contains(@id, 'corePriceDisplay_desktop_feature_div')]//span[contains(@class, 'a-price-whole')]/text()"
FLIPKART_XPATH = "//div[contains(@class, 'Nx9bqj') and contains(@class, 'CxhGGd')]/text()"

def get_price(product):
    url = f"http://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}&url={product['url']}"
    try:
        response = requests.get(url)
        print(f"🔍 {product['name']}")
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            raise Exception(f"Non-200 response: {Exception}")

        tree = html.fromstring(response.content)
        print(f"Content: {tree[:100]}")

        if 'amazon' in product['name'].lower():
            rqd_xpath = AMAZON_XPATH
        elif 'flipkart' in product['name'].lower():
            rqd_xpath = FLIPKART_XPATH
        else:
            print("⚠️ Website name not present in product['name']")
            return None

        price_elements = tree.xpath(rqd_xpath)
        print(f"Price Element: {price_elements}")
        if price_elements:
            price_text = price_elements[0].strip()
            return int(price_text.replace("₹", "").replace(",", ""))
    except Exception as e:
        print(f"❌ Failed to scrape {product['name']}: {e}")
    return None