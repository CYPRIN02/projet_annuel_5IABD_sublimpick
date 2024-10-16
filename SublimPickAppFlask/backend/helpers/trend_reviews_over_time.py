import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Helper function to generate review trend over time graph
def create_review_trend_graph(product_reviews, interval='Y'):
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

    # Convert review_date to datetime
    df['review_date'] = pd.to_datetime(df['review_date'], format='%m/%d/%y', errors='coerce')

    # Set the resampling rule based on the user's choice
    resample_rule = 'Y'  # Default to year
    if interval == 'M':
        resample_rule = 'M'  # Resample by Month
    elif interval == 'D':
        resample_rule = 'D'  # Resample by Day

    # Now use the resample_rule
    fig, ax = plt.subplots(figsize=(5, 5))
    df.set_index('review_date').resample(resample_rule).size().plot(ax=ax)  # Corrected to use resample_rule

    # Dynamically set axis labels
    if resample_rule == 'Y':
        ax.set_xlabel('Year')
    elif resample_rule == 'M':
        ax.set_xlabel('Month')
    elif resample_rule == 'D':
        ax.set_xlabel('Day')

    ax.set_title(f'Trend of Reviews Over Time ({interval})')
    ax.set_ylabel('Number of Reviews')

    img = BytesIO()
    plt.savefig(img, format='png')
    plt.close(fig)  # This will close the figure and free memory
    img.seek(0)
    plot_url3 = base64.b64encode(img.getvalue()).decode()
    return plot_url3


# import pandas as pd
# import matplotlib.pyplot as plt
# import base64
# from io import BytesIO

# # Helper function to generate review trend over time graph
# def create_review_trend_graph(product_reviews, interval = 'Y'):
#     if not product_reviews or len(product_reviews) == 0:
#         fig, ax = plt.subplots(figsize=(5, 5))
#         ax.text(0.5, 0.5, 'No reviews available', horizontalalignment='center', verticalalignment='center', fontsize=12, color='red')
#         ax.set_title('Trend of Reviews Over Time')
#         ax.axis('off')

#         img = BytesIO()
#         plt.savefig(img, format='png')
#         img.seek(0)
#         plot_url3 = base64.b64encode(img.getvalue()).decode()
#         return plot_url3

#     df = pd.DataFrame(product_reviews)
    
#     if 'review_date' not in df.columns or df['review_date'].isnull().all():
#         fig, ax = plt.subplots(figsize=(5, 5))
#         ax.text(0.5, 0.5, 'No review date data available', horizontalalignment='center', verticalalignment='center', fontsize=12, color='red')
#         ax.set_title('Trend of Reviews Over Time')
#         ax.axis('off')

#         img = BytesIO()
#         plt.savefig(img, format='png')
#         img.seek(0)
#         plot_url3 = base64.b64encode(img.getvalue()).decode()
#         return plot_url3

#     df['review_date'] = pd.to_datetime(df['review_date'], format='%m/%d/%y', errors='coerce')

#     # Set the resampling rule based on the user's choice
#     resample_rule = 'Y'  # Default to year
#     if interval == 'M':
#         resample_rule = 'M'  # Resample by Month
#     elif interval == 'D':
#         resample_rule = 'D'  # Resample by Day

#     fig, ax = plt.subplots(figsize=(5, 5))
#     df.set_index('review_date').resample('Y').size().plot(ax=ax)
#     ax.set_title(f'Trend of Reviews Over Time ({interval})')
#     ax.set_xlabel('Year')
#     ax.set_ylabel('Number of Reviews')

#     img = BytesIO()
#     plt.savefig(img, format='png')
#     # After saving
#     plt.close(fig)  # This will close the figure and free memory
#     img.seek(0)
#     plot_url3 = base64.b64encode(img.getvalue()).decode()
#     return plot_url3
