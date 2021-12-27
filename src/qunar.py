import csv
import os.path
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from tool import *

import requests as requests
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import lxml

proxy = {
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
}
QUNAR_URL_TEMPLATE = 'http://travel.qunar.com/travelbook/list/22-shanghai-299878/hot_ctime/{}.htm'
QUNAR_NOTE_URL_TEMPLATE = "http://travel.qunar.com/travelbook/note/{}"


def download_all_search_page():
    if not os.path.exists("../html/qunar/search"):
        os.makedirs("../html/qunar/search")
    for i in range(1, 190):
        url = QUNAR_URL_TEMPLATE.format(i)
        time.sleep(random.randint(5, 10))
        r = requests.get(url, proxy=proxy)
        if "你所在的IP访问频率过高" in r.text:
            print("访问频率过高，休眠5秒")
            time.sleep(10)
            r = requests.get(url, proxy=proxy)
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
    with open(page_fix, 'r', encoding='utf-8') as f:
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


def save_note(number: str, url: str):
    print("正在解析游记 {} ， 链接: {} ...".format(number, url))
    time.sleep(random.randint(1, 5))
    r = requests.get(url, headers=get_random_header(headers),proxies=proxy)
    if "你所在的IP访问频率过高" in r.text:
        print("访问频率过高， 停止")
        return number + "失败"
    with open("../html/qunar/note/{}.html".format(number), 'w', encoding='utf-8') as f:
        f.write(r.text)
    return number


if __name__ == '__main__':
    if not os.path.exists("../html/qunar/note"):
        os.makedirs("../html/qunar/note")
    pool = ThreadPoolExecutor(max_workers=1)
    threads = []
    with open("../csv/qunar/qunar.csv", 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        records = list(csv_reader)
        records = records[1:]
        for i in range(len(records)):
            number, url, title = records[i]
            threads.append(pool.submit(save_note, number, url))

    for t in as_completed(threads):
        number = t.result()
        print("游记 {} 解析完成".format(number))

    print("解析数据完成")
