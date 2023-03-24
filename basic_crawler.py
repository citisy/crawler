import requests
import re
import time
import logging
import random
import traceback
import json
import os

logging.basicConfig(
    level=logging.INFO,
    format='[ %(asctime)s ] %(message)s',
)
DEBUG = False


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
                        logging.error(error_message)

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


def add_callback(callback=None, callback_args=None):
    """程序遇到异常后，不会退出，打印异常信息后继续往下执行"""

    def wrap2(func):
        def wrap(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                exit(1)
            except:
                if callback:
                    callback(callback_args)
                if DEBUG:
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

    @staticmethod
    def save_as_text(text, save_path):
        logging.info(f'saving: {save_path}')
        with open(save_path, 'w', encoding='utf8') as f:
            f.write(text)

    @staticmethod
    def save_as_file(stream, save_path):
        logging.info(f'saving: {save_path}')
        with open(save_path, 'wb') as f:
            f.write(stream)

    @staticmethod
    def save_as_json(js, save_path):
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

    @staticmethod
    def save_as_mongodb(js, collection):
        collection.update_one(js)

    def cache_by_json(self, path=None, root=None):
        """加载已经爬取的json，避免重复爬取"""
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

    @staticmethod
    def get_title(html):
        titles = re.findall('(?is)<title>(.*?)</title>', html)
        title = ''
        if titles:
            title = titles[0].replace('\n', '').replace('\r', '')

        return title

    def start4url(self, url, *args,
                  get_response_kwargs=dict(),
                  run_kwargs=dict(),
                  **kwargs):
        """推荐任务开始入口
        输入一个包含url列表的网页，解析网页获取url列表后，调用 run() 方法下达循环抓取任务
        默认调用 get_response() 获取响应
        :param url: 开始抓取的页面
        :param args: 自定义的参数
        :param kwargs: 网络请求用到的参数
        """
        response = self.get_response(url, *args, **get_response_kwargs)
        if response:
            return self.run(response, *args, **run_kwargs)

    def start4file(self, path=None, root=None, *args, **kwargs):
        """推荐任务开始入口
        输入一个包含url列表的文件或文件夹，解析文件获取url列表后，调用 run() 方法下达循环抓取任务"""
        if path:
            with open(path, 'r', encoding='utf8') as f:
                urls = f.read().split('\n')
                return self.run(urls, *args, **kwargs)
        if root:
            urls = []
            for file in os.listdir(root):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf8') as f:
                    urls += f.read().split('\n')

            return self.run(urls, *args, **kwargs)

    def run(self, obj, *args, **kwargs):
        """推荐任务开始入口
        输入一个包含url列表的元素，例如一个list型的url列表，一个包含url列表的文件、一个包含url列表的页面等
        然后从中解析得到url列表，进行循环抓取工作
        特别地，解析得到url列表的工作也已封装成 start4*() 系列函数，这些函数会默认调用 run() ，并传入一个list型的url列表。
        :param obj: 开始抓取的url返回的响应
        :param args: 自定义的参数
        :param kwargs: 网络请求时用到的参数
        """
        return obj

    @add_callback(lambda x: logging.error('Something wrong while crawling!'))
    def get_response(self, url: str, *args, auto_encoding=True, **kwargs) -> requests.models.Response or None:
        """获取一般页面html的方法
        默认有
        * 自动探测网页是否可以正常访问
        * 自动探测网页encoding
        * 请求失败重试3次
        * 连接超时失败时程序不中断退出
        等优化配置
        :param args: 自定义的参数
        :param kwargs: 网络请求时用到的参数
        """
        response = self.session.get(url, **kwargs)

        response.raise_for_status()

        if auto_encoding:
            a = re.search('charset=["\']?([^\s"\'; ]+)', response.text)  # get html encoding automatically

            if a:
                response.encoding = a.group(1)
            else:
                response.encoding = 'utf8'

        return response

    @add_delay()
    def repeat_crawl(self, url: str, *args, **kwargs):
        """解析重复抓取同一类型页面的方法
        默认添加延时0.2，建议在此添加页面解析的方法
        默认调用 get_repeat_response() 获取重复页面的html
        :param url: 需要抓取的url
        :param args: 自定义的参数
        :param kwargs: 网络请求时用到的参数
        """
        return self.get_repeat_response(url, *args, **kwargs)

    def get_repeat_response(self, url: str, *args, **kwargs):
        """重复获取同一类型页面html的方法
        默认调用 get_response() 获取页面html
        :param url: 需要抓取的url
        :param args: 自定义的参数
        :param kwargs: 网络请求时用到的参数
        """
        return self.get_response(url, *args, **kwargs)
