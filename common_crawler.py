"""普通的网络爬虫，简单的get请求，单线程爬取
利用关键词爬取百度收索词条"""

import requests
from bs4 import BeautifulSoup
import re
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[ %(asctime)s ] %(message)s',
)


class Crawler():
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'Connection': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        }

    def fix_text(self, text, repalce_list=(' ', '_', '\r', '\t', '\u3000', '百度图片搜索', '百度百科')):
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

        for i in repalce_list:
            text = text.replace(i, '')

        return text

    def get_html(self, url, **kwargs):
        try:
            html = self.session.get(url, headers=self.headers, **kwargs)
            if html.status_code != 200:
                logging.error('url: {} status code is {}'.format(html.url, html.status_code))
                return

            a = re.search('charset=["\']?([^\s"\'; ]+)', html.text)  # get html encoding automatically
            if a:
                html.encoding = a.group(1)
            else:
                html.encoding = 'utf8'
            return html

        except KeyboardInterrupt:
            exit(1)

        except Exception as e:
            logging.error('error   {} : {}'.format(url, e))
            logging.info('something error, perhaps crawler is limit, sleep 10 minutes')
            time.sleep(60 * 10)  # crawler is limited, so we stop 10 minute
            return

    def do_something(self, html, **kwargs):
        """do something after get the html"""
        soup = BeautifulSoup(html.text, 'lxml')
        crawl_list = soup.find_all('h3')
        if len(crawl_list) == 0:
            logging.info('empty crawl list  %s ', html.url)
            return

        for crawl in crawl_list:
            url = crawl.find('a')['href']
            html = self.get_html(url, **kwargs)
            if html:
                self.save_html(html.text, 'html_file/%f.html' % time.time())

    def save_html(self, text, save_path):
        logging.info('saving: %s' % save_path)
        with open(save_path, 'w', encoding='utf8') as f:
            f.write(text)

    def save(self, stream, save_path):
        logging.info('saving: %s' % save_path)
        with open(save_path, 'wb') as f:
            f.write(stream)

    def download_big_file(self, url, save_path, chunk_size=1024):
        with self.session.get(url, stream=True) as r:
            content_size = int(r.headers['content-length'])
            print(content_size)
            logging.info('saving: %s, total size: %f Mb' % (save_path, content_size / 1024))
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)

    def crawl(self, url, **kwargs):
        html = self.get_html(url, **kwargs)
        if html:
            self.do_something(html, **kwargs)


if __name__ == '__main__':
    crawler = Crawler()
    words = ['葡萄', '苹果', '雪梨', '黑莓']
    base_url = 'http://www.baidu.com/s?wd=%s&tn=monline_dg&ie=utf-8'
    for word in words:
        logging.info('crawling words: %s', word)
        url = base_url % word
        crawler.crawl(url, timeout=2)
