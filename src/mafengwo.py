import csv
import os.path
import re
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import execjs
import requests
from bs4 import BeautifulSoup, Tag
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.edge.options import Options as EdgeOptions

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'Cookie': 'PHPSESSID=0gpvfb80qhnfc1n7o5gqpsqm16; mfw_uuid=61c5b478-5361-2488-23a5-e06736f11d4f; oad_n=a%3A3%3A%7Bs%3A3%3A%22oid%22%3Bi%3A1029%3Bs%3A2%3A%22dm%22%3Bs%3A15%3A%22www.mafengwo.cn%22%3Bs%3A2%3A%22ft%22%3Bs%3A19%3A%222021-12-24+19%3A52%3A24%22%3B%7D; __jsluid_h=13cea7414df644ce54a5de7a6540f80e; __omc_chl=; __omc_r=; __mfwc=direct; __mfwlv=1640346745; __mfwvn=1; uva=s%3A78%3A%22a%3A3%3A%7Bs%3A2%3A%22lt%22%3Bi%3A1640346745%3Bs%3A10%3A%22last_refer%22%3Bs%3A6%3A%22direct%22%3Bs%3A5%3A%22rhost%22%3Bs%3A0%3A%22%22%3B%7D%22%3B; __mfwurd=a%3A3%3A%7Bs%3A6%3A%22f_time%22%3Bi%3A1640346745%3Bs%3A9%3A%22f_rdomain%22%3Bs%3A0%3A%22%22%3Bs%3A6%3A%22f_host%22%3Bs%3A3%3A%22www%22%3B%7D; __mfwuuid=61c5b478-5361-2488-23a5-e06736f11d4f; Hm_lvt_8288b2ed37e5bc9b4c9f7008798d2de0=1640346747; bottom_ad_status=0; UM_distinctid=17dec49016fa32-0ecd7647597cb4-796f244e-1ea000-17dec49017058; __jsl_clearance=1640346837.606|0|U372H6t74qQH17j%2Fx3CnaHKzX48%3D; __mfwb=3cc0af210f16.1.direct; __mfwa=1640346745579.87723.2.1640346745579.1640349385644; __mfwlt=1640349385; Hm_lpvt_8288b2ed37e5bc9b4c9f7008798d2de0=1640349386; CNZZDATA30065558=cnzz_eid%3D576555278-1640338510-%26ntime%3D1640349310'
}
url = "http://www.mafengwo.cn/search/q.php?q=%E4%B8%8A%E6%B5%B7&t=notes&seid=&mxid=&mid=&mname=&kt=1"


def get_viewer_number(plain: str):
    return plain.strip().replace("浏览", "")


def get_info_from_child(child: any) -> tuple:
    title = child.h3.a.text.strip().replace("\n", "")
    note_url = child.h3.a['href']
    viewer = get_viewer_number(child.ul.li.text)
    return title, note_url, viewer


def get_all_notes(url: str) -> tuple:
    r = requests.get(url, headers=headers)
    html = r.text
    soup = BeautifulSoup(html, 'lxml')
    result = soup.find('div', class_='att-list').find('ul')
    childs = [child.find('div', class_="ct-text") for child in result.children if isinstance(child, Tag)]
    return map(get_info_from_child, childs)


def get_clearance(text: str):
    soup = BeautifulSoup(text, 'lxml')
    script = soup.find('script').text
    js_clearance = re.match(r"document.cookie=(.*);", script).group(1)
    clearance = execjs.eval(js_clearance)
    cookies = dict([l.split("=") for l in clearance.split(";")])
    return cookies


def get_html_from_note(note_url: str) -> tuple:
    s = requests.session()
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'Referer': note_url,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        "Cookie": '__jsluid_h=f8928711fac62217c555464ad855d214; PHPSESSID=idd2huh8c2c0u1qi1dv87da0r2; mfw_uuid=61c667c5-334e-3654-c47c-2cccda783168; oad_n=a%3A3%3A%7Bs%3A3%3A%22oid%22%3Bi%3A1029%3Bs%3A2%3A%22dm%22%3Bs%3A15%3A%22www.mafengwo.cn%22%3Bs%3A2%3A%22ft%22%3Bs%3A19%3A%222021-12-25+08%3A37%3A25%22%3B%7D; __mfwc=direct; __mfwlv=1640392646; __mfwvn=1; bottom_ad_status=1; Hm_lvt_8288b2ed37e5bc9b4c9f7008798d2de0=1640346747; uva=s%3A106%3A%22a%3A3%3A%7Bs%3A2%3A%22lt%22%3Bi%3A1640392646%3Bs%3A10%3A%22last_refer%22%3Bs%3A38%3A%22http%3A%2F%2Fwww.mafengwo.cn%2Fi%2F22509373.html%22%3Bs%3A5%3A%22rhost%22%3BN%3B%7D%22%3B; __mfwurd=a%3A3%3A%7Bs%3A6%3A%22f_time%22%3Bi%3A1640392646%3Bs%3A9%3A%22f_rdomain%22%3Bs%3A15%3A%22www.mafengwo.cn%22%3Bs%3A6%3A%22f_host%22%3Bs%3A3%3A%22www%22%3B%7D; __mfwuuid=61c667c5-334e-3654-c47c-2cccda783168; UM_distinctid=17def056479ceb-047af1cb76e00a-796f244e-1ea000-17def05647aa3e; __jsl_clearance=1640396329.09|0|%2F9Zcg9Oe2JWwKAidqSCkIQdW1so%3D; __mfwb=95c6c65edd09.1.direct; __mfwa=1640392646773.92992.2.1640392646773.1640396331660; __mfwlt=1640396331; Hm_lpvt_8288b2ed37e5bc9b4c9f7008798d2de0=1640396332; CNZZDATA30065558=cnzz_eid%3D235280131-1640382872-http%253A%252F%252Fwww.mafengwo.cn%252F%26ntime%3D1640393675'
    }
    s.headers.update(header)
    # first
    r = s.get(note_url)
    if r.status_code == 521:
        raise Exception("访问被拒绝 No Cookie")
        clearance = get_clearance(r.text)
        s.cookies.update(requests.utils.cookiejar_from_dict(clearance))
        # second
        r = s.get(note_url)
        print(r.status_code)
    html = r.text
    save_html_to_folder(note_url, html)
    return html


