"""multithread in python is fake multithread
'cause GIL(Global Interpreter Lock),
it means that only one thread run at the same time,
so it used to run in I/O dense, such as crawl"""
from concurrent.futures import ThreadPoolExecutor
import threading
from common_crawler import Crawler


class myCrawler(Crawler):
    def do_something(self, html, **kwargs):
        print(html.text)


def use_pool():
    crawler = myCrawler()
    ips = ['12.13.14.%d' % (ip + 1) for ip in range(30)]
    urls = ["http://ip-api.com/json/%s" % ip for ip in ips]
    pool = ThreadPoolExecutor(max_workers=10)
    pool.map(crawler.crawl, urls)


def normal_multithread():
    crawler = myCrawler()
    ips = ['12.13.14.%d' % (ip + 1) for ip in range(30)]
    urls = ["http://ip-api.com/json/%s" % ip for ip in ips]
    for url in urls:
        t = threading.Thread(target=crawler.crawl, args=(url,))
        t.start()


if __name__ == '__main__':
    normal_multithread()
    # use_pool()
