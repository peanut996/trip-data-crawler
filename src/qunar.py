from selenium import webdriver
from bs4 import BeautifulSoup
import lxml

QUNAR_URL = 'http://travel.qunar.com/travelbook/list/22-shanghai-299878/hot_ctime/1.htm '


if __name__ == '__main__':

    driver = webdriver.Edge()
    print("等待页面加载完成")
    driver.get(QUNAR_URL)
    print("页面加载完成")

    page = BeautifulSoup(driver.page_source, 'lxml')