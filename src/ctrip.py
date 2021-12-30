import csv
import os.path
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

import time

from tool import *

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.58"
}
CTRIP_SEARCH_URL_TEMPLATE = 'https://you.ctrip.com/travels/Shanghai2/t2-p{}.html'
CTRIP_YOU_URL_TEMPLATE = 'https://you.ctrip.com{}'


def download_ctrip_search_page(page_num):
    url = CTRIP_SEARCH_URL_TEMPLATE.format(page_num)
    print('downloading page {}...'.format(page_num))
    retry_count = 0
    while retry_count < 20:
        proxy = get_proxy()
        try:

            res = requests.get(url, headers=headers, timeout=(3, 7))
            if res.status_code != 200:
                raise Exception('status code is {}'.format(res.status_code))
            print('page {} downloaded'.format(page_num))
            save_search_page(page_num, res.text)
            break
        except Exception as e:
            delete_proxy(proxy)
            time.sleep(random.randint(1, 2))
            retry_count += 1
            print('download page {} failed, retry count: {}, reason: {}'.format(page_num, retry_count, str(e)))


def save_search_page(page_num, html):
    print('saving page {}...'.format(page_num))
    with open("../html/ctrip/search/{}.html".format(page_num), 'w', encoding='utf-8') as f:
        f.write(html)


def download_all_search_page():
    if not os.path.exists("../html/ctrip/search"):
        os.makedirs("../html/ctrip/search")
    pool = ThreadPoolExecutor(max_workers=5)
    workers = []
    for i in range(1, 190):
        time.sleep(random.randint(1, 2))
        workers.append(pool.submit(download_ctrip_search_page, i))

    for worker in as_completed(workers):
        number = worker.result()
        print('page {} downloaded'.format(number))


def parse_search_page(page_num):
    with open("../html/ctrip/search/{}.html".format(page_num), 'r', encoding='utf-8') as f:
        html = f.read()
        soup = BeautifulSoup(html, 'lxml')
        items = soup.find_all('a', class_='journal-item cf')
        info = [(get_page_number(i['href']), i.div.find("dt").text, CTRIP_YOU_URL_TEMPLATE.format(i['href']),
                 i.find("i", class_="numview").text, i.find("i", class_="want").text,
                 i.find("i", class_="numreply").text) for i in
                items]
        return info


def get_page_number(url: str):
    return url.split("/")[3].replace(".html", "")


def save_parse_search_result_csv():
    records = []
    start = time.time()
    for i in range(1, 190):
        print('parsing page {}...'.format(i))
        records.append(parse_search_page(i))
    if not os.path.exists("../csv/ctrip"):
        os.makedirs("../csv/ctrip")
    with open("../csv/ctrip/search.csv", 'w', encoding='utf-8') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['page_number', 'title', 'url', "view", "like", "reply"])
        for record in records:
            for r in record:
                csv_writer.writerow(r)

    print('time cost: {}'.format(time.time() - start))


def read_all_search_result_from_csv():
    records = []
    with open("../csv/ctrip/search.csv", 'r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            records.append((row["page_number"], row["title"], row["url"], row["view"], row["like"], row["reply"]))
    return records


def save_suceess_note_page(note_number, text):
    if not os.path.exists("../html/ctrip/note/success"):
        os.makedirs("../html/ctrip/note/success")
    with open("../html/ctrip/note/success/{}.html".format(note_number), 'w', encoding='utf-8') as f:
        f.write(text)


def save_fail_note_page(note_number, text):
    if not os.path.exists("../html/ctrip/note/fail"):
        os.makedirs("../html/ctrip/note/fail")
    with open("../html/ctrip/note/fail/{}.html".format(note_number), 'w', encoding='utf-8') as f:
        f.write(text)


def delete_fail_note_page(note_number):
    if os.path.exists("../html/ctrip/note/fail/{}.html".format(note_number)):
        os.remove("../html/ctrip/note/fail/{}.html".format(note_number))


def download_note_page(note_number, url):
    print('downloading note {}...'.format(note_number))
    retry_count = 0
    while retry_count < 20:
        proxy = get_proxy()
        try:
            res = requests.get(url, headers=headers, timeout=(3.05, 7.05))
            if res.status_code != 200:
                save_fail_note_page(note_number, res.text)
                raise Exception('status code is {}'.format(res.status_code))
            print('note {} downloaded'.format(note_number))
            save_suceess_note_page(note_number, res.text)
            return note_number
        except Exception as e:
            time.sleep(random.randint(1, 2))
            retry_count += 1
            print('download note {} failed, retry count: {}, reason: {}'.format(note_number, retry_count, str(e)))
            delete_proxy(proxy)
    return note_number + "failed"


def download_all_note():
    pool = ThreadPoolExecutor(max_workers=16)
    workers = []
    records = read_all_search_result_from_csv()
    for number, _, url in records:
        workers.append(pool.submit(download_note_page, number, url))

    for worker in as_completed(workers):
        number = worker.result()
        if "failed" in number:
            print('note {} failed'.format(number))
        print('note {} downloaded'.format(number))


def parse_note_info(page_number, html):
    soup = BeautifulSoup(html, 'lxml')
    contents = [i.text for i in soup.find('div', class_='ctd_content').find_all('p')]
    imgs = [i["data-original"] for i in soup.find_all("img", class_="lary_1")]
    return page_number, "".join(contents), "\n".join(imgs)


def read_note_html(note_number):
    with open("../html/ctrip/note/success/{}.html".format(note_number), 'r', encoding='utf-8') as f:
        html = f.read()
        return html


def append_contents_img_to_csv(number):
    if not os.path.exists("../html/ctrip/note/success/{}.html".format(number)):
        print("note {} not found".format(number))
        return
    return parse_note_info(number, read_note_html(number))


def parse_note_info_to_fina_csv():
    start = time.time()
    records = read_all_search_result_from_csv()
    file_handler = open("../csv/ctrip/final.csv", 'w', encoding='utf-8', newline='')
    csv_writer = csv.writer(file_handler)
    csv_writer.writerow(['page_number', 'title', 'url', "view", "like", "reply", "contents", "imgs"])
    item = 0
    for number, title, url, view, like, reply in records:
        item += 1
        print("processing {} note {}".format(item, number))
        _, contents, imgs = append_contents_img_to_csv(number)
        csv_writer.writerow([number, title, url, view, like, reply, contents, imgs])
    print("done")
    print("cost {} seconds".format(time.time() - start))


if __name__ == '__main__':
    parse_note_info_to_fina_csv()
