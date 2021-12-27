import csv
import os.path
import random

import requests as requests
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import lxml

QUNAR_URL_TEMPLATE = 'http://travel.qunar.com/travelbook/list/22-shanghai-299878/hot_ctime/{}.htm'
QUNAR_NOTE_URL_TEMPLATE = "http://travel.qunar.com/travelbook/note/{}"


def download_all_search_page():
    if not os.path.exists("../html/qunar/search"):
        os.makedirs("../html/qunar/search")
    for i in range(1, 190):
        url = QUNAR_URL_TEMPLATE.format(i)
        time.sleep(random.randint(1, 3))
        r = requests.get(url)
        with open("../html/qunar/search/{}.html".format(i), 'w', encoding='utf-8') as f:
            f.write(r.text)
        print("page {} done".format(i))


def parse_search_page(page_number) -> tuple:
    """
    :param page_number:
    :return: numbers, urls, titles
    """
    page_fix = "../html/qunar/search/{}.html".format(page_number)
    html = ""
    with open(page_fix, 'r',encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'lxml')
    list = soup.find('ul', class_='b_strategy_list').find_all('li', class_="list_item")
    page_numbers = [get_page_number(i.h2.a['href']) for i in list]
    urls = [QUNAR_NOTE_URL_TEMPLATE.format(get_page_number(i.h2.a['href'])) for i in list]
    titles = [i.h2.a.text for i in list]
    return page_numbers, urls, titles


def get_page_number(path: str) -> str:
    return path.split("/")[2]


def parse_all_search_page():
    records = []
    for i in range(1, 190):
        print("正在解析第{}页。。。".format(i + 1))
        records.append(parse_search_page(i))
    print("解析数据完成")
    return records


if __name__ == '__main__':
    records = []
    for i in range(1, 190):
        print("正在解析第{}页。。。".format(i + 1))
        records.append(parse_search_page(i))

    print("解析数据完成")

    if not os.path.exists("../csv/qunar"):
        os.makedirs("../csv/qunar/")
    with open("../csv/qunar/qunar.csv", 'w', encoding="utf-8") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["序号", "链接", "标题"])
        for record in records:
            for i in range(len(record[0])):
                csv_writer.writerow([record[0][i], record[1][i], record[2][i]])
        print('写入完成')
