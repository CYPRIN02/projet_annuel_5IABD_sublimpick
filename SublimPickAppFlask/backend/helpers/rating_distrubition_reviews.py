import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Helper function to generate review distribution graph
def create_review_graphs(product_reviews):
    # Vérifier s'il y a des reviews
    if not product_reviews or len(product_reviews) == 0:
        # Si pas de critiques, retourner un message par défaut ou un graphique vide
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.text(0.5, 0.5, 'No reviews available', horizontalalignment='center', verticalalignment='center', fontsize=12, color='red')
        ax.set_title('Distribution of Star Ratings')
        ax.axis('off')  # Enlever les axes

        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        return plot_url
    
    # Si des reviews existent, continuer avec le traitement
    df = pd.DataFrame(product_reviews)
    df['review_date'] = pd.to_datetime(df['review_date'],  format='%m/%d/%y', errors='coerce')

    df_sorted = df.sort_values(by='review_date', ascending=False)
    star_counts = df_sorted['review_stars'].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(star_counts, labels=star_counts.index, autopct='%1.1f%%', startangle=90)
    ax.set_title('Distribution of Star Ratings')

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return plot_url