import json
import os
class TreeNode:
    def __init__(self, node_data):
        self.id = node_data.get('id')
        self.name = node_data.get('name')
        self.number = node_data.get('number')
        self.hp = node_data.get('hp')
        self.left = node_data.get('left')
        self.right = node_data.get('right')

    def display_node_info(self):
        print(f"ID: {self.id}, Name: {self.name}, Number: {self.number}, HP: {self.hp}")

def read_tree_from_json():
    # Load the JSON file containing the tree data
    current_directory = os.path.dirname(os.path.abspath(__file__))
    TREE_JSON = os.path.join(current_directory, "pokemon_card_tree.json")

    with open(TREE_JSON, 'r') as tree_file:
        tree_data = json.load(tree_file)

    return tree_data

def construct_tree(tree_data):
    if not tree_data:
        return None

    root = TreeNode(tree_data)
    root.left = construct_tree(tree_data.get('left'))
    root.right = construct_tree(tree_data.get('right'))

    return root

def display_tree_info(node):
    if node:
        display_tree_info(node.right)
        node.display_node_info()
        display_tree_info(node.left)

if __name__ == "__main__":
    tree_json_data = read_tree_from_json()
    root_node = construct_tree(tree_json_data)
    
    print("Tree Information:")
    display_tree_info(root_node)
