"""use multiprocess in linux/unix not in windows best
'cause windows system has no callable 'fork', it's fake multiprocess
"""

from multiprocessing import Process, Pool  # use Queue in multiprocessing, neither import queue
from common_crawler import Crawler
import sys

sys.setrecursionlimit(1000000)  # todo: RecursionError:maximum recursion depth exceeded


class myCrawler(Crawler):
    def do_something(self, html, **kwargs):
        print(html.text)


def sub_process(urls):
    crawler = myCrawler()
    for url in urls:
        crawler.crawl(url)


def use_pool():
    urls = [["http://ip-api.com/json/12.13.%d.%d" % (i, j) for i in range(10, 14)] for j in range(10, 20)]
    pool = Pool(5)
    for url in urls:
        pool.apply_async(sub_process, args=(url,))

    pool.close()
    pool.join()


def normal_multiprocess():
    urls = [["http://ip-api.com/json/12.13.%d.%d" % (i, j) for i in range(10, 14)] for j in range(10, 20)]
    process = []
    for url in urls:
        process.append(Process(target=sub_process, args=(url,)))

    for p in process:
        p.start()

    for p in process:
        p.join()


if __name__ == '__main__':
    normal_multiprocess()
    # use_pool()
