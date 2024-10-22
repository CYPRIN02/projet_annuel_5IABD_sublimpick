import pandas as pd
import csv
import ast
import json
from datetime import datetime

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

# Load product data from the Python file
with open('urls/url_dump_2024_10_07_13_22_09.py', 'r', encoding='utf-8') as f:
    py_content = f.read()

# Extract and evaluate the product data
product_data_str = py_content.split("CATEGORIES = ")[1]
product_data = ast.literal_eval(product_data_str)

# Convert product data to a DataFrame
product_df = pd.DataFrame(product_data, columns=['url', 'name', 'rating_star', 'rating_nb_reviews', 'price'])

# Load review data from the new CSV file (handling quotes and commas)
review_df = pd.read_csv(
    'output_folder/predicted_reviews_with_keywords.csv', 
    sep=',', 
    quotechar='"',  # Handle fields enclosed in double quotes
    quoting=csv.QUOTE_MINIMAL  # Handle quotes only when necessary
)

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

# Save JSON output
with open('output_folder/merged_product_reviews.json', 'w', encoding='utf-8') as outfile:
    json.dump(merged_json, outfile, indent=4)