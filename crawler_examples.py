from crawler_by_simulate_browser import *


class BaikeCrawler(Crawler):
    """利用关键词爬取百度百科收索词条"""

    from web_content_extractor import Extractor

    extractor = Extractor()

    @add_delay()
    def run(self, response, *args, **kwargs):
        return self.extractor.extract(response.text)


# crawler = BaikeCrawler()
#
# with open('keyword.txt', 'r', encoding='utf8') as f:
#     words = f.read().split('\n')
#
# data = {}
#
# base_url = 'https://baike.baidu.com/item/%s'
# for word in words:
#     logging.info('crawling words: %s', word)
#     url = base_url % word
#     contents = crawler.start4url(url, timeout=2)
#     data[word] = contents
#
# crawler.save_as_json(data, 'baike/baidubaike.json')


class BaiduBaikeCrawler(SimulateBrowser):
    """抓取百度百科某一领域的所有词条
    args[1]: 文本内容保存的地址
    args[2]: 原始HTML文件保存的根目录"""

    def run(self, html, *args, **kwargs):
        save_path1 = args[1] if len(args) > 1 else None
        save_path2 = args[2] if len(args) > 2 else None

        self.wait_element('list')
        url_dict = {}
        elements = self.browser.find_elements_by_class_name('list')
        for element in elements:
            e = element.find_element_by_class_name('title')
            url = e.get_property('href')
            title = e.text
            url_dict[title] = url

            response = self.repeat_crawl(url)
            self.save_as_file(response.content, os.path.join(save_path2, f'{title}.html'))

        self.save_as_json(url_dict, save_path1)

    @add_try()
    @add_delay()
    def repeat_crawl(self, url: str, *args, **kwargs):
        return self.session.get(url, **kwargs)


# crawler = BaiduBaikeCrawler()
# crawler.start4url('http://baike.baidu.com/fenlei/%E6%96%87%E5%8C%96%E9%81%97%E4%BA%A7',
#                   'baike/baidubaike.json', 'baike_html')
# crawler.quit()


class BaiduNewsCrawler(SimulateBrowser):
    """模拟浏览器抓取百度新闻
    args[1]: 文本内容保存的地址
    args[2]: 原始HTML文件保存的根目录"""

    from web_content_extractor import Extractor

    extractor = Extractor()

    def run(self, html: str, *args, **kwargs):
        self.quit()
        save_path1 = args[1] if len(args) > 1 else None
        save_path2 = args[2] if len(args) > 2 else None
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
                if save_path2:
                    self.save_as_text(html, os.path.join(save_path2, f'{title}.html'))

        self.save_as_json(dic, save_path1)

    @add_callback()
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
# crawler.start4url(url, 5, 'news/baidu_news.json', 'news_html')
# crawler.quit()
