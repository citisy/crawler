"""use multiprocess in linux/unix not in windows best
'cause windows system has no callable 'fork', it's fake multiprocess
"""

from multiprocessing import Process, Pool  # use Queue in multiprocessing, neither import queue
from basic_crawler import Crawler
import sys

sys.setrecursionlimit(1000000)  # todo: RecursionError:maximum recursion depth exceeded


class myCrawler(Crawler):
    def run(self, response, *args, **kwargs):
        print(response.text)


def sub_process(urls):
    """多进程任务"""
    crawler = myCrawler()
    for url in urls:
        crawler.start4url(url)


def use_pool():
    """调用进程池"""
    urls = [["http://ip-api.com/json/12.13.%d.%d" % (i, j) for i in range(10, 14)] for j in range(10, 20)]
    pool = Pool(5)
    for url in urls:
        pool.apply_async(sub_process, args=(url,))

    pool.close()
    pool.join()


def normal_multiprocess():
    """主进程"""
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
