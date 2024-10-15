import io
import base64
from io import BytesIO
from flask import Flask, request, jsonify, render_template
from matplotlib.figure import Figure
import pandas as pd
from collections import Counter
import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from helpers.rating_distrubition_reviews import create_review_graphs
from helpers.sentiment_analysis_reviews import create_sentiment_graph
from helpers.trend_reviews_over_time import create_review_trend_graph
from helpers.keywords_top_reviews import create_keyword_graph


import logging

# # Désactiver la journalisation des requêtes HTTP
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)  # Seuls les messages d'erreur seront affichés


# Initialize Flask app
app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

# Load the JSON data (merged_product_reviews.json)
json_file_path = 'merged_product_reviews.json'
if os.path.exists(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        product_data = json.load(f)
else:
    raise FileNotFoundError(f"{json_file_path} not found. Ensure the file exists.")



# Home route (Index page with project introduction)
@app.route('/')
def index():
    return render_template('home.html')

# Route to the search page
@app.route('/search')
def search_page():
    return render_template('index.html')

# Route to search for products by name
@app.route('/search_products', methods=['GET'])
def search_products():
    query = request.args.get('query', '').lower()
    filtered_products = [product for product in product_data if query in product['product_name'].lower()]
    product_list = [{'product_name': product['product_name'], 'product_link': product['product_link']} for product in filtered_products]
    return jsonify(product_list)

# Route to show product details in a separate page
@app.route('/product/<path:product_url>')
def product_details(product_url):
    product_url = product_url.strip().lower().rstrip('/')
    product = next((product for product in product_data if product['product_link'].strip().lower().rstrip('/') == product_url), None)

    if product is None:
        return render_template('404.html'), 404
    
    plot_url = create_review_graphs(product['reviews'])
    plot_url2 = create_sentiment_graph(product['reviews'])
    plot_url3 = create_review_trend_graph(product['reviews'])
    plot_url4 = create_keyword_graph(product['reviews'])

    return render_template('product_details.html', product=product, plot_url=plot_url, plot_url2=plot_url2, plot_url3=plot_url3, plot_url4=plot_url4)

# Main entry point to run the app
if __name__ == '__main__':
    app.run(debug=False)
