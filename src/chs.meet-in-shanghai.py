#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/3/26 16:49
# @Author  : peanut996
# @File    : chs.meet-in-shanghai.py
# @Usage   :
import csv
import os.path

import requests
from furl import furl
from bs4 import BeautifulSoup

from tool import headers

PAGE_URL = "https://chs.meet-in-shanghai.net/travel-news/newslist.php?page={}"


def download_all_pages():
    for i in range(25, 154):
        r = requests.get(PAGE_URL.format(i), headers=headers)
        r.encoding = "utf-8"
        with open("html/meet-in-shanghai/page/{}.html".format(i), "w", encoding="utf-8") as f:
            f.write(r.text)
        print("page {} downloaded".format(i))


def read_page(page_num: int):
    with open("html/meet-in-shanghai/page/{}.html".format(page_num), "r", encoding="utf-8") as f:
        return f.read()


def parse_page(page_num: int):
    page_html = read_page(page_num)
    soup = BeautifulSoup(page_html, "lxml")
    news_list = soup.find_all("div", class_="newsdiv")
    urls = [i.div.a["href"] for i in news_list]
    titles = [i.div.p.text for i in news_list]
    numbers = list(map(get_number_from_url, urls))
    return list(zip(numbers, titles, urls))


def parse_all_page():
    infos = []
    for i in range(25, 154):
        print("parsing page {}".format(i))
        infos += parse_page(i)
    with open("csv/meet-in-shanghai-page.csv", "w", encoding="utf-8") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["序号", "标题", "链接"])
        csv_writer.writerows(infos)
    print("meet-in-shanghai-page.csv saved")


def get_number_from_url(url: str):
    f = furl(url)
    return f.args["id"]


def read_page_info():
    all_infos = []
    with open("csv/meet-in-shanghai-page.csv", "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f)
        for i in csv_reader:
            all_infos.append(i)
    return all_infos[1:]


def download_all_news():
    all_infos = read_page_info()
    download_num = 0
    for number, title, url in all_infos:
        download_news(url)
        print("news {} downloaded {}/{}".format(number,
                                                download_num, len(all_infos)))


def download_news(url: str):
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    with open("html/meet-in-shanghai/news/{}.html".format(get_number_from_url(url)), "w", encoding="utf-8") as f:
        f.write(response.text)


def read_content_html(number: str):
    with open("html/meet-in-shanghai/news/{}.html".format(number), "r", encoding="utf-8") as f:
        return f.read()


def parse_content_html(number: str):
    html = read_content_html(number)
    soup = BeautifulSoup(html, "lxml")
    content = soup.find("div", class_="p_newstxt")
    if content is None:
        return None, None
    text = content.text
    imgs = [i["src"] for i in soup.find_all("img")]
    img = ",".join(imgs)
    return text, img


def parse_all_info():
    all_infos = read_page_info()
    parse_infos = []
    download_num = 0
    for number, title, url in all_infos:
        text, img = parse_content_html(number)
        if text is None:
            continue
        download_num += 1
        print("news {} parsed {}/{}".format(number,
                                            download_num, len(all_infos)))
        parse_infos.append([number, title, url, text, img])
    return parse_infos


def save_parsed_info(info):
    with open("csv/meet-in-shanghai-info.csv", "w", encoding="utf-8") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["序号", "标题", "链接", "内容", "图片"])
        csv_writer.writerows(info)


if __name__ == "__main__":
    if not os.path.exists("html/meet-in-shanghai/page"):
        os.makedirs("html/meet-in-shanghai/page")
    if not os.path.exists("html/meet-in-shanghai/news"):
        os.makedirs("html/meet-in-shanghai/news")
    # download_all_pages()
    # download_all_news()
    info = parse_all_info()
    save_parsed_info(info)
    # text, img = parse_content_html("18843")
    # print(text)
