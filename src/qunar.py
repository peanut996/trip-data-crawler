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
    'Cookie': "JSESSIONID=710DBEA4178D29941ED68B8D8BCDF06F; QN1=0000910034fc3c011190013c; qunar-assist={%22version%22:%2220211215173359.925%22%2C%22show%22:false%2C%22audio%22:false%2C%22speed%22:%22middle%22%2C%22zomm%22:1%2C%22cursor%22:false%2C%22pointer%22:false%2C%22bigtext%22:false%2C%22overead%22:false%2C%22readscreen%22:false%2C%22theme%22:%22default%22}; QN205=organic; QN277=organic; csrfToken=2CIcuuvSFBCT2ZAXoJMH5zuv7IzRQvK3; _i=RBTjeRkWfEHxqJowlLfddeucDEex; QN269=D973CAD0670311ECBEFDFA163E3ACAE1; Hm_lvt_c56a2b5278263aa647778d304009eafc=1640602678; fid=2d3cfb3a-0204-451d-8933-f1bc108e7172; viewbook=7716902|7716902|7716902|7716902|7716902; _vi=WAprBYwKuB6otGFFLSyA_u2xWpC_LtPsfoNGTzfd7Fnl9kAVk7gtkk5dvKVEbXyZts2oJsHSO9nyoX4SowP25Ub3Ixj33Coo5jCDxPbacLAQqcHrNacCsEAuJ7j9sRN0hTMp_hp9aCwZrxX60sHm0qh8C7qyBtaiQVUDoXkwl41Y; QN267=09273142896cc8c31f; Hm_lpvt_c56a2b5278263aa647778d304009eafc=1640614739; QN271=8db04eb6-ff9d-4e76-b310-962f0e8804b9"
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


def save_fail_html(html: str, number: str):
    if not os.path.exists("../html/qunar/fail"):
        os.makedirs("../html/qunar/fail")
    with open("../html/qunar/fail/{}.html".format(number), 'w', encoding='utf-8') as file:
        file.write(html)


def delete_fail_item(number):
    file_path = "../html/qunar/fail/{}.html".format(number)
    if os.path.exists(file_path):
        os.remove(file_path)
        print("删除失败文件成功: {}".format(number + ".html"))


def save_note(number: str, url: str):
    time.sleep(random.randint(1, 3))
    print("正在解析游记 {} ， 链接: {} ...".format(number, url))
    if os.path.exists("../html/qunar/note/{}.html".format(number)):
        print("游记{} 已经存在".format(number))
        delete_fail_item(number)
        return number
    retry_count = 0
    html = ""
    while retry_count < 20:
        try:
            print("游记 {} 第{}次尝试".format(number, retry_count + 1))
            secs = random.randint(3, 20)
            print("游记 {} 休眠 {} 秒".format(number, secs))
            time.sleep(secs)
            temp_proxy = get_proxy()
            r = requests.get(url, headers=headers, proxies=get_proxy_dict(temp_proxy), timeout=(3.05, 7.05))
            if r.status_code != 200 or is_bad_html(r.text):
                print("游记 {} 访问频率过高".format(number))
                save_fail_html(r.text, number)
                delete_proxy(temp_proxy)
                raise Exception("访问频率过高")
            html = r.text
            break
        except Exception as e:
            print("游记 {} 重试, 原因".format(number) + str(e))
            retry_count += 1

    if html == "":
        return number + "失败"
    print("爬取 {} 游记成功".format(number))
    delete_fail_item(number)
    with open("../html/qunar/note/{}.html".format(number), 'w', encoding='utf-8') as f:
        f.write(html)
    return number


def is_bad_html(html: str) -> bool:
    return html == '' or "你所在的IP访问频率过高" in html or "HTTP Status 404" in html or "Backend timeout" in html \
           or "您访问的页面不存在" in html or "cannot find token param" in html or "Blocked because of application" in html


if __name__ == '__main__':
    if not os.path.exists("../html/qunar/note"):
        os.makedirs("../html/qunar/note")
    pool = ThreadPoolExecutor(32)
    threads = []
    with open("../csv/qunar/qunar.csv", 'r', encoding='utf-8', newline='') as f:
        csv_reader = csv.reader(f)
        records = list(csv_reader)
        records = [r for r in records if len(r) > 0]
        records = records[1:]
        for i in range(len(records)):
            number, url, title = records[i]
            threads.append(pool.submit(save_note, number, url))

    fail_item = []
    for t in as_completed(threads):
        number = t.result()
        if "失败" in number:
            fail_item.append(number.replace("失败", ""))
        print("游记 {} 解析完成".format(number))
    with open("../csv/qunar/qunar_fail.csv", 'w', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(fail_item)
    print("解析数据完成")
    # print(get_proxy())
