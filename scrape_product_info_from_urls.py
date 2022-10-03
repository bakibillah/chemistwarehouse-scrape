import os
import pathlib
import shutil
import time
import db_query
import pymysql
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# from pyvirtualdisplay import Display for docker only
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from add_to_cert import add_to_cert
from solve_captcha import solve_captcha

# 39924,3|71499,2 # 966557887410

connection = pymysql.connect(host='localhost',
                             user='mdbakibillah',
                             password='TalhaZubayer789*',
                             database='cwh_scrape',
                             charset='utf8mb4',
                             autocommit=True,
                             cursorclass=pymysql.cursors.DictCursor)

if __name__ == '__main__':

    options = Options()
    # options.headless = True
    options.add_argument('--no-first-run --disable-notifications --no-service-autorun --password-store=basic')
    # Pass the argument 1 to allow and 2 to block
    # options.add_experimental_option("prefs", {
    #     "profile.default_content_setting_values.notifications": 1,
    #     "profile.default_content_setting_values.cookies": 1,
    #     "profile.block_third_party_cookies": "false"
    # })
    # options.add_argument('--headless')
    options.add_argument('--disable-notifications')
    profile = pathlib.Path.cwd().joinpath('profile_cwh')
    profile = str(profile)
    print(profile)
    # exists = os.path.exists(profile)
    # if exists:
    #     shutil.rmtree(profile, ignore_errors=True)
    #     time.sleep(.5)
    options.add_argument("--window-size=1920,1080")
    # options.add_argument("--headless=chrome")
    driver = uc.Chrome(options=options, user_data_dir=profile)
    try:
        driver.get('https://www.chemistwarehouse.com.au/')
        time.sleep(1)
        if driver.title == "Just a moment...":
            time.sleep(30)
            print('checking browser')

        all_products_urls = db_query.get_all_products_urls()

        for product in all_products_urls:
            try:
                url_id = product["id"]
                url = product["product_url"]
                print(url)
                driver.get(url)
                time.sleep(1)
                if driver.title == "Just a moment...":
                    print('captcha solving')
                    time.sleep(30)
                try:
                    title = driver.find_element(By.CSS_SELECTOR, ".product-name h1").text
                except NoSuchElementException:
                    title = ''
                try:
                    product_id = driver.find_element(By.CSS_SELECTOR, ".product-id").text
                    product_id = product_id.rsplit(":")[1]
                    product_id = product_id.strip()
                except NoSuchElementException:
                    product_id = ''
                try:
                    rating = driver.find_element(By.XPATH, "//span[@class='bv-rating']/span").text
                    rating = float(rating)
                except NoSuchElementException:
                    rating = None
                try:
                    number_of_rater = driver.find_element(By.XPATH, "//span[@class='bv-rating-ratio-count']/span").text
                    number_of_rater = number_of_rater.strip("()")
                    number_of_rater = int(number_of_rater)
                except NoSuchElementException:
                    number_of_rater = None
                try:
                    product_price = driver.find_element(By.XPATH, "//span[@class='product__price']").text
                except NoSuchElementException:
                    product_price = ''
                try:
                    image_url = driver.find_element(By.XPATH, "//div[@id='product_images']//a")
                    image_url = image_url.get_attribute("href")
                except NoSuchElementException:
                    image_url = ''
                try:
                    description = driver.find_element(By.CSS_SELECTOR, ".product-info-section.general-info:nth-child(3)").text
                except NoSuchElementException:
                    description = ''
                try:
                    categories = driver.find_elements(By.CSS_SELECTOR, ".breadcrumbs:nth-child(2) > a")
                    category = categories[1].text
                    sub_category = categories[2].text
                except NoSuchElementException:
                    category = ''
                    sub_category = ''
                # print(f"title:{title} \n product_id: {product_id} \nrating: {rating}\n number of rater: {number_of_rater}\n product price: {product_price}\n image_url: {image_url}\n description: {description}\n category: {category}\n sub_category: {sub_category}")
                try:
                    with connection.cursor() as cursor:
                        sql_insert = "INSERT INTO `products` (`link`, `title`, `price`, `sku`, `description`, " \
                                     "`image_url`, `Category`, `sub-category`, `average_rating`, `number_of_raters`) " \
                                     "VALUES (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s) "
                        cursor.execute(sql_insert, (url, title, product_price, product_id, description, image_url, category, sub_category, rating, number_of_rater))
                        update_product_url = f"UPDATE `product_url` SET `done` = '1' WHERE (`id` = '{url_id}');"
                        cursor.execute(update_product_url)
                except pymysql.IntegrityError:
                    print(f"Duplicate for url: {url}")
                    pass
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)
                continue

    except Exception as e:
        print(e)
    finally:
        driver.close()
        driver.quit()
