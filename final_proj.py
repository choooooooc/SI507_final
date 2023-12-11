from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import json
import os

app = Flask(__name__)


class Card:
    def __init__(self, card_data):
        self.id = card_data.get('id')
        self.name = card_data.get('name')
        self.release_date = card_data.get('set', {}).get('releaseDate')
        self.set = card_data.get('set', {}).get('name')
        self.series = card_data.get('set', {}).get('series')
        self.number = int(card_data.get('number')) if card_data.get(
            'number') and card_data.get('number').isdigit() else None
        self.hp = int(card_data.get('hp')) if card_data.get(
            'hp') and card_data.get('hp').isdigit() else 0
        self.type = card_data.get('types') if 'types' in card_data else None
        self.rarity = card_data.get(
            'rarity') if 'rarity' in card_data else None
        self.left = None
        self.right = None


class CardBST:
    def __init__(self):
        self.root = None

    def insert(self, card):
        new_card = card

        if not self.root:
            self.root = new_card
        else:
            self._insert_recursive(self.root, new_card)

    def _insert_recursive(self, current_node, new_card):
        if new_card.hp < current_node.hp:
            if not current_node.left:
                current_node.left = new_card
            else:
                self._insert_recursive(current_node.left, new_card)
        else:
            if not current_node.right:
                current_node.right = new_card
            else:
                self._insert_recursive(current_node.right, new_card)

    def reverse_inorder_traversal(self, node):
        sorted_cards = []  

        def traverse(node):
            nonlocal sorted_cards
            if node:
                traverse(node.right)
                sorted_cards.append({
                    'ID': node.id,
                    'Name': node.name,
                    'Number': node.number,
                    'HP': node.hp,
                    'Set': node.set,
                    'Series': node.series,
                    'Release': node.release_date,
                    'Rarity': node.rarity,
                })
                traverse(node.left)

        traverse(node)  
        return sorted_cards  
    

# Function to fetch product data
def fetch_cards_from_api():
    """
    Fetches Pokemon cards from the Pokemon TCG API based on specified parameters.

    Returns
    -------
    list
        List of Pokemon cards retrieved from the API.
    """
    order = '-set.releaseDate'
    url = f'https://api.pokemontcg.io/v2/cards'
    all_cards = []
    page = 1
    while page < 8:
        response = requests.get(f"{url}?page={page}&orderBy={order}")
        if response.status_code == 200:
            json_file = json.loads(response.text)
            cards = json_file.get('data', [])
            for card in cards:
                release_date = card.get('set', {}).get('releaseDate')
                if release_date and release_date > "2020":  # Filter cards with release date after 2020
                    all_cards.append(card)
            page += 1
        else:
            print("API error")
            break
    for item in all_cards:
        item.pop("tcgplayer", None)
        item.pop("cardmarket", None)
        item.pop("attacks", None)
        item.pop("weaknesses", None)
        item.pop("retreatCost", None)
        item.pop("legalities", None)
    return all_cards


current_directory = os.path.dirname(os.path.abspath(__file__))
CACHE_NAME = os.path.join(current_directory, "pokemon_cards.json")


def load_cache():
    """
    Loads cached data from the local cache file.

    Returns
    -------
    dict
        Dictionary containing the cached data.
    """
    if os.path.exists(CACHE_NAME):
        with open(CACHE_NAME, 'r') as cache_file:
            return json.load(cache_file)
    return {}


def save_cache(data):
    """
    Saves data to the local cache file.

    Parameters
    ----------
    data : dict
        The data to be saved to the cache.
    """
    with open(CACHE_NAME, 'w') as cache_file:
        json.dump(data, cache_file)


def fetch_pokemon_cards():
    """
    Fetches Pokemon cards from the cached data.

    Returns
    -------
    list
        List of Pokemon card objects created from the cached data.
    """
    if os.path.exists(CACHE_NAME):
        raw_json_data = load_cache() 
    else:
        save_cache(fetch_cards_from_api())
        raw_json_data = load_cache()
    cards = [Card(card_data) for card_data in raw_json_data]
    return cards


