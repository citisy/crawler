"""multithread in python is fake multithread
'cause GIL(Global Interpreter Lock),
it means that only one thread run at the same time,
so it used to run in I/O dense, such as crawl"""
from concurrent.futures import ThreadPoolExecutor
from basic_crawler import *
import queue


class CrawlerByPool(Crawler):
    """调用线程池"""
    def run(self, urls, *args, **kwargs):
        self.q = queue.Queue()
        pool = ThreadPoolExecutor(max_workers=10)
        pool.map(self.repeat_crawl, urls)

        i = 0
        while True:
            if not self.q.empty():
                print(self.q.get())
                i += 1

            if i >= len(urls):
                break

    @add_delay()
    def repeat_crawl(self, url: str, *args, **kwargs):
        r = self.get_response(url)
        self.q.put(r)


if __name__ == '__main__':
    ips = ['12.13.14.%d' % (ip + 1) for ip in range(30)]
    urls = ["http://ip-api.com/json/%s" % ip for ip in ips]

    crawler = CrawlerByPool()
    crawler.run(urls)
