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

import logging

# # Désactiver la journalisation des requêtes HTTP
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)  # Seuls les messages d'erreur seront affichés


# Initialize Flask app
app = Flask(__name__)

# Load the JSON data (merged_product_reviews.json)
json_file_path = 'merged_product_reviews.json'
if os.path.exists(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        product_data = json.load(f)
else:
    raise FileNotFoundError(f"{json_file_path} not found. Ensure the file exists.")

# Helper function to generate the review distribution graph
def create_review_graphs(product_reviews):
    df = pd.DataFrame(product_reviews)
    df['review_collected_date'] = pd.to_datetime(df['review_collected_date'], errors='coerce')
    df_sorted = df.sort_values(by='review_collected_date', ascending=False)
    star_counts = df_sorted['review_stars'].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(star_counts, labels=star_counts.index, autopct='%1.1f%%', startangle=90)
    ax.set_title('Distribution of Star Ratings')

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return plot_url

# Helper function to generate sentiment analysis graph
def create_sentiment_graph(product_reviews):
    df = pd.DataFrame(product_reviews)
    sentiment_counts = df['sentiment_category'].value_counts()

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.bar(sentiment_counts.index, sentiment_counts.values, color=['green', 'red', 'orange'])
    ax.set_title('Sentiment Analysis of Reviews')

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url2 = base64.b64encode(img.getvalue()).decode()
    return plot_url2


# Helper function to generate review trend over time graph
def create_review_trend_graph(product_reviews):
    df = pd.DataFrame(product_reviews)
    df['review_date'] = pd.to_datetime(df['review_date'], format='%m/%d/%y', errors='coerce')

    fig, ax = plt.subplots(figsize=(5, 5))
    df.set_index('review_date').resample('M').size().plot(ax=ax)
    ax.set_title('Trend of Reviews Over Time')
    ax.set_xlabel('Month')
    ax.set_ylabel('Number of Reviews')

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url3 = base64.b64encode(img.getvalue()).decode()
    return plot_url3

# Helper function to generate a word cloud-like chart for keywords
def create_keyword_graph(product_reviews):
    keywords = []
    for review in product_reviews:
        keywords.extend(eval(review['keywords']))

    keyword_counts = Counter(keywords).most_common(10)
    keywords, counts = zip(*keyword_counts)

    fig, ax = plt.subplots(figsize=(5, 5))
    sns.barplot(x=counts, y=keywords, ax=ax, palette="viridis", legend=False, hue = keywords)
    ax.set_title('Top 10 Keywords in Reviews')

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url4 = base64.b64encode(img.getvalue()).decode()
    return plot_url4


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
