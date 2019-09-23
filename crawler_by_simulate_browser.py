"""模拟浏览器抓取百度新闻，堪称万能爬虫手段，唯一缺点就是慢，因为要渲染js
百度新闻的页面"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import time
import logging
from bs4 import BeautifulSoup
from general_extracter import Crawler


class SimulateBrowser(Crawler):
    def __init__(self):
        self.replace_name = ['|', '<', '>', '/', '\\', '?', '*', ':', '"']
        chrome = 'chromedriver'
        chrome_options = webdriver.ChromeOptions()
        chrome_options.headless = True  # quite mode
        self.browser = webdriver.Chrome(chrome, chrome_options=chrome_options)

    def do_something(self, html, **kwargs):
        soup = BeautifulSoup(html, 'lxml')
        crawl_list = soup.find('div', id='body').find_all('a')
        if len(crawl_list) == 0:
            logging.error('empty list!')

        for crawl in crawl_list:
            try:
                crawl_url = crawl['href']
            except KeyError:
                logging.error('can not found url!')
                continue

            if crawl_url[:4] != 'http':
                continue

            html = self.get_html(crawl_url)
            title = self.browser.title
            for r in self.replace_name:
                title = title.replace(r, '')
            self.save_html(html, 'html_file/%s.html' % title)
        self.browser.quit()     # quit browser

    def get_html(self, url, **kwargs):
        self.browser.get(url)
        for i in range(5):
            ActionChains(self.browser).key_down(Keys.DOWN).perform()  # simulate sliding down the web
            time.sleep(0.5)

        html = self.browser.page_source
        return html


if __name__ == '__main__':
    crawler = SimulateBrowser()
    url = 'http://news.baidu.com/'
    crawler.crawl(url)
