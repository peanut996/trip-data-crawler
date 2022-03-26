#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/3/26 11:14
# @Author  : peanut996
# @File    : gov.shanghai.py
# @Usage   : 上海一网半
import csv
import os.path
import random
import time
from bs4 import BeautifulSoup

import requests

from tool import get_url_number

url = "https://search.sh.gov.cn/searchResult"
HOST = "https://search.sh.gov.cn"

PATYLOAD_TEMPLATE = "text=%E6%97%85%E6%B8%B8&pageNo=1&newsPageNo={}&pageSize=20&resourceType=&channel=%E8%A6%81%E9%97%BB%E5%8A%A8%E6%80%81&category1=&category2=&category3=&category4=&category6=xwzx&category7=www.shanghai.gov.cn&sortMode=2&searchMode=1&timeRange=&accurateMode=&district=&street=&stealthy=1&searchText=%E6%97%85%E6%B8%B8"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:98.0) Gecko/20100101 Firefox/98.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://search.sh.gov.cn/search',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://search.sh.gov.cn',
    'Connection': 'keep-alive',
    'Cookie': 'AlteonP=AsDfYhvgEqzHD6QrbhV2cw$$; JSESSIONID=3C8A0399509A949C6A03837F989DBDDC; wondersLog_zwdt_sdk=%7B%22persistedTime%22%3A1648263636282%2C%22updatedTime%22%3A1648263636685%2C%22sessionStartTime%22%3A1648263636284%2C%22sessionReferrer%22%3A%22https%3A%2F%2Fsearch.sh.gov.cn%2Fsearch%22%2C%22recommend_code%22%3A2026726040743949%2C%22sessionUuid%22%3A2647699014288468%2C%22LASTEVENT%22%3A%7B%22eventId%22%3A%22wondersLog_pv%22%2C%22time%22%3A1648263636684%7D%2C%22deviceId%22%3A%22fad0de7a7aeccde87862b6b8b0820d6b-2517%22%2C%22costTime%22%3A%7B%22wondersLog_unload%22%3A1648263636685%7D%7D; searched=%E6%97%85%E6%B8%B8%23',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-origin',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'
}


def parse_page(page: str):
    html = BeautifulSoup(page, "lxml")
    result = html.find_all("div", class_="result result-elm")
    title = [i.a['title'] for i in result]
    url = [HOST + i.a['href'] for i in result]
    return list(zip(title, url))


def download_page(title, url):
    r = requests.get(url, headers=headers, allow_redirects=True)
    # number = get_url_number(r.request.url)
    html = r.text
    return html


def parse_content(h: str):
    soup = BeautifulSoup(h, "lxml")
    content = soup.find("div", class_="Article_content")
    if content is None:
        content = soup.find("div", class_="tab-pane active")
        text = content.p.span.text
        return text, ""
    texts = content.find_all("p")
    imgs = content.find_all("img")
    text = "".join([i.text for i in texts])
    img = ", ".join(list(map(lambda s: HOST + s, [i["src"] for i in imgs])))
    if len(text) > 0:
        return text, img
    return None, None


def read_page(page_number: int) -> str:
    with open("html/gov.shanghai/page/{}.html".format(page_number), "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    if not os.path.exists("html/gov.shanghai/page"):
        os.makedirs("html/gov.shanghai/page")
    all_info = []

    f = open("csv/gov.shanghai.csv", "w", encoding="utf-8")
    csv_writer = csv.writer(f)
    csv_writer.writerow(["序号", "标题", "内容", "图片"])
    for n in range(3,28):
        print("正在爬取第{}页".format(n))
        for t, u in parse_page(read_page(n)):
            text, img = parse_content(download_page(t, u))
            number = get_url_number(u)
            csv_writer.writerow([number, t, text, img])
            print("第{}页 编号{}写入完成".format(n, number))

    f.close()
    print("完成")



