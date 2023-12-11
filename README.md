# SI507_final
Backup for SI507 final project.
## Running the code
1. Make sure you have python installed
2. Install the required Python packages using `pip install -r requirements.txt`.
3. Run the [Flask application](final_proj.py) by executing `python final_proj.py` in your terminal.
API can be accessed without keys. If you want to increase rate, you can apply for an API key referring to https://docs.pokemontcg.io/getting-started/authentication/#:~:text=Authentication%20to%20the%2>
## Interacting with the program
Once the Flask application is running, you can click on the link and:
1. Access the home page to filter Pokémon cards by type.
  ![image](/image/home_page.png)
2. Explore the cards displayed in descending order of HP.
3. Click on the 'View Details' link below a card to view its details, including an image and other information.
4. Check the price information and available purchase URLs for a specific card on the detail page.

## Date Structure
Binary Search Tree: I implemented a Binary Search Tree class to organize the Pokemon cards based on their HP. For a new card, the insert() method will determine its position in the tree based on the HP attribute. After all target cards are inserted into the appropriate nodes of the BST, I used the reverse_inorder_traversal() method to traverse the tree in reverse order, from the rightmost node (highest HP) to the leftmost (lowest HP). At each node, it also prints the card information (ID, name, number, HP) in reverse order of their HP values. Then the target cards are displayed in a descending order of their HP.<br>
[Constructing the BST](data_structure.py)<br>
[JSON file with my BST](pokemon_card_tree.json)<br>
[Reading the json of the tree](read_tree.py)
