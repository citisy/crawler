"""multithread in python is fake multithread
'cause GIL(Global Interpreter Lock),
it means that only one thread run at the same time,
so it used to run in I/O dense, such as crawl"""
from concurrent.futures import ThreadPoolExecutor
import threading
from basic_crawler import Crawler


class myCrawler(Crawler):
    def run(self, response, *args, **kwargs):
        print(response.text)


def use_pool():
    """调用线程池"""
    crawler = myCrawler()
    ips = ['12.13.14.%d' % (ip + 1) for ip in range(30)]
    urls = ["http://ip-api.com/json/%s" % ip for ip in ips]
    pool = ThreadPoolExecutor(max_workers=10)
    pool.map(crawler.start4url, urls)


def normal_multithread():
    """主线程
    todo: Connection pool is full, discarding connection: ip-api.com"""
    crawler = myCrawler()
    ips = ['12.13.14.%d' % (ip + 1) for ip in range(30)]
    urls = ["http://ip-api.com/json/%s" % ip for ip in ips]
    for url in urls:
        t = threading.Thread(target=crawler.start4url, args=(url,))
        t.start()


if __name__ == '__main__':
    normal_multithread()
    # use_pool()
