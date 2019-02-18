from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import os
import time
from general_crawler_by_count import *

firefox = './geckodriver'
browser = webdriver.Firefox(executable_path=firefox)
conn = MongoClient('127.0.0.1', 27017)  # also, u can use any other methods to save ur data
db = conn.citisy
collection = db.baidunews


def crawl(crawl_list):
    if len(crawl_list) == 0:
        logging.info('empty list : %s ', url)
    for crawl in crawl_list:
        try:
            crawl_url = crawl['href']
        except KeyError:
            continue
        if crawl_url[:4] != 'http':
            continue
        logging.info('        %s', crawl_url)
        html = get_html(crawl_url)
        if html is None:
            continue
        encoding = re.findall('charset=["\']?([^\s"\'; ]+)', html.text)  # get html encoding automatically
        try:
            html.encoding = encoding[0]
        except:
            html.encoding = 'utf8'
        soup = BeautifulSoup(html.text, 'lxml')
        ct = re.findall('(15[0-9]{8})[^0-9]', html.text)  # timestamp is a 10-bit number, and 2017 start with 15
        try:
            title = soup.head.title.text
        except:
            title = ''
        match = fix_html(html.text)
        if collection.find_one({'title': title}):  # if the passage exist, needn't download again
            continue
        ret = div(match)
        if len(ret) > 1:
            r = ''
            l = 0
            for i in ret:
                if l < len(i):
                    l = len(i)
                    r = i
        elif len(ret) == 0:
            logging.info('has no ret : %s !', url)
            continue
        else:
            r = ret[0]
        if len(ct) == 0:
            ct = ['']
        if len(r) == 0:
            logging.info(' has no r : %s !', url)
            continue
        collection.insert(
            {
                'url': crawl_url,
                'title': title,
                'ct': ct[0],
                'ret': r}
        )


while 1:
    base_url = 'http://news.sogou.com/'
    base_urls = ['', 'china.shtml', 'world.shtml', 'society.shtml', 'dangmei.shtml', 'mil.shtml', 'ent.shtml',
                 'business.shtml', 'sports.shtml', 'edu.shtml', 'house.shtml', 'women.shtml']
    for base in base_urls:
        print(base)
        browser.get(base_url + base)
        for i in range(5):
            ActionChains(browser).key_down(Keys.DOWN).perform()  # simulate the action of slide the web
            time.sleep(0.5)

        cookie_ = [item["name"] + "=" + item["value"] for item in browser.get_cookies()]
        cookie = ';'.join(item for item in cookie_)
        headers['cookie'] = cookie

        html = browser.page_source
        soup = BeautifulSoup(html, 'lxml')
        crawl_list = soup.find('div', class_='box-news').find_all('a')
        crawl(crawl_list)

    base_url = 'http://news.baidu.com/'
    base_urls = ['', 'guonei', 'guoji', 'mil', 'finance', 'ent', 'sports', 'internet', 'tech', 'game', 'lady', 'auto',
                 'house']
    for base in base_urls:
        print(base)
        browser.get(base_url + base)
        for i in range(5):
            ActionChains(browser).key_down(Keys.DOWN).perform()
            time.sleep(0.5)

        cookie_ = [item["name"] + "=" + item["value"] for item in browser.get_cookies()]
        cookie = ';'.join(item for item in cookie_)
        headers['cookie'] = cookie

        html = browser.page_source
        soup = BeautifulSoup(html, 'lxml')
        crawl_list = soup.find('div', id='body').find_all('a')
        crawl(crawl_list)

    logging.info('sleep 0.5 hour...')
    time.sleep(60 * 30)
