import os
import pathlib
import shutil
import time
import db_query
import pymysql
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException
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
                             user='root',
                             password='**********',
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

    driver = uc.Chrome(options=options, user_data_dir=profile)
    try:
        driver.get('https://www.chemistwarehouse.com.au/')
        time.sleep(1)
        if driver.title == "Just a moment...":
            time.sleep(30)
            print('checking browser')
            driver.save_screenshot("photo/000.png")
            if driver.title == "Just a moment...":
                solve_captcha(driver)
            else:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".eupopup-button_1"))).click()
                driver.save_screenshot("photo/00.png")
        else:
            try:
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".eupopup-button_1"))).click()
            except TimeoutException:
                pass

        product_category_list = db_query.get_product_category_list()
        for category in product_category_list:
            product_category_id = category["id"]
            product_category_name = category["category_name"]
            product_category_url = category["category_url"]
            total_products_in_the_category = category["total_products"]
            driver.get(product_category_url)
            if driver.title == "Just a moment...":
                time.sleep(30)


            def recursive_category_all_page_visit():
                if driver.title == "Just a moment...":
                    time.sleep(30)
                all_products_in_this_page = driver.find_elements(By.CSS_SELECTOR, ".category-product")
                for product in all_products_in_this_page:
                    link = product.get_attribute("href")
                    print(link)
                    try:
                        with connection.cursor() as cursor:
                            sql = "INSERT INTO `product_url` (`category_name`, `product_url`) VALUES (%s, %s)"
                            cursor.execute(sql, (product_category_name, link))
                    except pymysql.IntegrityError:
                        print(f"IntegrityError: {link}")
                        pass
                    except Exception as e:
                        print(e)
                try:
                    WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Next']"))).click()
                    print('clicked next')
                    time.sleep(5)
                    recursive_category_all_page_visit()
                except TimeoutException:
                    print('no more page in this category')
                    return


            recursive_category_all_page_visit()
    except Exception as e:
        print(e)
    finally:
        driver.close()
        driver.quit()
