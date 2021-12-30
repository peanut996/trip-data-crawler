import os.path
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
        # proxy = get_proxy()
        try:
            time.sleep(random.randint(1,2))
            res = requests.get(url, headers=headers,timeout=(3,7))
            if res.status_code != 200:
                raise Exception('status code is {}'.format(res.status_code))
            print('page {} downloaded'.format(page_num))
            save_search_page(page_num, res.text)
        except Exception as e:
            # delete_proxy(proxy)
            retry_count += 1
            time.sleep(5)
            print('download page {} failed, retry count: {}, reason: {}'.format(page_num, retry_count + 1, str(e)))

def save_search_page(page_num, html):
    print('saving page {}...'.format(page_num))
    with open("../html/ctrip/search/page{}.html".format(page_num), 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    if not os.path.exists("../html/ctrip/search"):
        os.makedirs("../html/ctrip/search")
    for i in range(1, 10):
        download_ctrip_search_page(i)

    print("hello world")
