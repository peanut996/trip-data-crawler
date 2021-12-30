import os.path
from concurrent.futures import ThreadPoolExecutor, as_completed

import time

from tool import *

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.58"
}
CTRIP_SEARCH_URL_TEMPLATE = 'https://you.ctrip.com/travels/Shanghai2/t2-p{}.html'


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

if __name__ == '__main__':
    download_all_search_page()

