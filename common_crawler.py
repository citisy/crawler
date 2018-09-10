"""use the keyword to crawl baidu for getting the urls, find the sentences with keywords"""

import requests
from bs4 import BeautifulSoup
import re
from pymongo import MongoClient
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[ %(asctime)s ] %(message)s',
)

repalce_list = [' ', '_', '\r', '\t', '\u3000', '百度图片搜索', '百度百科']


def fix_text(text, repalce_list=repalce_list):
    """Escape character"""
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
        text = text.replace(i, "")
    return text


def main(word, base_url):
    logging.info('crawling words: %s', word)
    ret = {}
    url = base_url % word
    try:
        html = session.get(url, headers=headers, timeout=2)
    except KeyboardInterrupt:
        exit(1)
    except Exception as e:
        logging.error('error   {} : {}'.format(url, e))
        logging.info('crawl is limit, sleep 10 mins')
        time.sleep(60 * 10)  # crawler is limited, so we stop 10 minute
        return
    html.encoding = 'utf8'
    soup = BeautifulSoup(html.text, 'lxml')
    crawl_list = soup.find_all('h3')
    if len(crawl_list) == 0:
        logging.info('empty crawl list  %s ', html.url)
    ret['word'] = word
    ret['sen'] = []
    for crawl in crawl_list:
        crawl_html = auto_crawl(crawl)
        if crawl_html is None:
            continue
        # * only match sentences with keywords
        # * eg:
        #       keyword: 苹果,
        #       passage: ...有利于身体的生长发育。苹果营养价值高，酸甜可口，营养丰富，是老幼皆宜的水果之一。它的营养价值和医疗价值都很高，每100g鲜苹果肉中含糖类15g...
        #       match:苹果营养价值高，酸甜可口，营养丰富，是老幼皆宜的水果之一
        # * always, a sentence will start with (。？！(sens end) >"'(html tags end)) and end with (。？！<"')
        # * eg:
        #       <div class="para" label-module="para">苹果品种数以千计，分为酒用品种、烹调品种、尾食品种3大类。3类品种的大小、颜色、香味、光滑度 （可能还有脆性、风味）等特点均有差别。不少品种...</div>
        #       result: 苹果品种数以千计，分为酒用品种、烹调品种、尾食品种3大类。3类品种的大小、颜色、香味、光滑度 （可能还有脆性、风味）等特点均有差别。
        match = re.findall('[^。？！>"\']*' + word + '[^。？！<"\']*', crawl_html.text)
        for a in match:
            a = fix_text(a)
            if len(a) > 10 and a not in ret['sen']:
                ret['sen'].append(a)
    # collection.insert(ret)
    print(ret)


def auto_crawl(crawl):
    crawl_url = crawl.find('a')['href']
    try:
        crawl_html = session.get(crawl_url, headers=headers, timeout=2)
        logging.info('        %s', crawl_html.url)
    except Exception as e:
        logging.error('error   {} : {}'.format(crawl_url, e))
        return None
    encoding = re.findall('charset=["]*([^\s";]+)', crawl_html.text)    # usually, u can get encoding in html's head
    if len(encoding) == 0:  # generally, if can't get encoding, it probability means the web limit our crawler.
        encoding = 'utf8'
    crawl_html.encoding = encoding[0]
    return crawl_html


session = requests.Session()
headers = {
    'Connection': 'Keep-Alive',
    'Accept': 'text/html, application/xhtml+xml, */*',
    'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
}

if __name__ == '__main__':
    # conn = MongoClient('127.0.0.1', 27017)  # also, u can use any other methods to save ur data
    # db = conn.citisy
    # collection = db.test
    words = ['葡萄', '苹果', '雪梨', '黑莓']
    base_url = 'http://www.baidu.com/s?wd=%s&tn=monline_dg&ie=utf-8'
    for word in words:
        # if collection.find_one({'word': i}):  # if the database exist the word, needn't to crawl the word
        #     continue
        main(word, base_url)
    # conn.close()
