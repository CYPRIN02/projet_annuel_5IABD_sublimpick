import pandas as pd
import csv
import ast
import json
from datetime import datetime
from google.cloud import storage  # Import GCS client

# Function to download files from GCS
def download_from_gcs(bucket_name, blob_name):
    """Downloads the file from GCS and returns the content as text."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.download_as_text()

# Function to upload the result JSON to GCS
def upload_to_gcs(bucket_name, blob_name, content):
    """Uploads content (string) to GCS as a file."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(content)
    print(f"[LOG] Uploaded result to GCS: {bucket_name}/{blob_name}")

# Convert review_date to m/d/yy format without leading zeros manually
def format_date(date_str):
    try:
        # Convert the ISO 8601 date string to a datetime object
        date_obj = pd.to_datetime(date_str, errors='coerce')
        if pd.isnull(date_obj):
            return None  # Handle invalid dates
        
        # Extract month, day, and year and manually remove leading zeros
        month = date_obj.month
        day = date_obj.day
        year = date_obj.year % 100  # Get the last two digits of the year
        
        return f"{month}/{day}/{year}"
    except Exception as e:
        print(f"Error formatting date: {e}")
        return None

# Fetch the url_dump from GCS
bucket_url = 'sublime_bucket_bis'
url_file_name = '10/url/url_dump_<your_file>.py'  # Update with the exact filename or pass dynamically
url_file_content = download_from_gcs(bucket_url, url_file_name)

# Extract and evaluate the product data from the url_dump file
product_data_str = url_file_content.split("CATEGORIES = ")[1]
product_data = ast.literal_eval(product_data_str)

# Convert product data to a DataFrame
product_df = pd.DataFrame(product_data, columns=['url', 'name', 'rating_star', 'rating_nb_reviews', 'price'])

# Fetch the predicted reviews CSV from GCS
bucket_reviews = 'sublime_bucket_2024'

# Get today's date in the format YYYY-MM-DD
today = datetime.now().strftime("%Y-%m-%d")

# Dynamically generate the file name with today's date
predicted_reviews_file_name = f'scrapping/10/prediction/prediction_{today}.csv'

# Download the predicted reviews CSV from GCS
predicted_reviews_content = download_from_gcs(bucket_reviews, predicted_reviews_file_name)

# Convert the predicted reviews CSV content to a DataFrame
from io import StringIO
review_df = pd.read_csv(StringIO(predicted_reviews_content), sep=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

# Normalize URLs in both DataFrames
product_df['url'] = product_df['url'].str.lower().str.rstrip('/').str.replace('http://', 'https://')
review_df['review_url_src'] = review_df['review_url_src'].str.lower().str.rstrip('/').str.replace('http://', 'https://')

# Merge product and review data
merged_df = pd.merge(product_df, review_df, left_on='url', right_on='review_url_src', how='left')

# Create JSON output format
merged_json = []
for product_url, group in merged_df.groupby('url'):
    product_info = {
        'product_name': group['name'].values[0],
        'price': group['price'].values[0],
        'rating_star': group['rating_star'].values[0],
        'rating_nb_reviews': group['rating_nb_reviews'].values[0],
        'product_link': product_url,
        'reviews': []
    }
    
    # Add reviews
    for _, review_row in group.iterrows():
        if pd.isna(review_row['review_stars']):
            continue  # Skip if there's no review data
        
        # Format the review_date
        formatted_review_date = format_date(review_row['review_date'])
        
        review_info = {
            'review_stars': review_row['review_stars'],
            'review_title': review_row['review_title'],
            'review_thoughts': review_row['review_thoughts'],
            'review_author': review_row['review_author'],
            'review_date': formatted_review_date,  # Use the new formatted date
            'review_verified': review_row['review_verified'],
            'review_tup': review_row['review_tup'],
            'review_tdown': review_row['review_tdown'],
            'review_collected_date': review_row['review_collected_date'],
            'sentiment_category': review_row['predicted_sentiment'],  # Use the new sentiment category field
            'keywords': review_row['keywords']  # Add keywords field
        }
        product_info['reviews'].append(review_info)
    
    merged_json.append(product_info)

# Convert the result into a JSON string
result_json_content = json.dumps(merged_json, indent=4)

# Save the JSON output to GCS
output_bucket_name = 'sublime_bucket_bis'
output_file_name = '10/reviews/merged_product_reviews.json'
upload_to_gcs(output_bucket_name, output_file_name, result_json_content)
