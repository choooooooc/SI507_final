import requests
import requests_cache
import json
from bs4 import BeautifulSoup
import os
requests_cache.install_cache('pricecharting_cache', expire_after=3600)

def fetch_product_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    product_rows = soup.find_all("tr")[1:]  # Exclude the first row
    data = []
    for row in product_rows:
        card_name_element = row.find('td', class_='title')
        card_url_element = card_name_element.find('a') if card_name_element else None
        card_name = card_url_element.text.strip() if card_url_element else 'Not available'
        card_url = card_url_element.get('href') if card_url_element else 'Not available'

        card_set_element = row.find('td', class_='console')
        card_set = card_set_element.text.strip() if card_set_element else 'Not available'

        low_price_element = row.find('td', class_='price numeric used_price')
        mid_price_element = row.find('td', class_='price numeric cib_price')
        high_price_element = row.find('td', class_='price numeric new_price')

        low_price = low_price_element.find('span', class_='js-price').text.strip() if low_price_element else 'Not available'
        mid_price = mid_price_element.find('span', class_='js-price').text.strip() if mid_price_element else 'Not available'
        high_price = high_price_element.find('span', class_='js-price').text.strip() if high_price_element else 'Not available'

        product_data = {
            'Card Name': card_name,
            'Card Set': card_set,
            'Card URL': card_url,
            'Low Price': low_price,
            'Mid Price': mid_price,
            'High Price': high_price
        }
        data.append(product_data)
    return data
current_directory = os.path.dirname(os.path.abspath(__file__))
CACHE_NAME = os.path.join(current_directory, "cards_price.json")
# load cache
def load_cache():
    if os.path.exists(CACHE_NAME):
        with open(CACHE_NAME, 'r') as cache_file:
            return json.load(cache_file)
    return {}
# save cache
def save_cache(data):
    with open(CACHE_NAME, 'w') as cache_file:
        json.dump(data, cache_file)

searching_term="pikachu"
url = f"https://www.pricecharting.com/search-products?q={searching_term}&type=prices"
product_data = fetch_product_data(url)
save_cache(product_data)
print('Data has been saved to cards_price.json')

