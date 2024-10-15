from flask import Blueprint, jsonify, request
import json

product_routes = Blueprint('product_routes', __name__)

# Charger les données produits (si nécessaire, mais tu peux les passer depuis app.py)
with open('merged_product_reviews.json', 'r', encoding='utf-8') as f:
    product_data = json.load(f)

# API pour rechercher des produits
@product_routes.route('/api/search_products', methods=['GET'])
def search_products():
    query = request.args.get('query', '').lower()
    filtered_products = [product for product in product_data if query in product['product_name'].lower()]
    return jsonify(filtered_products)

# API pour obtenir les détails d'un produit
@product_routes.route('/api/product_details', methods=['GET'])
def product_details():
    product_url = request.args.get('product_url', '').lower()
    product = next((product for product in product_data if product['product_link'].lower() == product_url), None)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product)
