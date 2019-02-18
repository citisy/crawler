"""recommend to use multithread in windows, and multiprocess in linux"""

from multiprocessing import Process, Queue  # use Queue in multiprocessing, neither import queue
from common_crawler import *
import sys

sys.setrecursionlimit(1000000)  # todo: RecursionError:maximum recursion depth exceeded


def producer(words, base_url, q):
    for word in words:
        logging.info('crawling words: %s', word)
        url = base_url % word
        try:
            html = session.get(url, headers=headers, timeout=2)
        except KeyboardInterrupt:
            exit(1)
        except Exception as e:
            logging.error('{} : {}'.format(url, e))
            logging.info('crawl is limit, sleep 10 mins')
            time.sleep(60 * 10)  # crawler is limited, so we stop 10 minute
            return
        html.encoding = 'utf8'
        soup = BeautifulSoup(html.text, 'lxml')
        crawl_list = soup.find_all('h3')
        if len(crawl_list) == 0:
            logging.info('empty crawl list  %s ', html.url)
        for crawl in crawl_list:
            q.put([word, crawl])    # producer


def consumers(work_q):
    while 1:
        if not work_q.empty():
            word, crawl = work_q.get()      # consumers
            crawl_html = auto_crawl(crawl)
            ret = {}
            ret['word'] = word
            ret['sen'] = []
            if crawl_html is None:
                continue
            # only match sentences with keywords
            # eg:
            #   keyword: 苹果,
            #   passage: ...有利于身体的生长发育。苹果营养价值高，酸甜可口，营养丰富，是老幼皆宜的水果之一。它的营养价值和医疗价值都很高，每100g鲜苹果肉中含糖类15g...
            #   match:苹果营养价值高，酸甜可口，营养丰富，是老幼皆宜的水果之一
            match = re.findall('[^。？！>"\']*' + word + '[^。？！<"\']*', crawl_html.text)
            for a in match:
                a = fix_text(a)
                if len(a) > 10 and a not in ret['sen']:
                    ret['sen'].append(a)
            print(ret)


if __name__ == '__main__':
    words = ['葡萄', '苹果', '雪梨', '黑莓']
    base_url = 'http://www.baidu.com/s?wd=%s&tn=monline_dg&ie=utf-8'

    work_q = Queue()
    work_process = []
    work_process.append(
        Process(target=producer, args=(words, base_url, work_q,))
    )
    for _ in range(3):
        work_process.append(
            Process(target=consumers, args=(work_q,))
        )

    for i in work_process:
        i.start()
    for i in work_process:
        i.join()
