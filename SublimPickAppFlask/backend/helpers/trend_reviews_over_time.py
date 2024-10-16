import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Helper function to generate review trend over time graph
def create_review_trend_graph(product_reviews):
    if not product_reviews or len(product_reviews) == 0:
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.text(0.5, 0.5, 'No reviews available', horizontalalignment='center', verticalalignment='center', fontsize=12, color='red')
        ax.set_title('Trend of Reviews Over Time')
        ax.axis('off')

        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url3 = base64.b64encode(img.getvalue()).decode()
        return plot_url3

    df = pd.DataFrame(product_reviews)
    
    if 'review_date' not in df.columns or df['review_date'].isnull().all():
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.text(0.5, 0.5, 'No review date data available', horizontalalignment='center', verticalalignment='center', fontsize=12, color='red')
        ax.set_title('Trend of Reviews Over Time')
        ax.axis('off')

        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url3 = base64.b64encode(img.getvalue()).decode()
        return plot_url3

    df['review_date'] = pd.to_datetime(df['review_date'], format='%m/%d/%y', errors='coerce')

    fig, ax = plt.subplots(figsize=(5, 5))
    df.set_index('review_date').resample('Y').size().plot(ax=ax)
    ax.set_title('Trend of Reviews Over Time')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Reviews')

    img = BytesIO()
    plt.savefig(img, format='png')
    # After saving
    plt.close(fig)  # This will close the figure and free memory
    img.seek(0)
    plot_url3 = base64.b64encode(img.getvalue()).decode()
    return plot_url3
