from flask import Flask, request, jsonify
import json
import os

# Initialize Flask app
app = Flask(__name__)

# Step 1: Load the JSON data (merged_product_reviews.json)
json_file_path = 'merged_product_reviews.json'
if os.path.exists(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        product_data = json.load(f)
else:
    raise FileNotFoundError(f"{json_file_path} not found. Ensure the file exists.")

# Home route to avoid 404 on the root URL
@app.route('/')
def home():
    return "<h1>Welcome to the Sublimpick API</h1><p>Use /search_products or /product_details to interact with the API.</p>"

# Route to search for products by name or URL (Page 1)
@app.route('/search_products', methods=['GET'])
def search_products():
    query = request.args.get('query', '').lower()

    # Search products by product name or part of the name
    filtered_products = [product for product in product_data if query in product['product_name'].lower()]
    
    # Return product names and URLs
    product_list = [{'product_name': product['product_name'], 'product_link': product['product_link']} for product in filtered_products]
    
    return jsonify(product_list)

# Route to get product details and reviews (Page 2)
@app.route('/product_details', methods=['GET'])
def product_details():
    product_url = request.args.get('product_url', '').lower()

    # Find the product based on the product URL
    product = next((product for product in product_data if product['product_link'].lower() == product_url), None)
    
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    # Return the full product details including reviews
    return jsonify(product)

# Main entry point to run the app
if __name__ == '__main__':
    app.run(debug=False)
