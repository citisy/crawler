import selenium
from selenium import webdriver
import selenium.webdriver.support.ui as ui
from basic_crawler import *


class SimulateBrowser(Crawler):
    """堪称万能爬虫手段，唯一缺点就是慢，因为要渲染js"""

    def __init__(self, headless=False, timeout=10):
        super().__init__()
        self.timeout = timeout
        self.replace_name = ['|', '<', '>', '/', '\\', '?', '*', ':', '"']
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.headless = headless  # quite mode

        self.browser = webdriver.Chrome(chrome_options=self.chrome_options)

        self.browser.set_page_load_timeout(self.timeout)    # 连接超时
        self.browser.set_script_timeout(self.timeout)       # js加载超时

    @add_try()
    def get_response(self, url, *args, **kwargs) -> str:
        """args[0]: 网页下滑等待加载内容的次数，默认为0，即不等待加载"""
        wait_times = args[0] if len(args) > 0 else 0
        try:
            self.browser.get(url)

        except selenium.common.exceptions.TimeoutException:  # 如果出现超时，浏览器就会死掉，需要重启
            logging.error('url: {} timeout! Restart browser!'.format(url))
            self.restart()  # todo: 重启浏览器方法耗费资源，后面寻求更加优雅的替代方法

        new_html = self.browser.page_source
        for _ in range(wait_times):  # 保证页面已经加载完新内容
            old_html = ''
            while new_html != old_html:
                old_html = self.browser.page_source
                self.slide_down()
                time.sleep(0.1)
                new_html = self.browser.page_source

        return new_html

    @add_delay()
    def slide_down(self):
        """网页滑到最低端，以加载页面"""
        js = 'window.scrollTo(0,document.body.scrollHeight);'
        self.browser.execute_script(js)

    def wait_element(self, class_name, timeout=10):
        """等待页面的某个元素加载完毕"""
        wait = ui.WebDriverWait(self.browser, timeout)
        wait.until(lambda x: x.find_element_by_class_name(class_name))

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

