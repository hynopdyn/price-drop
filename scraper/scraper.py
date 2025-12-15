# scraper/scraper.py
from bs4 import BeautifulSoup
from curl_cffi import requests
import time

async def scrape(url: str):
    # Create a session, send a request, and soupify the HTML
    session = requests.AsyncSession()
    res = await session.get(url, impersonate="chrome")
    soup = BeautifulSoup(res.text, "html.parser")
    print(soup.prettify()[:1000])

    # Grab the product title and price
    product_title = soup.select_one("span#productTitle").text.strip()
    product_price_whole = soup.select_one("div#corePriceDisplay_desktop_feature_div span.a-price-whole").text.strip()
    product_price_fraction = soup.select_one("span.a-price-fraction").text.strip()

    # Remove any commas from the whole part of the price
    product_price_whole = product_price_whole.replace(",", "")

    # Combine the dollars and cents to form the full price
    product_price = float(product_price_whole + product_price_fraction)

    # Grab the first thumbnail image URL
    product_image = soup.select_one("img#landingImage")["src"]

    data = {
        "url": url,
        "title": product_title,
        "image": product_image,
        "price": product_price,
        "timestamp": time.time()
    }

    return data

# For standalone testing
if __name__ == "__main__":
    import asyncio
    import json

    start = time.time()

    url = "https://www.amazon.com/gp/aw/d/B07V8KG7ND/"
    product_data = asyncio.run(scrape(url))
    print(json.dumps(product_data, indent=2))

    print(f"Scrape completed in {product_data['timestamp'] - start:.3f} seconds")