import os
import csv
import ast
from google.cloud import storage

# Initialize GCS client
def get_gcs_client():
    return storage.Client()

def download_review_files_from_gcs(bucket_name, month):
    """Download all Python files from the GCS reviews folder and return a list of their content."""
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    reviews_folder = f"{month}/reviews/"
    
    review_data = []

    # List all files in the reviews folder
    blobs = list(bucket.list_blobs(prefix=reviews_folder))
    for blob in blobs:
        if blob.name.endswith('.py'):
            # Download the content of the Python review file
            content = blob.download_as_text()
            print(f"[LOG] Downloaded {blob.name} from GCS")
            
            # Evaluate the Python content (convert string into Python object)
            reviews = ast.literal_eval(content.split('= ')[1].strip())  # Assuming content is in the format: `reviews = [...]`
            review_data.extend(reviews)

    return review_data

def save_merged_csv_to_gcs(bucket_name, month, data, headers):
    """Save the merged data as a CSV in the GCS merged_reviews folder."""
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    
    # Define GCS path for the merged file
    gcs_path = f"{month}/merged_reviews/merged_reviews.csv"
    
    # Convert data to CSV string
    csv_content = ""
    csv_writer = csv.writer(csv_content, delimiter=';', quoting=csv.QUOTE_ALL)
    csv_writer.writerow(headers)  # Write headers
    csv_writer.writerows(data)  # Write review rows
    
    # Upload the merged CSV to GCS
    blob = bucket.blob(gcs_path)
    blob.upload_from_string(csv_content, content_type='text/csv')
    print(f"[LOG] Merged reviews saved to GCS at {gcs_path}")

def merge_reviews_from_gcs(bucket_name, month):
    """Download and merge review files from GCS, then upload the merged CSV back to GCS."""
    # Download all review files from GCS
    review_data = download_review_files_from_gcs(bucket_name, month)
    
    if not review_data:
        print("[LOG] No review data found.")
        return
    
    # Column headers for the CSV
    csv_headers = ["review_url_src", "review_stars", "review_title", "review_thoughts",
                   "review_author", "review_date", "review_verified", "review_tup", 
                   "review_tdown", "review_collected_date"]
    
    # Save merged data to GCS as a CSV file
    save_merged_csv_to_gcs(bucket_name, month, review_data, csv_headers)

if __name__ == "__main__":
    # Example usage:
    # bucket_name = "sublime_bucket_bis"
    # current_month = "10"  # Example for October
    
    bucket_name = "sublime_bucket_bis"  # Replace with your GCS bucket
    current_month = "10"  # Or use a dynamic method to get the current month
    
    merge_reviews_from_gcs(bucket_name, current_month)
