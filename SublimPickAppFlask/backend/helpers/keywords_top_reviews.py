import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import seaborn as sns
from collections import Counter

# Helper function to generate a word cloud-like chart for keywords
def create_keyword_graph(product_reviews):
    if not product_reviews or len(product_reviews) == 0:
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.text(0.5, 0.5, 'No reviews available', horizontalalignment='center', verticalalignment='center', fontsize=12, color='red')
        ax.set_title('Top 10 Keywords in Reviews')
        ax.axis('off')

        img = BytesIO()
        plt.savefig(img, format='png')
        # After saving
        plt.close(fig)  # This will close the figure and free memory
        img.seek(0)
        plot_url4 = base64.b64encode(img.getvalue()).decode()
        return plot_url4

    keywords = []
    for review in product_reviews:
        if 'keywords' in review and review['keywords']:
            keywords.extend(eval(review['keywords']))

    if len(keywords) == 0:
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.text(0.5, 0.5, 'No keywords data available', horizontalalignment='center', verticalalignment='center', fontsize=12, color='red')
        ax.set_title('Top 10 Keywords in Reviews')
        ax.axis('off')

        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url4 = base64.b64encode(img.getvalue()).decode()
        return plot_url4

    keyword_counts = Counter(keywords).most_common(10)
    keywords, counts = zip(*keyword_counts)

    fig, ax = plt.subplots(figsize=(5, 5))
    sns.barplot(x=counts, y=keywords, ax=ax, palette="viridis", legend=False, hue=keywords)
    ax.set_title('Top 10 Keywords in Reviews')

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url4 = base64.b64encode(img.getvalue()).decode()
    return plot_url4
