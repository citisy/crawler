from selenium import webdriver
import selenium.webdriver.support.ui as ui
from basic_crawler import *
from tqdm import tqdm
from bs4 import BeautifulSoup


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

    def wait_element(self, class_name, timeout=10):
        wait = ui.WebDriverWait(self.browser, timeout)
        wait.until(lambda x: x.find_element_by_class_name(class_name))

    def quit(self):
        self.browser.quit()

