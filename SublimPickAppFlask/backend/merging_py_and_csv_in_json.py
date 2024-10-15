import pandas as pd
import ast
import json

# Step 1: Load and parse the Python file (url_dump_2024_09_23_17_12_10.py)
py_file_path = 'url_dump_2024_09_23_17_12_10.py'

# Read the Python file contents
with open(py_file_path, 'r', encoding='utf-8') as f:
    py_content = f.read()

# Extract the product data from the Python file
product_data_str = py_content.split("CATEGORIES = ")[1]
product_data = ast.literal_eval(product_data_str)  # Safely evaluate the Python list

# Convert product data to a DataFrame
product_df = pd.DataFrame(product_data, columns=['url', 'name', 'rating_star', 'rating_nb_reviews', 'price'])

# Step 2: Load review data from the CSV file (output_with_sentiments_keywords.csv)
csv_file_path = 'output_with_sentiments_keywords.csv'
review_df = pd.read_csv(csv_file_path, sep=';')

# Step 3: Normalize URLs in both DataFrames (lowercase and remove trailing slashes, ensure https)
product_df['url'] = product_df['url'].str.lower().str.rstrip('/').str.replace('http://', 'https://')
review_df['review_url_src'] = review_df['review_url_src'].str.lower().str.rstrip('/').str.replace('http://', 'https://')

# Step 4: Create a dictionary for the CSV file reviews
reviews_dict = {}

# Iterate through the review DataFrame and add each review to the corresponding URL
for index, row in review_df.iterrows():
    url = row['review_url_src']
    
    # If the URL is not in the dictionary, initialize an empty list
    if url not in reviews_dict:
        reviews_dict[url] = []
    
    # Append the review data as a dictionary of values to the dictionary
    reviews_dict[url].append({
        "review_stars": row['review_stars'],
        "review_title": row['review_title'],
        "review_thoughts": row['review_thoughts'],
        "review_author": row['review_author'],
        "review_date": row['review_date'],
        "review_verified": row['review_verified'],
        "review_tup": row['review_tup'],
        "review_tdown": row['review_tdown'],
        "review_collected_date": row['review_collected_date'],
        "predicted_sentiment": row['predicted_sentiment'],
        "sentiment_category": row['sentiment_category'],
        "keywords": row['keywords']
    })

# Step 5: Merge product data with the reviews dictionary based on URL
merged_output = []

for index, product_row in product_df.iterrows():
    product_url = product_row['url']
    product_name = product_row['name']
    
    # Find matching reviews for this product URL from the reviews_dict
    product_reviews = reviews_dict.get(product_url, [])
    
    # Merge the product information with the reviews for that product
    merged_output.append({
        'product_name': product_name,
        'price': product_row['price'],
        'rating_star': product_row['rating_star'],
        'rating_nb_reviews': product_row['rating_nb_reviews'],
        'product_link': product_url,
        'reviews': product_reviews  # List of associated reviews
    })

# Step 6: Print or save the merged output for review
for product in merged_output:
    print(f"Product: {product['product_name']}")
    print(f"URL: {product['product_link']}")
    print(f"Price: {product['price']}")
    print(f"Number of Reviews: {len(product['reviews'])}")
    for review in product['reviews']:
        print(f" - Review Title: {review['review_title']}, Author: {review['review_author']}")
    print("\n" + "="*50 + "\n")

# Step 7: Save the merged data to a JSON file
output_file_path = 'merged_product_reviews.json'
with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(merged_output, f, ensure_ascii=False, indent=4)

print(f"Merged product and review data saved to {output_file_path}")


# import pandas as pd
# import ast

# # Step 1: Load and parse the Python file as a string (reading it like a CSV)
# py_file_path = 'url_dump_2024_09_23_17_12_10.py'  # Replace with actual file path

# # Read the contents of the Python file
# with open(py_file_path, 'r', encoding='utf-8') as f:
#     py_content = f.read()

# # Step 2: Extract the product data from the Python file content
# # Look for the list inside the Python file by locating 'CATEGORIES' and parsing the list
# product_data_str = py_content.split("CATEGORIES = ")[1]  # Isolate the list of products
# product_data = ast.literal_eval(product_data_str)  # Safely evaluate the Python list

# # Convert the product data into a DataFrame
# product_df = pd.DataFrame(product_data, columns=['url', 'name', 'rating_star', 'rating_nb_reviews', 'price'])

# # Step 3: Load review data from the CSV file
# csv_file_path = 'output_with_sentiments_keywords.csv'  # Replace with actual file path
# review_df = pd.read_csv(csv_file_path, sep=';')

# # Step 4: Normalize URLs in both DataFrames (lowercase and remove trailing slashes)
# product_df['url'] = product_df['url'].str.lower().str.rstrip('/')
# review_df['review_url_src'] = review_df['review_url_src'].str.lower().str.rstrip('/')

# # Step 5: Merge the two DataFrames on the 'url' and 'review_url_src' columns
# merged_df = pd.merge(product_df, review_df, left_on='url', right_on='review_url_src', how='left')

# # Step 6: Save the merged DataFrame to a CSV file
# output_file_path = 'merged_output.csv'  # Replace with actual output path
# merged_df.to_csv(output_file_path, index=False)

# print("Merged file saved successfully.")
