import os.path
import random

import requests as requests
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import lxml

QUNAR_URL_TEMPLATE = 'http://travel.qunar.com/travelbook/list/22-shanghai-299878/hot_ctime/{}.htm'

def download_all_search_page():
    if not os.path.exists("../html/qunar/search"):
        os.makedirs("../html/qunar/search")
    for i in range(1, 189):
        url = QUNAR_URL_TEMPLATE.format(i)
        time.sleep(random.randint(1, 3))
        r = requests.get(url)
        with open("../html/qunar/search/{}.html".format(i), 'w') as f:
            f.write(r.text)
        print("page {} done".format(i))


if __name__ == '__main__':
    download_all_search_page()
