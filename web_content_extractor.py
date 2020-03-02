import re
import sys


class Extractor:
    """通用爬虫，无需解析页面即可获取正文内容，可用于绝大部分的网页的正文提取"""

    def start4url(self, *args, **kwargs):
        from basic_crawler import Crawler

        crawler = Crawler()
        response = crawler.start4url(url, *args, **kwargs)
        html = crawler.fix_text(response.text)
        return self.start4html(html)

    def start4html(self, html: str):
        match = re.sub(r'(?is)<pre.*?</pre>|'
                       r'(?is)<style.*?</style>|'
                       r'(?is)<script.*?</script>|'
                       r'(?is)<!--.*?-->|'
                       r'(?is)<.*?>|'
                       r'(?is)<head.*?</head>|',
                       '',
                       html)  # sub areas of pre, style, script, label comment, labels
        contents = self.get_contents(match)
        return contents

    def get_contents(self, text):
        strip_list = [' ', '\\']  # only replace characters at the line's beginning and ending

        text_list = text.split('\n')

        for i in range(len(text_list)):
            for s in strip_list:
                text_list[i] = text_list[i].strip(s)

        # count each line's words
        count = []
        for t in text_list:
            nan_chinese = re.findall('[a-zA-Z0-9_-]+', t)
            count.append(len(t) - len(nan_chinese) / 2)  # 2 English characters equals 1 chinese character

        kc = 2  # degree of smooth
        smooth_count = [sum(count[i - kc:i + kc + 1]) / 5. for i in range(kc, len(count) - kc - 1)]

        flag = 0
        contents = []
        for i in range(kc, len(count) - kc - 1):
            # where the content is start
            if all([flag == 0, count[i] > 7, smooth_count[i - kc] > 20]):
                flag = 1
                contents.append('')

            if flag == 1:
                contents[-1] += text_list[i]

            # where the content is end
            if all([flag == 1, count[i] < 4, smooth_count[i - kc] < 10]):
                flag = 0

        return contents


if __name__ == '__main__':
    crawler = Extractor()
    # url = 'http://music.yule.sohu.com/20091109/n268066205.shtml'
    # url = 'http://ent.qq.com/a/20091109/000253.htm'  #  连接多
    # url = 'https://kexue.fm/'     # 格式独特
    # url = 'https://kexue.fm/archives/5776'
    # url = 'https://blog.csdn.net/ying86615791/article/details/76215363'  # 内容分散
    # url = 'https://www.2cto.com/kf/201703/611583.html'    # 正文少
    # url = 'http://www.cnblogs.com/blueel/archive/2013/01/14/2859497.html'
    # url = 'https://blog.csdn.net/singwhatiwanna/article/details/48439621'   # 正文篇章多
    # url = 'https://www.crummy.com/software/BeautifulSoup/bs4/doc.zh/#id17'      # 文档类型
    # url = 'http://news.ifeng.com/a/20180906/60029282_0.shtml?_zbs_baidu_news'
    # url = 'https://3w.huanqiu.com/a/3458fa/7FYoUgcrac8?agt=8'
    # url = 'http://xinwen.eastday.com/a/180906102137870.html?qid=news.baidu.com'
    # url = 'http://sports.ifeng.com/a/20180906/60028642_0.shtml?_zbs_baidu_news'
    url = 'http://www.xinhuanet.com/politics/xxjxs/2019-09/16/c_1125001493.htm'
    if len(sys.argv) > 2:
        url = sys.argv[1]
    contents = crawler.start4url(url, timeout=2)
    print(contents)