def save_html_to_folder(note_url: str, html: str):
    folder_prefix = "../html/mafengwo"
    if not os.path.exists(folder_prefix):
        os.makedirs(folder_prefix)
    with open(folder_prefix + "/" + get_number_from_url(note_url) + ".html", 'w', encoding='utf-8') as fp:
        fp.write(html)


def get_number_from_url(url: str) -> str:
    return re.match(r".*/i/(\d+)", url).group(1)


def handle(title, url, viewer):
    print("开始处理 {}, {}".format(title, url))
    number = get_number_from_url(url)
    print("睡眠3秒...")
    html = get_html_from_note(url)
    print("页面下载结束")
    save_html_to_folder(url, html)
    print("处理结束 {}, {}".format(title, url))
    return number, title, url, viewer


def save_to_csv(note_info: tuple):
    folder_prefix = "../csv/mafengwo"
    if not os.path.exists(folder_prefix):
        os.makedirs(folder_prefix)

    with open(folder_prefix + "/mafengwo.csv", 'w') as fp:
        note_info = [handle(title, url, viewer) for (title, url, viewer) in note_info]
        csv_writer = csv.writer(fp)
        csv_writer.writerow(["序号", '标题', "链接", "浏览量"])
        csv_writer.writerows(note_info)


def parse_note(html: str) -> tuple:
    def is_seq(css_class: str):
        seq_class = "_j_seqitem"
        return seq_class in css_class

    soup = BeautifulSoup(html, 'lxml')
    article = soup.find("div", attrs={"class": "vc_article"})
    seq_title = soup.find_all("div", class_="article_title _j_anchorcnt _j_seqitem")
    titles = [i.text.strip() for i in seq_title]
    seq_img = soup.find_all("div", class_="add_pic _j_anchorcnt _j_seqitem")
    imgs = [i.a.img["data-src"] for i in seq_img]
    seq_p = article.find_all("p", class_=is_seq)
    ps = [i.text.strip().replace(" ", "").replace("\n", "") for i in seq_p]
    return ''.join(titles), ''.join(ps), '\n'.join(imgs)


def is_title(css_class: str):
    return "article_title" in css_class


def is_img(css_class: str):
    return "add_pic" in css_class


def get_parse_from_number(number: int) -> tuple:
    with open("../html/mafengwo/" + number + ".html", 'r',encoding='utf-8') as file:
        return parse_note(file.read())


def seleium_to_get_html(url):
    options = EdgeOptions()
    options.add_argument('--headless')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-blink-features')
    driver = webdriver.Edge(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
    })
    driver.get(url)
    print("页面加载完成")
    for i in range(10):
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        ActionChains(driver).key_down(Keys.DOWN).perform()
        time.sleep(5)
    print('页面滚动完成')
    html = driver.page_source
    parse_note(html)
    save_html_to_folder(url, html)
    print('页面解析完成')
    driver.close()
    return get_number_from_url(url)


if __name__ == "__main__":
    with open('../csv/mafengwo/mafengwo.csv', 'r', encoding='utf-8') as file:
        with open('../csv/mafengwo/final_mafengwo.csv', 'w', encoding='utf-8') as final_file:
            csv_reader = csv.DictReader(file)
            fieldnames = ['编号', '标题', '链接', '浏览量', '小标题', '正文', '图片']
            csv_writer = csv.writer(final_file)
            csv_writer.writerow(fieldnames)
            for row in csv_reader:
                number = row['number']
                if not os.path.exists("../html/mafengwo/" + number + ".html"):
                    print("{} 不存在".format(number))
                    continue
                title = row['title']
                url = row['url']
                viewer = row['viewer']
                titles, ps, imgs = get_parse_from_number(number)
                csv_writer.writerow([number, title, url, viewer, titles, ps, imgs])

