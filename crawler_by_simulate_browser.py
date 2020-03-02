from selenium import webdriver
from basic_crawler import *
from tqdm import tqdm


class SimulateBrowser(Crawler):
    """堪称万能爬虫手段，唯一缺点就是慢，因为要渲染js
    args[0]: 网页下滑等待加载内容的次数，默认为0，即不等待加载"""

    def __init__(self):
        super().__init__()
        self.replace_name = ['|', '<', '>', '/', '\\', '?', '*', ':', '"']
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_experimental_option('w3c', False)
        # chrome_options.headless = True  # quite mode
        self.browser = webdriver.Chrome(chrome_options=chrome_options)

    @add_try()
    def get_response(self, url, *args, **kwargs) -> str:
        wait_times = args[0] if len(args) > 0 else 0
        self.browser.get(url)
        new_html = self.browser.page_source
        for _ in range(wait_times):  # 保证页面已经加载完新内容
            old_html = ''
            while new_html != old_html:
                old_html = self.browser.page_source
                self.slide_down()
                new_html = self.browser.page_source

        return new_html

    @add_delay()
    def slide_down(self):
        """网页滑到最低端，以加载页面"""
        js = "var q=document.documentElement.scrollTop=100000"
        self.browser.execute_script(js)

    def quit(self):
        self.browser.quit()


class BaiduNewsCrawler(SimulateBrowser):
    """模拟浏览器抓取百度新闻
    args[1]: 文件保存的地址"""

    from web_content_extractor import Extractor

    extractor = Extractor()

    def run(self, html: str, *args, **kwargs):
        self.quit()
        save_path = args[1] if len(args) > 1 else None
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
            html = self.fix_text(html)
            contents = self.extractor.start4html(html)
            if contents:
                dic[crawl_url] = {title: contents}

        self.save_as_json(dic, save_path)

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


if __name__ == '__main__':
    crawler = BaiduNewsCrawler()
    url = 'http://news.baidu.com/'
    crawler.start4url(url, 5, 'news/baidu_news.json')
    # crawler.quit()
