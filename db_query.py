import pymysql

connection = pymysql.connect(host='localhost',
                             user='mdbakibillah',
                             password='TalhaZubayer789*',
                             database='cwh_scrape',
                             charset='utf8mb4',
                             autocommit=True,
                             cursorclass=pymysql.cursors.DictCursor)


def get_product_category_list():
    with connection.cursor() as cursor:
        sql = "SELECT * FROM cwh_scrape.category;"
        cursor.execute(sql)
        product_category = cursor.fetchall()
        print(product_category)
    return product_category


def get_all_products_urls():
    with connection.cursor() as cursor:
        sql = "SELECT * FROM cwh_scrape.product_url where `done` = '0';"
        cursor.execute(sql)
        products_url = cursor.fetchall()
        # print(products_url)
    return products_url

