import os
import json


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
            print(
                f"ID: {node.id}, Name: {node.name}, Number: {node.number}, HP: {node.hp}")
            self.reverse_inorder_traversal(node.left)


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

# Create binary search tree


def create_card_tree():
    raw_json_data = load_cache()
    cards = [Card(card_data) for card_data in raw_json_data]
    card_tree = CardBST()

    for card in cards:
        card_tree.insert(card)

    return card_tree

# Convert tree to dictionary


def tree_to_dict(node):
    if not node:
        return None
    return {
        'id': node.id,
        'name': node.name,
        'number': node.number,
        'hp': node.hp,
        'left': tree_to_dict(node.left),
        'right': tree_to_dict(node.right)
    }

# Save constructed tree as JSON


def save_tree_as_json(tree):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    TREE_JSON = os.path.join(current_directory, "pokemon_card_tree.json")
    tree_dict = tree_to_dict(tree.root) if tree.root else {}

    with open(TREE_JSON, 'w') as tree_file:
        json.dump(tree_dict, tree_file, indent=2)


if __name__ == "__main__":
    card_tree = create_card_tree()
    save_tree_as_json(card_tree)
