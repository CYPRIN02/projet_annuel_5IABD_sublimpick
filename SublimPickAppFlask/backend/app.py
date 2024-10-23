import os
import json
import tempfile
import time
from flask import Flask, request, jsonify, render_template
from google.cloud import storage

# Importation des modules pour les graphiques
from backend.helpers.rating_distrubition_reviews import create_review_graphs
from backend.helpers.sentiment_analysis_reviews import create_sentiment_graph
from backend.helpers.trend_reviews_over_time import create_review_trend_graph
from backend.helpers.keywords_top_reviews import create_keyword_graph

import matplotlib
matplotlib.use('Agg')  # Agg backend for non-interactive environments

import logging
logging.basicConfig(level=logging.DEBUG)

# Initialisation de l'application Flask
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '../frontend/templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '../frontend/static')
)
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Forcer le rechargement des templates

# Variable globale pour stocker les données produits
product_data = None

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Télécharge un fichier blob de Google Cloud Storage."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
        print(f"Fichier {source_blob_name} téléchargé vers {destination_file_name}.")
    except Exception as e:
        print(f"Erreur lors du téléchargement du fichier: {e}")

def load_product_data():
    """Télécharge les données produits depuis le bucket GCP et les charge en mémoire."""
    global product_data
    if product_data is None:
        bucket_name = os.getenv('BUCKET_NAME', 'sublime_bucket_bis')
        storage_path = os.getenv('STORAGE_PATH', '10/reviews/merged_product_reviews.json')
        destination_file = os.path.join(tempfile.gettempdir(), 'merged_product_reviews.json')

        try:
            download_blob(bucket_name, storage_path, destination_file)
        except Exception as e:
            print(f"Erreur lors du téléchargement des données produits: {e}")
            return None

        # Charger les données JSON en mémoire
        if os.path.exists(destination_file):
            try:
                with open(destination_file, 'r', encoding='utf-8') as file:
                    product_data = json.load(file)
                    print("Données produits chargées en mémoire.")
            except Exception as e:
                print(f"Erreur lors du chargement des données JSON: {e}")
        else:
            raise FileNotFoundError(f"{destination_file} introuvable.")
    return product_data


@app.route('/')
def index():
    """Affiche la page d'accueil."""
    return render_template('home.html')

@app.route('/search')
def search_page():
    """Affiche la page de recherche."""
    return render_template('index.html')

@app.route('/search_products', methods=['GET'])
def search_products():
    """Recherche les produits par nom."""
    query = request.args.get('query', '').lower()
    product_data = load_product_data()
    filtered_products = [p for p in product_data if query in p['product_name'].lower()]
    return jsonify([{'product_name': p['product_name'], 'product_link': p['product_link']} for p in filtered_products])

@app.route('/product/<path:product_url>', methods=['GET'])
def product_details(product_url):
    """Affiche les détails d'un produit spécifique."""
    product_url = product_url.strip().lower().rstrip('/')
    product_data = load_product_data()
    
    product = next((p for p in product_data if p['product_link'].strip().lower().rstrip('/') == product_url), None)
    
    if not product:
        return render_template('error.html'), 404

    # Génération des graphiques pour le produit
    interval = request.args.get('interval', 'Y')
    plot_url = create_review_graphs(product['reviews'])
    plot_url2 = create_sentiment_graph(product['reviews'])
    plot_url3 = create_review_trend_graph(product['reviews'], interval)
    plot_url4 = create_keyword_graph(product['reviews'])

    return render_template('product_details.html', product=product, plot_url=plot_url, plot_url2=plot_url2, plot_url3=plot_url3, plot_url4=plot_url4)

# Lancer l'application Flask
if __name__ == "__main__":
    app.run(debug=True)
