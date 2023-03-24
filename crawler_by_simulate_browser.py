import logging
import time
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.alert import Alert
from basic_crawler import Crawler, add_try, add_delay, add_callback
from webdriver_manager.chrome import ChromeDriverManager


class SimulateBrowser(Crawler):
    """堪称万能爬虫手段，唯一缺点就是慢，因为要渲染js"""

    def __init__(self, headless=False, timeout=10):
        super().__init__()
        self.timeout = timeout
        self.replace_name = ['|', '<', '>', '/', '\\', '?', '*', ':', '"']
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.headless = headless  # quite mode

        self.browser = webdriver.Chrome(ChromeDriverManager().install(),
                                        chrome_options=self.chrome_options)
        self.browser.set_page_load_timeout(self.timeout)    # 连接超时
        self.browser.set_script_timeout(self.timeout)       # 加载超时

    @add_try()
    def get_response(self, url, *args, wait_times=0, most_times=10, per_wait=0.1, **kwargs) -> str:
        """args[0]: 网页下滑等待加载内容的次数，默认为0，即不等待加载"""
        # wait_times = args[0] if len(args) > 0 else 0
        # most_times = args[1] if len(args) > 1 else 10
        # per_wait = args[2] if len(args) > 2 else 0.1
        try:
            self.browser.get(url)

        except selenium.common.exceptions.TimeoutException:  # 如果出现超时，浏览器就会死掉，需要重启
            logging.error('url: {} timeout! Restart browser!'.format(url))
            self.restart()  # todo: 重启浏览器方法耗费资源，后面寻求更加优雅的替代方法
            return

        try:
            new_html = self.browser.page_source
        except selenium.common.exceptions.UnexpectedAlertPresentException:
            logging.error('url: {} have something wrong!'.format(url))
            Alert(self.browser).accept()
            return

        for _ in range(wait_times):  # 保证页面已经加载完新内容
            old_html = ''
            i = 0
            while new_html > old_html and i < most_times:
                old_html = self.browser.page_source
                self.slide_down()
                time.sleep(per_wait)
                new_html = self.browser.page_source
                i += 1

        return new_html

    @add_delay()
    @add_callback(lambda x: logging.error('Something wrong while saving screenshot!'))
    def slide_down(self):
        """网页滑到最低端，以加载页面"""
        js = 'window.scrollTo(0,document.body.scrollHeight);'
        self.browser.execute_script(js)

    def wait_element(self, class_name, timeout=10):
        """等待页面的某个元素加载完毕"""
        wait = WebDriverWait(self.browser, timeout)
        return wait.until(lambda x: x.find_element_by_class_name(class_name))

    @add_callback(lambda x: logging.error('Something wrong while saving screenshot!'))
    def save_whole_screenshot(self, save_path):
        """保存整个页面，要使用这个方法，一定要把headless设为true，否则得到仍然是部分页面的截图"""
        logging.info(f'Saving screenshot: {save_path}')
        width = self.browser.execute_script("return document.documentElement.scrollWidth")
        height = self.browser.execute_script("return document.documentElement.scrollHeight")
        # 将浏览器的宽高设置成刚刚获取的宽高
        self.browser.set_window_size(width, height)
        # 截图并关掉浏览器
        self.browser.save_screenshot(save_path)

    def restart(self):
        """重启浏览器"""
        self.quit()
        self.browser = webdriver.Chrome(chrome_options=self.chrome_options)

        self.browser.set_page_load_timeout(self.timeout)
        self.browser.set_script_timeout(self.timeout)

    def quit(self):
        self.browser.quit()

