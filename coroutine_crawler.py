"""use this crawl method, we will be limited soon. so it must use with ip pool"""

import gevent
from gevent import monkey
from common_crawler import *
import sys
sys.setrecursionlimit(1000000)

monkey.patch_all()

if __name__ == "__main__":
    words = ['葡萄', '苹果', '雪梨', '黑莓']
    base_url = 'http://www.baidu.com/s?wd=%s&tn=monline_dg&ie=utf-8'
    work_cor = []
    for word in words:
        work_cor.append(
                gevent.spawn(main, word, base_url,)
            )
    gevent.joinall(work_cor)
