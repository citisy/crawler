import logging
import os
import re
from tqdm import tqdm
from basic_crawler import Crawler, add_try, add_callback, add_delay
from crawler_by_simulate_browser import SimulateBrowser
from crawl_media import StaticStreamCrawler
from bs4 import BeautifulSoup


class BaikeKeywordCrawler(Crawler):
    """利用关键词爬取百度百科收索词条"""

    from web_content_extractor import Extractor

    extractor = Extractor()

    def run(self, fn, *args, **kwargs):
        with open(fn, 'r', encoding='utf8') as f:
            words = f.read().split('\n')

        base_url = 'https://baike.baidu.com/item/%s'

        data = {}

        for word in words:
            logging.info('crawling words: %s', word)
            url = base_url % word
            r = self.repeat_crawl(url, timeout=2)
            if r:
                text = self.extractor.extract(r.text)
                data[word] = text

        self.save_as_json(data, 'baike/baidubaike.json')


# crawler = BaikeKeywordCrawler()
# crawler.run('keyword.txt')


class BaiduBaikeCrawler(SimulateBrowser):
    """抓取百度百科某一领域的所有词条
    args[1]: 文本内容保存的地址
    args[2]: 原始HTML文件保存的根目录"""

    def run(self, url, *args, save_path1=None, save_path2=None, **kwargs):
        self.get_response(url)
        self.wait_element('list')
        url_dict = {}
        elements = self.browser.find_elements_by_class_name('list')
        for element in elements:
            e = element.find_element_by_class_name('title')
            url = e.get_property('href')
            title = e.text
            url_dict[title] = url

            response = self.get_repeat_response(url)
            self.save_as_file(response.content, os.path.join(save_path2, f'{title}.html'))

        self.save_as_json(url_dict, save_path1)
        self.quit()

    @add_try()
    @add_callback()
    def get_repeat_response(self, url: str, *args, **kwargs):
        try:
            response = self.session.get(url, **kwargs)
            if response.status_code != 200:
                logging.error('url: {} status code is {}'.format(response.url, response.status_code))
                return

            a = re.search('charset=["\']?([^\s"\'; ]+)', response.text)  # get html encoding automatically

            if a:
                response.encoding = a.group(1)
            else:
                response.encoding = 'utf8'
            return response

        except KeyboardInterrupt:
            exit(1)


# crawler = BaiduBaikeCrawler()
# crawler.run('http://baike.baidu.com/fenlei/%E6%96%87%E5%8C%96%E9%81%97%E4%BA%A7',
#             'baike/baidubaike.json', 'baike_html')


class BaiduNewsCrawler(SimulateBrowser):
    """模拟浏览器抓取百度新闻
    默认有自动提取文本内容等优化
    args[1]: 文本内容保存的地址
    args[2]: 原始HTML文件保存的根目录"""

    from web_content_extractor import Extractor

    extractor = Extractor()

    def run(self, html: str, *args, json_save_path=None, html_save_path=None, **kwargs):
        self.quit()
        soup = BeautifulSoup(html, 'lxml')
        crawl_list = soup.find('div', id='body').find_all('a')
        if len(crawl_list) == 0:
            logging.error('empty list!')

        dic = {}
        for crawl in tqdm(crawl_list):
            try:
                crawl_url = crawl['href']
            except KeyError:
                logging.error(f'can not found url: {crawl}')
                continue

            if crawl_url[:4] != 'http':
                continue

            html, title = self.repeat_crawl(crawl_url, *args, **kwargs)
            contents = self.extractor.extract(html)
            if contents:
                dic[crawl_url] = {title: contents}
                if html_save_path:
                    self.save_as_text(html, os.path.join(html_save_path, f'{title}.html'))

        self.save_as_json(dic, json_save_path)

    @add_delay()
    def repeat_crawl(self, url, *args, **kwargs):
        response = self.get_repeat_response(url)

        if not response:
            return '', ''

        title = self.get_title(response.text)

        return response.text, title

    @add_try()
    @add_callback()
    def get_repeat_response(self, url: str, *args, **kwargs):
        try:
            response = self.session.get(url, **kwargs)
            if response.status_code != 200:
                logging.error('url: {} status code is {}'.format(response.url, response.status_code))
                return

            a = re.search('charset=["\']?([^\s"\'; ]+)', response.text)  # get html encoding automatically

            if a:
                response.encoding = a.group(1)
            else:
                response.encoding = 'utf8'
            return response

        except KeyboardInterrupt:
            exit(1)


# crawler = BaiduNewsCrawler()
# url = 'http://news.baidu.com/'
# crawler.start4url(
#     url, 5, run_kwargs=dict(
#         json_save_path='news/baidu_news.json',
#         html_save_path='news_html'
#     ))
# crawler.quit()


class Ku6Crawler(StaticStreamCrawler):
    def run(self, response, *args, **kwargs):
        urls = re.findall('<a class="video-image-warp" target="_blank" href="(.*?)">', response.text)
        for url in tqdm(urls):
            self.repeat_crawl(url, *args, **kwargs)

    @add_delay()
    def repeat_crawl(self, url, *args, video_save_dir=None, home_url=None, **kwargs):
        if url.startswith('/video/'):
            if home_url:
                url = home_url + url
            response = self.get_repeat_response(url, *args, **kwargs)
            video_urls = re.findall('<source src="(.*?)" type="video/mp4">', response.text) or re.findall(
                'type: "video/mp4", src: "(.*?)"', response.text)
            if video_urls:
                video_url = video_urls[0]
                title = re.findall('document.title = "(.*?)"', response.text)[0]
                self.save_as_big_file(video_url, f'{video_save_dir}/{title}.mp4')

# """todo:
# 1. 字幕文件抓取
# 2. 批量抓取m3u8列表
# 3. m3u8链接会过期，目测是链接中带有时间戳信息"""
# crawler = Ku6Crawler()
# url = 'https://www.ku6.com/index'
# home_url = 'https://www.ku6.com'
# crawler.start4url(
#     url,
#     run_kwargs=dict(
#         video_save_dir='video_',
#         home_url=home_url
#     ))
