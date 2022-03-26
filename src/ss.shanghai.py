#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/3/26 09:11
# @Author  : peanut996
# @File    : ss.shanghai.py
# @Usage   : 上海市文化和旅游局
import csv
import os
import random
from re import S

import time
from bs4 import BeautifulSoup
import bs4

import requests

from tool import format_str, get_url_number, headers

PAGE_TEMPLATE = "http://ss.shanghai.gov.cn/service/whlyj/search?q=%E6%97%85%E6%B8%B8&page={}&view=ywdt&contentScope=2&dateOrder=1&tr=5&dr=2019-12-01%20%E8%87%B3%202021-12-01&format=1&re=2"
HOST = "https://whlyj.sh.gov.cn"


def download_page(page: int):
    r = requests.get(PAGE_TEMPLATE.format(page))
    if not os.path.exists("html/ss.shanghai"):
        os.mkdir("html/ss.shanghai")
    with open("html/ss.shanghai/page-{}.html".format(page), "w", encoding="utf-8") as f:
        f.write(r.text)
        print("page-{} downloaded".format(page))


def download_all():
    for i in range(1, 32):
        time.sleep(random.randint(1, 3))
        download_page(i)


def read_page(page: int):
    with open("html/ss.shanghai/page-{}.html".format(page), "r", encoding="utf-8") as f:
        return f.read()


def read_content(number):
    with open("html/ss.shanghai/content/{}.html".format(number), "r", encoding="utf-8") as f:
        return f.read()


def parse_page_urls(h: str):
    soup = bs4.BeautifulSoup(h, "lxml")
    url_divs = soup.find_all("div", class_="url")
    title_divs = soup.find_all("div", class_="title")
    titles = [format_str(i.a["title"]) for i in title_divs]
    urls = [i.a['href'] for i in url_divs]
    numbers = [get_url_number(i) for i in urls]
    info = list(zip(numbers, titles, urls))
    return info


def parse_all_page_urls():
    infos = []
    for i in range(1, 32):
        h = read_page(i)
        infos.extend(parse_page_urls(h))
    return infos


def write_to_file(infos):
    if not os.path.exists("csv/ss.shanghai"):
        os.mkdir("csv/ss.shanghai")
    with open("csv/ss.shanghai/ss.shanghai.csv", "w", encoding="utf-8") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['序号', '标题', "链接"])
        csv_writer.writerows(infos)


def read_infos():
    infos = []
    with open("csv/ss.shanghai/ss.shanghai.csv", "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f)
        for i in csv_reader:
            infos.append(i)

    infos = infos[1:]
    return infos


def download_page_content(number, url, title):
    r = requests.get(url, headers=headers)
    if not os.path.exists("html/ss.shanghai/content"):
        os.mkdir("html/ss.shanghai/content")
    with open("html/ss.shanghai/content/{}.html".format(number), "w", encoding="utf-8") as f:
        f.write(r.text)
        print("{} downloaded".format(title))


def parse_page_content(number):
    h = read_content(number)
    if "404 Not Found" in h:
        return None, None
    soup = bs4.BeautifulSoup(h, "lxml")
    content = soup.find("div", class_="Article_content article")
    imgs = ", ".join(list(map(lambda s: HOST + s, [i["src"] for i in content.find_all("img")])))
    text = "".join([i.text for i in content.find_all("p")])
    if len(text) > 0:
        return text, imgs
    print("{} parse error, {}, {}".format(number,text,imgs))
    return None, None


if __name__ == "__main__":
    print("ss.shanghai.py")
    all_infos = []
    infos = read_infos()
    for number, title, url in infos:
        text, imgs = parse_page_content(number)
        if text is not None and imgs is not None:
            print("{} parsed".format(title))
            all_infos.append([number, title, url, text, imgs])

    print("all_infos parsed {}".format(len(all_infos)))
    with open("csv/ss.shanghai/ss.shanghai.content.csv", "w", encoding="utf-8") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['序号', '标题', "链接", "正文", "图片"])
        csv_writer.writerows(all_infos)
    print("all_infos written")
