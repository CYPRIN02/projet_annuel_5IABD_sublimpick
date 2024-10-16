import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Helper function to generate sentiment analysis graph
def create_sentiment_graph(product_reviews):
    if not product_reviews or len(product_reviews) == 0:
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.text(0.5, 0.5, 'No reviews available', horizontalalignment='center', verticalalignment='center', fontsize=12, color='red')
        ax.set_title('Sentiment Analysis of Reviews')
        ax.axis('off')

        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url2 = base64.b64encode(img.getvalue()).decode()
        return plot_url2

    df = pd.DataFrame(product_reviews)
    
    if 'sentiment_category' not in df.columns or df['sentiment_category'].isnull().all():
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.text(0.5, 0.5, 'No sentiment data available', horizontalalignment='center', verticalalignment='center', fontsize=12, color='red')
        ax.set_title('Sentiment Analysis of Reviews')
        ax.axis('off')

        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url2 = base64.b64encode(img.getvalue()).decode()
        return plot_url2

    sentiment_counts = df['sentiment_category'].value_counts()

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.bar(sentiment_counts.index, sentiment_counts.values, color=['green', 'red', 'orange'])
    ax.set_title('Sentiment Analysis of Reviews')

    img = BytesIO()
    plt.savefig(img, format='png')
    # After saving
    plt.close(fig)  # This will close the figure and free memory
    img.seek(0)
    plot_url2 = base64.b64encode(img.getvalue()).decode()
    return plot_url2
