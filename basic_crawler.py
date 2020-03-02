import requests
from bs4 import BeautifulSoup
import re
import time
import logging
import random
import traceback
import json
import os
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format='[ %(asctime)s ] %(message)s',
)


def add_try(count=2,
            wait=600,
            error_message='something error, perhaps crawler is limit, sleep 10 minutes',
            err_type=ConnectionError):
    def wrap2(func):
        def wrap(*args, **kwargs):
            i = 0
            while i < count:
                try:
                    return func(*args, **kwargs)
                except err_type as e:
                    i += 1
                    logging.error(e)

                    if error_message:
                        logging.info(error_message)

                    logging.info(f'{i}th try!')
                    time.sleep(wait)

        return wrap

    return wrap2


def add_delay(secs=1, thresold=0.2):
    def wrap2(func):
        def wrap(*args, **kwargs):
            r = func(*args, **kwargs)
            time.sleep(random.uniform(secs - thresold, secs + thresold))  # 模拟访问频率
            return r

        return wrap

    return wrap2


def add_callback(callback=None):
    """程序遇到异常后，不会退出，打印异常信息后继续往下执行"""

    def wrap2(func):
        def wrap(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                if callback:
                    callback()
                traceback.print_exc()

        return wrap

    return wrap2


class Crawler:
    """自定义的爬虫框架"""

    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'Connection': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        }
        self.session.headers.update(self.headers)
        self.cache_dic = dict()

    def fix_text(self, text, replace_list=None):
        # replace escape character
        text = (text.replace("&quot;", "\"").replace("&ldquo;", "“").replace("&rdquo;", "”")
                .replace("&middot;", "·").replace("&#8217;", "’").replace("&#8220;", "“")
                .replace("&#8221;", "\”").replace("&#8212;", "——").replace("&hellip;", "…")
                .replace("&#8226;", "·").replace("&#40;", "(").replace("&#41;", ")")
                .replace("&#183;", "·").replace("&amp;", "&").replace("&bull;", "·")
                .replace("&lt;", "<").replace("&#60;", "<").replace("&gt;", ">")
                .replace("&#62;", ">").replace("&nbsp;", "").replace("&#160;", " ")
                .replace("&tilde;", "~").replace("&mdash;", "—").replace("&copy;", "@")
                .replace("&#169;", "@").replace("♂", ""))

        replace_list = replace_list or (' ', '_', '\r', '\t', '\u3000')
        for i in replace_list:
            text = text.replace(i, '')

        return text

    def save_as_text(self, text, save_path):
        logging.info(f'saving: {save_path}')
        with open(save_path, 'w', encoding='utf8') as f:
            f.write(text)

    def save_as_file(self, stream, save_path):
        logging.info(f'saving: {save_path}')
        with open(save_path, 'wb') as f:
            f.write(stream)

    def save_as_json(self, js, save_path):
        logging.info(f'saving: {save_path}')
        with open(save_path, 'w', encoding='utf8') as f:
            json.dump(js, f, indent=4, ensure_ascii=False)

    def save_as_big_file(self, url, save_path, chunk_size=1024):
        with self.session.get(url, stream=True) as r:
            content_size = int(r.headers['content-length'])
            logging.info('saving: %s, total size: %f Mb' % (save_path, content_size / 1024 / 1024))
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)

    def save_as_mongodb(self, js, collection):
        collection.update_one(js)

    def cache_by_json(self, path=None, root=None):
        if path:
            logging.info(f'saving: {path}')
            try:
                with open(path, 'r', encoding='utf8') as f:
                    self.cache_dic.update(json.load(f))
            except Exception as e:
                logging.error(f'when cache file: {path} meet error: {e}')
                return

        if root:
            for file in os.listdir(root):
                path = os.path.join(root, file)
                logging.info(f'saving: {path}')
                try:
                    with open(path, 'r', encoding='utf8') as f:
                        self.cache_dic.update(json.load(f))
                except Exception as e:
                    logging.error(f'when cache file: {path} meet error: {e}')
                    continue

    def get_title(self, html):
        titles = re.findall('(?is)<title>(.*?)</title>', html)
        title = ''
        if titles:
            title = titles[0].replace('\n', '').replace('\r', '')

        return title

    def start4url(self, url, *args, **kwargs):
        """
        :param url: 开始抓取的页面
        :param args: 自定义的参数
        :param kwargs: 网络请求用到的参数
        """
        response = self.get_response(url, *args, **kwargs)
        if response:
            self.run(response, *args, **kwargs)

        return response

    @add_try()
    @add_callback()
    def get_response(self, url: str, *args, **kwargs) -> requests.models.Response:
        try:
            response = self.session.get(url, **kwargs)
            if response.status_code != 200:
                logging.error('url: {} status code is {}'.format(response.url, response.status_code))
                return

            a = re.search('charset=["\']?([^\s"\'; ]+)', response.text)  # get html encoding automatically

            if a:
                response.encoding = a.group(1)
            else:
                response.encoding = 'utf8'
            return response

        except KeyboardInterrupt:
            exit(1)

    def run(self, response: requests.models.Response, *args, **kwargs):
        """do something after get the html
        :param response: 开始抓取的url返回的响应
        :param args: 自定义的参数
        :param kwargs: 网络请求时用到的参数
        :return:
        """
        return response

    @add_delay()
    def repeat_crawl(self, url: str, *args, **kwargs):
        """
        :param url: 需要抓取的url
        :param args: 自定义的参数
        :param kwargs: 网络请求时用到的参数
        :return: default return get_repeat_html()
        """
        return self.get_repeat_response(url, *args, **kwargs)

    def get_repeat_response(self, url: str, *args, **kwargs):
        """
        :param url: 需要抓取的url
        :param args: 自定义的参数
        :param kwargs: 网络请求时用到的参数
        :return: default return get_html()
        """
        return self.get_response(url, *args, **kwargs)


class BaiduCrawler(Crawler):
    def run(self, response, *args, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        crawl_list = soup.find_all('h3')
        if not crawl_list:
            logging.info('empty crawl list  %s ', response.url)
            return

        for crawl in tqdm(crawl_list):
            url = crawl.find('a')['href']
            self.repeat_crawl(url, *args, **kwargs)


if __name__ == '__main__':
    """普通的网络爬虫，简单的get请求，单线程爬取，利用关键词爬取百度收索词条"""
    crawler = BaiduCrawler()
    words = ['葡萄', '苹果', '雪梨', '黑莓']
    base_url = 'http://www.baidu.com/s?wd=%s&tn=monline_dg&ie=utf-8'
    for word in words:
        logging.info('crawling words: %s', word)
        url = base_url % word
        crawler.start4url(url, timeout=2)
