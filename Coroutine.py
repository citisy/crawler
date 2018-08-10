from queue import Queue
import requests
import time
import os
from bs4 import BeautifulSoup
import re
import gevent
from gevent import monkey

monkey.patch_all()


class coroutine_crawler(object):
    def __init__(self):
        self.q = Queue()
        self.headers = {
            'Connection': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/6.1 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }
        max_retries = 5
        self.session = requests.Session()
        requests.adapters.HTTPAdapter(max_retries=max_retries)
        self.base_url = 'http://www.baidu.com/s?wd='
        self.repalce_list = [' ', '_', '\n', '百度图片搜索', '百度百科']
        self.word_list = []

    def run(self, word_list):
        for word in word_list:
            word = str(word)
            print(word)
            ret = {}
            url = self.base_url + word + '&tn=monline_dg&ie=utf-8'
            try:
                html = self.session.get(url, headers=self.headers, timeout=3)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(e)
                time.sleep(60 * 10)
                continue
            html.encoding = 'utf8'
            soup = BeautifulSoup(html.text, 'lxml')
            crawl_list = soup.find_all('h3', class_='t c-gap-bottom-small')
            ret['word'] = word
            ret['sen'] = []
            for crawl in crawl_list:
                crawl_url = crawl.find('a')['href']
                try:
                    crawl_html = self.session.get(crawl_url, headers=self.headers, timeout=3)
                except Exception as e:
                    print(e)
                    continue
                crawl_html.encoding = 'utf8'
                match = re.findall('[^。？！>"\']*' + word + '[^。？！<"\']*', crawl_html.text)
                for a in match:
                    for _ in self.repalce_list:
                        a = a.replace(_, '')
                    if len(a) > 10 and a not in ret['sen']:
                        ret['sen'].append(a)

    def main(self):
        job_list = [gevent.spawn(self.run, word) for word in self.word_list]
        gevent.joinall(job_list)

    def get_word_list(self, fp_list):
        for fp in fp_list:
            fn_list = os.listdir(fp)
            for fn in fn_list:
                for line in open(os.path.join(fp, fn), 'r', encoding='utf-8'):
                    line = line.replace('\n', '').replace('\r', '')
                    self.word_list.append(line)


if __name__ == "__main__":
    cr = coroutine_crawler()
    fp_list = ['root/城市信息/全国',
               'root/生活百科/服饰']
    cr.get_word_list(fp_list)
    cr.main()
