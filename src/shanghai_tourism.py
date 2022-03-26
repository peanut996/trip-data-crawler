#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/3/26 20:00
# @Author  : peanut996
# @File    : shanghai_tourism.py
# @Usage   : 乐游上海
import csv
import os
import random
import time

import requests
from bs4 import BeautifulSoup

from tool import format_str

PAGE_TEMPLATE = "https://mp.weixin.qq.com/cgi-bin/appmsg?action=list_ex&begin={}&count=5&fakeid=&type=9&query=&token=&lang=zh_CN&f=json&ajax=1"
START = 201
# END = 1480
END = 250

CSV_FILE_RANGE = "151_200"

payload = {}
headers = {
    'authority': 'mp.weixin.qq.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Microsoft Edge";v="99"',
    'dnt': '1',
    'x-requested-with': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.46',
    'sec-ch-ua-platform': '"Windows"',
    'accept': '*/*',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&token=369563915&lang=zh_CN',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5',
}


def get_article_info(data):
    info = []
    for app_msg in data['app_msg_list']:
        title = app_msg['title']  # 文章标题
        link = app_msg['link']  # 文章链接
        info.append((title, link))
    return info


def download_page_info(page_number: int):
    response = requests.request(
        "GET", PAGE_TEMPLATE.format(page_number * 5), headers=headers, data=payload)

    data = response.json()
    if 'app_msg_list' not in data:
        return None
    return data


def download_save_page_info(page_number: int):
    print("正在下载第{}页".format(page_number))
    data = download_page_info(page_number)
    if data is None:
        return None
    info = get_article_info(data)
    return info


def save_all_info(info):
    with open("csv/shanghai_tourism_{}_{}.csv".format(START, END), "w", encoding="utf-8") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["标题", "列表"])
        csv_writer.writerows(info)


def download_all_page():
    all_info = []
    page = START
    f = open("csv/shanghai_tourism_{}.csv".format(CSV_FILE_RANGE),
             "w", encoding="utf-8")
    csv_writer = csv.writer(f)
    csv_writer.writerow(["标题", "列表"])

    while True and page <= END:
        time.sleep(3)
        info = download_save_page_info(page)
        if info is None:
            print("受到网络限制， 一小时后重试， page: {}".format(page))
            time.sleep(60 * 60)
            continue
        csv_writer.writerows(info)
        all_info += info
        page += 1

    f.close()


def read_csv():
    info = []
    with open("csv/shanghai_tourism_{}.csv".format(CSV_FILE_RANGE), "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            info.append(row)
    return info[1:]


def download_content(title, url):
    print("正在下载【{}..., url: {}".format(title, url))
    while True:
        try:
            r = requests.get(url, headers=headers)
            break
        except:
            print("网络超时， 正在重试， url: {}".format(url))
            time.sleep(1)
    with open("html/shanghai_tourism/{}.html".format(title), "w", encoding="utf-8") as f:
        f.write(r.text)
        print("【{}】----下载完成".format(title))


def download_all_content():
    infos = read_csv()
    infos = infos[360:]
    for index, info in enumerate(infos):
        title, url = info
        download_content(format_str(title), url)
        print("下载进度 {}/{}".format(index + 1, len(infos)))


def read_content_html(title: str):
    if not os.path.exists("html/shanghai_tourism/{}.html".format(title)):
        with open("html/shanghai_tourism/{}.html".format(format_str(title)), "w", encoding="utf-8") as f:
            return f.read()
    with open("html/shanghai_tourism/{}.html".format(title), "r", encoding="utf-8") as f:
        return f.read()


def parse_page_content(title: str):
    html = read_content_html(title)
    soup = BeautifulSoup(html, "lxml")
    content = soup.find("div", class_="rich_media_content")
    ps = content.find_all("p")
    imgs = content.find_all("img")
    text = "".join([p.text for p in ps])
    img = ",".join([img["data-src"] for img in imgs])
    return text, img


def parse_all_page_content():
    infos = read_csv()
    for index, info in enumerate(infos):
        title, url = info
        try:
            text, img = parse_page_content(title)
        except Exception as e:
            print(e)
            continue

        print("解析进度 {}/{}".format(index + 1, len(infos)))
        with open("csv/shanghai_tourism_content_{}.csv".format(CSV_FILE_RANGE), "a", encoding="utf-8") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow([title, text, img])

if __name__ == "__main__":

    # download_all_page()
    # download_all_content()
    parse_all_page_content()