def fetch_all_types():
    """
    Fetches all types of Pokemon cards from the cached data.

    Returns
    -------
    list
        List of all Pokemon types available.
    """
    if os.path.exists(CACHE_NAME):
        raw_json_data = load_cache() 
    else:
        save_cache(fetch_cards_from_api())
        raw_json_data = load_cache()
    cards = [Card(card_data) for card_data in raw_json_data]
    all_types = set()
    for card in cards:
        if card.type:
            all_types.update(card.type)

    return list(all_types)


def fetch_card_by_id(card_id):
    """
    Fetches a specific Pokemon card based on its ID.

    Parameters
    ----------
    card_id : str
        The ID of the Pokemon card to be fetched.

    Returns
    -------
    Card or None
        The Pokemon card object if found, otherwise None.
    """
    card_data = fetch_pokemon_cards()
    for card in card_data:
        if card.id == card_id:
            return card 
    return None


# get the url for the detailed page of the searched card
def fetch_card_detail_url(url):
    """
    Fetches the URL for the detailed page of the searched card.

    Parameters
    ----------
    url : str
        The URL to be checked.

    Returns
    -------
    str or None
        The detailed page URL if available, otherwise None.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    search_page_div = soup.find('div', {'id': 'search-page'})
    if search_page_div:  # 0 or n results
        h1_element = search_page_div.find('h1')
        if h1_element:
            extracted_h1 = h1_element.text.strip().lower()
            if "no results for" in extracted_h1:  # 0 result
                return None
            else:  # n results
                # only obtain the first result
                product_row = soup.find_all("tr")[1]
                data = []
                card_name_element = product_row.find('td', class_='title')
                card_url_element = card_name_element.find(
                    'a') if card_name_element else None
                card_url = card_url_element.get(
                    'href') if card_url_element else 'Not available'
                return card_url
    else:  # 1 result
        return url


def fetch_card_img(url):  # fetch the image of the card
    """
    Fetches the image URL of the card from its detailed page.

    Parameters
    ----------
    url : str
        The URL of the detailed page.

    Returns
    -------
    str or None
        The image URL if available, otherwise None.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    product_details_div = soup.find('div', {'id': 'product_details'})
    if product_details_div:
        cover_div = product_details_div.find('div', {'class': 'cover'})
        if cover_div:
            image_tag = cover_div.find('img')
            if image_tag:
                image_url = image_tag.get('src')
                return image_url
            else:
                return None
        else:
            return None
    else:
        return None


def fetch_price_chart(url):  # fetch the price chart of the card
    """
    Fetches the URL for the price chart of the card.

    Parameters
    ----------
    url : str
        The URL of the detailed page.

    Returns
    -------
    str or None
        The URL for the price chart if available, otherwise None.
    """
    response = requests.get(fetch_card_detail_url(url))
    soup = BeautifulSoup(response.content, "html.parser")
    chart_compare_element = soup.find('a', id='chart-compare')
    if chart_compare_element:
        product_detailurl = chart_compare_element.get('href')
        return product_detailurl
    else:
        return None


def fetch_cards_for_sale(url):
    """
    Fetches information about Pokemon cards available for sale.

    Parameters
    ----------
    url : str
        The URL of the page containing cards for sale.

    Returns
    -------
    list or None
        List of dictionaries containing information about cards for sale, or None if no information is found.
    """
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table_element = soup.find('table', class_='hoverable-rows sortable')
        if table_element:
            sales_rows = table_element.find_all('tr')[1:]
            cards_for_sale_info = []
            for row in sales_rows:
                sale_date_element = row.find('td', class_='date')
                sale_date = sale_date_element.text.strip() if sale_date_element else 'Not available'
                sale_price_element = row.find('td', class_='numeric')
                sale_price = sale_price_element.find(
                    class_='js-price').text.strip() if sale_price_element else 'Not available'
                url_element = row.find('td', class_='title')
                sale_url = url_element.find(
                    'a', class_='js-ebay-completed-sale')['href'] if url_element else 'Not available'

                sale_data = {
                    'date': sale_date,
                    'url': sale_url,
                    'price': sale_price
                }
                cards_for_sale_info.append(sale_data)

            return cards_for_sale_info

        return None


