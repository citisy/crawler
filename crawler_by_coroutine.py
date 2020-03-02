"""coroutine is to solve the problem of GIL
coroutine is a thread essentially"""
import gevent
from gevent import monkey
from basic_crawler import Crawler
import sys

sys.setrecursionlimit(1000000)
monkey.patch_all()


class myCrawler(Crawler):
    def run(self, response, *args, **kwargs):
        print(response.text)


def normal_coroutine():
    crawler = myCrawler()
    ips = ['12.13.14.%d' % (ip + 1) for ip in range(30)]
    urls = ["http://ip-api.com/json/%s" % ip for ip in ips]
    coroutine = []
    for url in urls:
        coroutine.append(gevent.spawn(crawler.start4url, url, ))

    gevent.joinall(coroutine)


if __name__ == "__main__":
    normal_coroutine()
