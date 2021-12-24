import requests
from bs4 import BeautifulSoup, Tag
import csv

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'Cookie': 'PHPSESSID=0gpvfb80qhnfc1n7o5gqpsqm16; mfw_uuid=61c5b478-5361-2488-23a5-e06736f11d4f; oad_n=a%3A3%3A%7Bs%3A3%3A%22oid%22%3Bi%3A1029%3Bs%3A2%3A%22dm%22%3Bs%3A15%3A%22www.mafengwo.cn%22%3Bs%3A2%3A%22ft%22%3Bs%3A19%3A%222021-12-24+19%3A52%3A24%22%3B%7D; __jsluid_h=13cea7414df644ce54a5de7a6540f80e; __omc_chl=; __omc_r=; __mfwc=direct; __mfwlv=1640346745; __mfwvn=1; uva=s%3A78%3A%22a%3A3%3A%7Bs%3A2%3A%22lt%22%3Bi%3A1640346745%3Bs%3A10%3A%22last_refer%22%3Bs%3A6%3A%22direct%22%3Bs%3A5%3A%22rhost%22%3Bs%3A0%3A%22%22%3B%7D%22%3B; __mfwurd=a%3A3%3A%7Bs%3A6%3A%22f_time%22%3Bi%3A1640346745%3Bs%3A9%3A%22f_rdomain%22%3Bs%3A0%3A%22%22%3Bs%3A6%3A%22f_host%22%3Bs%3A3%3A%22www%22%3B%7D; __mfwuuid=61c5b478-5361-2488-23a5-e06736f11d4f; Hm_lvt_8288b2ed37e5bc9b4c9f7008798d2de0=1640346747; bottom_ad_status=0; UM_distinctid=17dec49016fa32-0ecd7647597cb4-796f244e-1ea000-17dec49017058; __jsl_clearance=1640346837.606|0|U372H6t74qQH17j%2Fx3CnaHKzX48%3D; __mfwb=3cc0af210f16.1.direct; __mfwa=1640346745579.87723.2.1640346745579.1640349385644; __mfwlt=1640349385; Hm_lpvt_8288b2ed37e5bc9b4c9f7008798d2de0=1640349386; CNZZDATA30065558=cnzz_eid%3D576555278-1640338510-%26ntime%3D1640349310'
}
url = "http://www.mafengwo.cn/search/q.php?q=%E4%B8%8A%E6%B5%B7&t=notes&seid=&mxid=&mid=&mname=&kt=1"


def get_viewer_number(plain: str):
    return plain.strip().replace("浏览", "")


def get_info_from_child(child):
    title = child.h3.a.text
    note_url = child.h3.a['href']
    viewer = get_viewer_number(child.ul.li.text)
    return title, note_url, viewer


if __name__ == "__main__":
    r = requests.get(url, headers=headers)
    html = r.text
    soup = BeautifulSoup(html, 'lxml')
    result = soup.find('div', class_='att-list').find('ul')
    childs = [child.find('div', class_="ct-text") for child in result.children if isinstance(child, Tag)]
    result = map(get_info_from_child, childs)

    with open("mafengwo.csv", 'w', encoding='utf-8') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['标题', '链接', '浏览量'])
        csv_writer.writerows(result)