@app.route('/')
def index():
    """
    Handles the route for the home page. Show the type filter.

    Returns
    -------
    str
        HTML template rendered for the home page.
    """
    # Capability 1: Provide a list of Pokémon types to choose from
    pokemon_types = fetch_all_types() 
    return render_template('index.html', pokemon_types=pokemon_types)


@app.route('/cards', methods=['POST'])
def display_cards():
    """
    Handles the route for displaying filtered cards in a HP decending order. 

    Returns
    -------
    str
        HTML template rendered for displaying filtered cards.
    """
    # Capability 1: Filter cards by selected type and display in descending HP order
    selected_type = request.form['selected_type']
    cards_data = fetch_pokemon_cards()
    filter_type_cards = [
        card for card in cards_data if card.type and selected_type in card.type]
    card_tree = CardBST()
    for card in filter_type_cards:
        card_tree.insert(card)
    cards_sorted_by_hp = card_tree.reverse_inorder_traversal(
        card_tree.root)

    return render_template('cards.html', cards=cards_sorted_by_hp)


@app.route('/card_details/<path:card_id>')
def card_details(card_id):
    """
    Handles the route for displaying card details.

    Parameters
    ----------
    card_id : str
        The ID of the card to display details for.

    Returns
    -------
    str
        HTML template rendered for displaying card details.
    """
    # Capability 1: Show the selected card's details including its image
    chosen_card = fetch_card_by_id(card_id)
    card_name = chosen_card.name.replace(" ", "+")
    searching_term = f"{card_name}+%23{chosen_card.number}"
    url = f"https://www.pricecharting.com/search-products?q={searching_term}&type=prices"
    detail_url = fetch_card_detail_url(url)
    if detail_url:
        img_url = fetch_card_img(detail_url)
    card_info_data = {
        'ID': chosen_card.id,
        'Name': chosen_card.name,
        'Number': chosen_card.number,
        'HP': chosen_card.hp,
        'Set': chosen_card.set,
        'Series': chosen_card.series,
        'Release': chosen_card.release_date,
        'Rarity': chosen_card.rarity,
        'Img_url': img_url
    }

    return render_template('card_details.html', card_info=card_info_data)


@app.route('/price_info/<path:card_id>')
def price_info(card_id):
    """
    Handles the route for displaying price chart and purchase urls

    Parameters
    ----------
    card_id : str
        The ID of the card to display price information for.

    Returns
    -------
    str
        HTML template rendered for displaying price information.
    """
    # Capability 3: Show the price flow chart for the chosen card
    chosen_card = fetch_card_by_id(card_id)
    card_name = chosen_card.name.replace(" ", "+")
    searching_term = f"{card_name}+%23{chosen_card.number}"
    url = f"https://www.pricecharting.com/search-products?q={searching_term}&type=prices"
    detail_url = fetch_card_detail_url(url)
    chart_url = fetch_price_chart(detail_url)
    chart_url = "https://www.pricecharting.com"+chart_url
    # Capability 4: Show current cards for sale and their purchasing URLs
    cards_for_sale_data = fetch_cards_for_sale(detail_url)
    return render_template('price_info.html', url=chart_url, cards_for_sale=cards_for_sale_data)


if __name__ == '__main__':
    """
    Runs the Flask application.

    This function is the entry point for executing the Flask application.

    Returns
    -------
    None
    """
    app.run(debug=True)
