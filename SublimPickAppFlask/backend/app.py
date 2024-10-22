from flask import Flask, request, jsonify, render_template
import pandas as pd
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

import matplotlib
matplotlib.use('Agg')

from helpers.rating_distrubition_reviews import create_review_graphs
from helpers.sentiment_analysis_reviews import create_sentiment_graph
from helpers.trend_reviews_over_time import create_review_trend_graph
from helpers.keywords_top_reviews import create_keyword_graph

import time

# Timing the download and loading of the product data
start_time = time.time()
# Adjust paths to refer to frontend from the backend directory
app = Flask(
    __name__,
    template_folder=os.path.join(os.getcwd(), '..', 'frontend', 'templates'),
    static_folder=os.path.join(os.getcwd(), '..', 'frontend', 'static')
)
print("Template folder:", app.template_folder)
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Reload templates without caching

from google.cloud import storage
import tempfile

# Fonction pour télécharger un fichier depuis un bucket Google Cloud Storage
def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Télécharge un fichier blob de Cloud Storage vers le système local."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    print(f"Fichier {source_blob_name} téléchargé sur {destination_file_name}.")

# Télécharger les fichiers depuis Cloud Storage
# bucket_name = os.getenv('BUCKET_NAME', 'sublime_bucket_2024')
# storage_path = os.getenv('STORAGE_PATH', 'data-test-api-application')
bucket_name = os.getenv('BUCKET_NAME', 'sublime_bucket_bis')
storage_path = os.getenv('STORAGE_PATH', '10/reviews')



json_file_name = 'merged_product_reviews.json'
source_blob_name = f'{storage_path}/{json_file_name}'
# destination_file_name = f'/tmp/{json_file_name}'
destination_file_name = os.path.join(tempfile.gettempdir(), json_file_name)

# Télécharger le fichier JSON dans /tmp pour utilisation locale
download_blob(bucket_name, source_blob_name, destination_file_name)

# Charger les données JSON
json_file_path = destination_file_name
if os.path.exists(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        product_data = json.load(f)
else:
    raise FileNotFoundError(f"{json_file_path} not found. Ensure the file exists.")

# Log time taken to load product data
print(f"Time to load product data: {time.time() - start_time:.4f} seconds")

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
@app.route('/product/<path:product_url>', methods=['GET'])
def product_details(product_url):
    product_url = product_url.strip().lower().rstrip('/')
    product = next((product for product in product_data if product['product_link'].strip().lower().rstrip('/') == product_url), None)

    if product is None:
        return render_template('404.html'), 404
    
    # Timing the graph generation
    start_time = time.time()
    
    # Get the interval from the request parameters (default to 'Y' for Year)
    interval = request.args.get('interval', 'Y')
    
    plot_url = create_review_graphs(product['reviews'])
    plot_url2 = create_sentiment_graph(product['reviews'])
    plot_url3 = create_review_trend_graph(product['reviews'], interval)
    plot_url4 = create_keyword_graph(product['reviews'])
    
    # Check if the request is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # If it's an AJAX request
        return jsonify({
            'plot_url3': plot_url3  # Return only the graph that needs to be updated
        })

    # Log time taken to generate graphs
    print(f"Time to generate graphs: {time.time() - start_time:.4f} seconds")

    return render_template('product_details.html', product=product, plot_url=plot_url, plot_url2=plot_url2, plot_url3=plot_url3, plot_url4=plot_url4)

# Main entry point to run the app
if __name__ == '__main__':
    app.run(debug=False)
