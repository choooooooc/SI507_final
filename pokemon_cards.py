import requests
import json
import os

class Card:
    def __init__(self, card_data):
        self.id = card_data.get('id')
        self.name = card_data.get('name')
        self.release_date = card_data.get('set', {}).get('releaseDate')
        self.set = card_data.get('set', {}).get('name')
        self.series = card_data.get('set', {}).get('series')
        self.number = int(card_data.get('number')) if card_data.get('number') and card_data.get('number').isdigit() else None
        self.hp = int(card_data.get('hp')) if card_data.get('hp') and card_data.get('hp').isdigit() else None
        self.type = card_data.get('types') if 'types' in card_data else None
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
        if node:
            self.reverse_inorder_traversal(node.right)
            print(f"ID: {node.id}, Name: {node.name}, Number: {node.number}, HP: {node.hp}")
            self.reverse_inorder_traversal(node.left)


def fetch_pokemon_cards():
    key = "4d353b8e-e868-40b7-aa12-352136ed9894"
    #term = "name:pikachu"
    order='-set.releaseDate'
    url = f'https://api.pokemontcg.io/v2/cards'
    headers = {'X-Api-Key': key}
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

#cards_data=fetch_pokemon_cards()
#save_cache(cards_data)
raw_json_data = load_cache()
cards = [Card(card_data) for card_data in raw_json_data]
type_filter='Lightning'
filter_type_cards = [card for card in cards if card.type and 'Lightning' in card.type]
card_tree = CardBST()

for card in filter_type_cards:
    card_tree.insert(card)

print("Cards sorted by HP:")
card_tree.reverse_inorder_traversal(card_tree.root)