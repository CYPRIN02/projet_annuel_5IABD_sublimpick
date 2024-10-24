import random
import time
import glob
import os
import csv
import pandas as pd

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from datetime import date as dt
from google.cloud import storage  # Import the GCS client


def upload_to_gcs(bucket_name, blob_name, content):
    """Uploads content to a specified Google Cloud Storage location."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(content)
    print(f"[LOG] File uploaded to GCS: {bucket_name}/{blob_name}")

# Function to save URLs to GCS
def save_urls_to_gcs(products_list, month):
    """Save collected URLs to a Python file and upload to GCS."""
    bucket_name = "sublime_bucket_bis"
    date_now = time.strftime("%Y_%m_%d_%H_%M_%S")
    file_name = f"url_dump_{date_now}.py"
    gcs_path = f"{month}/url/{file_name}"

    content = "CATEGORIES = [\n"
    for i, item in enumerate(products_list):
        content += str(item) + (",\n" if i != len(products_list) - 1 else "\n")
    content += "]"

    # Upload to GCS
    upload_to_gcs(bucket_name, gcs_path, content)

# Function to save reviews to GCS
def save_reviews_to_gcs(df, month):
    """Save reviews as a CSV and upload to GCS."""
    bucket_name = "sublime_bucket_bis"
    date_now = time.strftime("%Y_%m_%d_%H_%M_%S")
    file_name = f"reviews_dump_{date_now}.csv"
    gcs_path = f"{month}/reviews/{file_name}"

    # Convert DataFrame to CSV string
    content = df.to_csv(sep=';', index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)

    # Upload to GCS
    upload_to_gcs(bucket_name, gcs_path, content)


def check_if_lastPage_exist(driver, css_selector):
    try:
        driver.find_element(By.CSS_SELECTOR, css_selector)
    except:
        print("Last page reached.")
        pass
    return True


def check_if_element_exist(d, className):
    try:
        d.find_element(By.CLASS_NAME, className)
    except:
        return False
    return True

def ensure_reviews_are_loaded(driver):
    try:
        # Wait until the reviews section is visible
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="pr-review-list"] div[class="p-w-r"]'))
        )
        print("[LOG] Review section is loaded.")
    except TimeoutException:
        print("[ERROR] Review section not loaded. Check the page structure or loading time.")



## ------------------------- ##
## -------  U R L s  ------- ##
## ------------------------- ##

def collect_urls(driver, urls):
    # Create list of lists (url, name, rating_star, rating_nb_reviews, price)
    products_info = []
    # Define current page
    current_page = 1

    print("[LOG] Begin collecting product urls and product information.")
    # Collect url data
    for url in urls:
        # Go to the product list page
        driver.get(url)
        print(f"[LOG] Now scraping {url}")

        # Reject the cookies
        try:
            cookie_btn = WebDriverWait(driver, 15).until(EC.presence_of_element_located((
                By.CSS_SELECTOR, 'button[id="onetrust-reject-all-handler"]')))
            cookie_btn.click()
            print("[LOG] Click on the cookies button.")
            # time.sleep(random.uniform(1, 3))
        except:
            pass

        while True:
            # Collect products urls and information
            # HTML code
            html_page = BeautifulSoup(driver.page_source, 'html.parser')

            # Select the products
            products = html_page.select('li[class^="productListProducts"]')

            for product in products:

                # Initialize variables
                url = None
                name = None
                rating_star = None
                rating_nb_reviews = None
                price = None

                try:
                    url = 'https://www.dermstore.com' + product.a['href']
                    print(url)
                except:
                    pass

                try:
                    name = product.select_one('h3[class="productBlock_productName"]').text.strip()
                    # print(name)
                except:
                    pass

                try:
                    rating_star = product.select_one('div[class="productBlock_itemDetails_wrapper"] '
                                                     'div[class="pr-snippet-rating-decimal"]').text.strip()
                    rating_nb_reviews = product.select_one('div[class="productBlock_itemDetails_wrapper"] '
                                                           'div[class*="pr-category-snippet__total"]').text.split()[
                        0].strip()
                    print(rating_star)
                    print(rating_nb_reviews)
                except:
                    pass

                try:
                    price = product.select_one('span[class*="productBlock_priceValue"]').text.strip()
                    # print(price)
                except:
                    pass

                products_info.append((url, name, rating_star, rating_nb_reviews, price))

            print(f"[LOG] Page {current_page} done.")
            # if current_page == 5:
            #    break
            # else:
            current_page += 1

            # Find next page button and click
            try:
                next_pg = driver.find_element(By.CSS_SELECTOR,
                                              'div[class="responsiveProductListPage_bottomPagination-above-description"] '
                                              'nav[class="responsivePaginationPages"] '
                                              'ul[class="responsivePageSelectors"] '
                                              'li button[class*="paginationNavigationButtonNext"]')
                next_pg.click()
                # time.sleep(random.randint(1, 3))
            except:
                print("[LOG] End of product list page.")
                break

    # Convert list of lists to a pandas DataFrame
    df = pd.DataFrame(products_info)

    # Drop duplicates from the DataFrame
    unique_df = df.drop_duplicates()

    # Convert the DataFrame back to a list of lists
    aggregated_list = unique_df.values.tolist()

    # Stack urls into a py file
    stack_products_list(aggregated_list)
    return aggregated_list


## ------------------------- ##
## ----  R E V I E W S  ---- ##
## ------------------------- ##

def collect_reviews(driver, products_info):
    # Result list that will contain all the result
    res = []
    print("[LOG] Begin collecting datas.")
    for product_info in products_info:
        # If product has more than 15 reviews
        if product_info[3] is not None and product_info[3].isdigit() and int(product_info[3]) > 15:
            # Get the url from the list
            current_url = product_info[0]
            print(f"[LOG] Collecting reviews from {current_url}")

            # Go to the url
            driver.get(current_url)
            time.sleep(random.randint(1, 3))

            # Create an empty list to stack the collected reviews per page
            tmp = []

            # Refuse cookie
            try:
                cookie_btn = WebDriverWait(driver, 15).until(EC.presence_of_element_located((
                    By.CSS_SELECTOR, 'button[id="onetrust-reject-all-handler"]')))
                cookie_btn.click()
                print("[LOG] Click on the cookies button.")
            except:
                pass

            # Ensure reviews section is loaded
            ensure_reviews_are_loaded(driver)

            # Go to reviews section
            try:
                # Define current page
                current_page = 1

                # While next page button exist, collect reviews on current page
                while True:
                    try:
                        # Get the comments
                        comments = driver.find_elements(By.CSS_SELECTOR,
                                                        'div[id="pr-review-list"] div[class="p-w-r"] '
                                                        'section[id="pr-review-display"] div[class="pr-review"]')
                        for comment in comments:
                            try:
                                review_title = comment.find_element(By.CSS_SELECTOR,
                                                                    'h3[class*="pr-rd-review-headline"]'
                                                                    ).get_attribute('innerText').strip()
                                print(review_title)
                            except:
                                pass
                            try:
                                review_stars = str(comment.find_element(By.CSS_SELECTOR,
                                                                        'div[class="pr-rd-star-rating"] '
                                                                        'div[class="pr-snippet-rating-decimal"]'
                                                                        ).get_attribute('innerText')).strip()
                                print(review_stars)
                            except:
                                pass
                            try:
                                review_thoughts = comment.find_element(By.CSS_SELECTOR,
                                                                       'section[class*="pr-rd-description"] '
                                                                       'p[class="pr-rd-description-text"]'
                                                                       ).get_attribute('innerText').strip()
                                print(review_thoughts)
                            except:
                                pass
                            try:
                                review_date = comment.find_element(By.CSS_SELECTOR,
                                                                   'section[class*="pr-rd-description"] '
                                                                   'p[class="pr-rd-details pr-rd-author-submission-date"] '
                                                                   'span[data-datetime]'
                                                                   ).get_attribute('data-datetime').strip()
                                review_author = comment.find_element(By.CSS_SELECTOR,
                                                                     'section[class*="pr-rd-description"] '
                                                                     'p[class*="pr-rd-author-nickname"] > span '
                                                                     '> span:nth-of-type(2)'
                                                                     ).text.strip()
                                print(review_date)
                                print(review_author)
                            except:
                                pass
                            try:
                                if comment.find_element(By.CSS_SELECTOR,
                                                        'section[class*="pr-rd-description"] '
                                                        'p[class*="pr-verified_buyer"] span[class="pr-rd-badging-text"]'
                                                        ).get_attribute('innerText') == "Verified Buyer":
                                    review_verified = "True"
                                else:
                                    review_verified = "False"
                                print(review_verified)
                            except NoSuchElementException:
                                review_verified = "False"
                                print("[LOG] End of review section page. No verified button found.")
                                pass
                            except:
                                pass
                            try:
                                review_tup = comment.find_element(By.CSS_SELECTOR,
                                                                  'footer[class*="pr-rd-footer"] '
                                                                  'div[class*="pr-helpful-voting"] '
                                                                  'button[class="pr-helpful-btn pr-helpful-yes"] '
                                                                  'span[class="pr-helpful-count"]'
                                                                  ).get_attribute('innerText').strip()
                                print(review_tup)
                            except NoSuchElementException:
                                print("[LOG] End of review section page. No thumbs up found.")
                                pass
                            except:
                                pass
                            try:
                                review_tdown = comment.find_element(By.CSS_SELECTOR,
                                                                    'footer[class*="pr-rd-footer"] '
                                                                    'div[class*="pr-helpful-voting"] '
                                                                    'button[class="pr-helpful-btn pr-helpful-no"] '
                                                                    'span[class="pr-helpful-count"]'
                                                                    ).get_attribute('innerText').strip()
                                print(review_tdown)
                            except:
                                pass

                            review_url_src = current_url
                            review_collected_date = dt.today().strftime('%Y-%m-%d')
                            tmp.append((review_url_src, review_stars, review_title, review_thoughts, review_author,
                                        review_date, review_verified, review_tup, review_tdown, review_collected_date))

                        print(f"[LOG] Page {current_page} done.")
                        print(tmp)

                        # Stop at x page
                        # if current_page == 5:
                        #    break
                        # else:
                        #    current_page += 1

                        # If the first 100 reviews have been collected, save then break
                        if len(tmp) > 1000:
                            n_reviews = len(tmp)
                            res.append(tmp)
                            print(f"[DEBUG] Reviews collected: {tmp}")
                            if not tmp:
                                print("[ERROR] No reviews collected!")
                            stack_reviews_list(tmp)
                            print(f"[LOG] Saved {n_reviews} reviews.")
                            break
                        else:
                            current_page += 1

                        try:
                            next_page = driver.find_element(By.CSS_SELECTOR,
                                                            'footer[class="pr-rd-main-footer"] div[class="pr-rd-pagination"] '
                                                            'a[class*="pr-rd-pagination-btn--next"]'
                                                            )
                            next_page.click()
                            print("[LOG] Successfully navigated to the next page.")
                            time.sleep(random.randint(1, 5))
                        except NoSuchElementException:
                            print("[LOG] End of review section page. No 'Next' button found.")
                        except ElementClickInterceptedException:
                            print("[ERROR] 'Next' button click intercepted. Possible overlay or popup issue.")
                            break
                        except TimeoutException:
                            print("[ERROR] Timeout while waiting for next page to load. Possibly a page loading issue.")
                            break
                        except:
                            print("[LOG] End of review section page.")
                            print(f"[DEBUG] Reviews collected: {tmp}")
                            if not tmp:
                                print("[ERROR] No reviews collected!")
                            stack_reviews_list(tmp)
                            n_reviews = len(tmp)
                            res.append(tmp)
                            print(f"[LOG] Saved {n_reviews} reviews.")
                            break
                    except:
                        print("oops smth is wrong")
                        break

            finally:
                # Notify when done
                print(f"[LOG] Reviews from {current_url} has been collected.")
                time.sleep(random.randint(1, 3))
        else:
            pass
    return res


def stack_products_list(products_list):
    """Stacks products list into a py file
    """

    url_path = os.path.join(os.curdir, 'urls')
    date_now = str(time.strftime('%Y_%m_%d_%H_%M_%S'))
    url_file_path = os.path.join(url_path, 'url_dump_' + date_now + '.py')

    with open(url_file_path, 'w', encoding='utf-8') as file:
        file.write('CATEGORIES = [ \n')
        for i, item in enumerate(products_list):
            if i != len(products_list) - 1:
                file.write(str(item) + ',' + '\n')
            else:
                file.write(str(item) + '\n')
        file.write(']')


def aggregate_urls():
    """Gathers all the python files containing tuples from a specified folder.
    It aggregates them into a single text file.
    """

    print("[LOG] Start the aggregation of the urls.")

    date_now = str(time.strftime('%Y_%m_%d_%H_%M_%S'))

    # Path to the folder containing the text files
    urls_path = os.path.join(os.curdir, 'urls')

    # Path to the output text file
    merged_urls_path = os.path.join(os.curdir, 'merged_urls')
    merged_url_res = os.path.join(merged_urls_path, 'merged_urls' + '.txt')

    # List to store the stacked tuples
    stacked_tuples = []

    # Iterate over each text file in the folder
    for file_path in glob.glob(os.path.join(urls_path, '*.py')):
        with open(file_path, 'r') as file:
            # Read each line in the text file
            for line in file:
                # Remove leading/trailing whitespace and newline characters
                line = line.strip()

                # Append the tuple to the stacked_tuples list
                stacked_tuples.append(eval(line))

    # Convert list of lists to a pandas DataFrame
    df = pd.DataFrame(stacked_tuples)

    # Drop duplicates from the DataFrame
    unique_df = df.drop_duplicates()

    # Convert the DataFrame back to a list of lists
    stacked_tuples_cleaned = unique_df.values.tolist()

    # Write the stacked tuples to the output text file
    with open(merged_url_res, 'w', encoding='utf-8') as file:
        for tuple_data in stacked_tuples_cleaned:
            file.write(str(tuple_data) + '\n')

    print("[LOG] The aggregation of the urls is finished.")


def stack_reviews_list(reviews_list):
    print(f"[DEBUG] Reviews list passed to function: {reviews_list}")
    review_path = os.path.join(os.curdir, 'reviews')
    os.makedirs(review_path, exist_ok=True)
    date_now = str(time.strftime('%Y_%m_%d_%H_%M_%S'))
    review_file_path = os.path.join(review_path, 'review_dump_' + date_now + '.py')
    with open(review_file_path, 'w', encoding='utf-8') as file:
        file.write('REVIEWS = [ \n')
        for i, item in enumerate(reviews_list):
            if i != len(reviews_list) - 1:
                file.write(str(item) + ',' + '\n')
            else:
                file.write(str(item) + '\n')
        file.write(']')
    print(f"[DEBUG] File saved: {review_file_path}")


def aggregate_reviews():
    """Gathers all the text files containing tuples from a specified folder.
    It aggregates them into a single py file.
    """

    print("[LOG] Start the aggregation of the reviews.")

    date_now = str(time.strftime('%Y_%m_%d_%H_%M_%S'))

    # Path to the folder containing the text files
    reviews_path = os.path.join(os.curdir, 'reviews')

    # Path to the output text file
    merged_reviews_path = os.path.join(os.curdir, 'merged_reviews')
    merged_reviews_res = os.path.join(merged_reviews_path, 'merged_reviews_' + date_now + '.py')

    # List to store the stacked tuples
    stacked_tuples = []

    # Iterate over each text file in the folder
    for file_path in glob.glob(os.path.join(reviews_path, '*.txt')):
        with open(file_path, 'r') as file:
            # Read each line in the text file
            for line in file:
                # Remove leading/trailing whitespace and newline characters
                line = line.strip()

                # Append the tuple to the stacked_tuples list
                stacked_tuples.append(eval(line))

    # Convert list of lists to a pandas DataFrame
    df = pd.DataFrame(stacked_tuples)

    # Drop duplicates from the DataFrame
    unique_df = df.drop_duplicates()

    # Convert the DataFrame back to a list of lists
    stacked_tuples_cleaned = unique_df.values.tolist()

    # Write the stacked tuples to the output text file
    with open(merged_reviews_res, 'w', encoding='utf-8') as file:
        for tuple_data in stacked_tuples_cleaned:
            file.write(str(tuple_data) + '\n')

    print("[LOG] The aggregation of the reviews is finished.")


def retreive_urls():
    # Path to the output text file
    merged_urls_path = os.path.join(os.curdir, 'merged_urls')
    merged_url_res = os.path.join(merged_urls_path, 'merged_urls' + '.txt')

    urls_list = []
    with open(merged_url_res, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            try:
                # Evaluate the line as a Python expression to convert it into a list
                parsed_list = eval(line)

                if isinstance(parsed_list, list):
                    urls_list.append(parsed_list)
                else:
                    print(f"Failed to convert line to list: {line}")
            except SyntaxError:
                print(f"Failed to convert line to list: {line}")

    return urls_list


def save_as_input_file(df):
    # Path to the input directory
    exchange_path = os.path.join(os.curdir, 'exchange')
    input_path = os.path.join(exchange_path, 'input')

    # Define the file path
    file_path = os.path.join(input_path, 'input.csv')

    # df.to_csv()
    df.to_csv(file_path, sep=';', index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)
