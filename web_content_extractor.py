import re
import sys


class Extractor:
    """通用爬虫，无需解析页面即可获取正文内容，可用于绝大部分的网页的正文提取"""

    def fix_text(self, text, replace_list=None):
        # replace escape character
        text = (text.replace("&quot;", "\"").replace("&ldquo;", "“").replace("&rdquo;", "”")
                .replace("&middot;", "·").replace("&#8217;", "’").replace("&#8220;", "“")
                .replace("&#8221;", "”").replace("&#8212;", "——").replace("&hellip;", "…")
                .replace("&#8226;", "·").replace("&#40;", "(").replace("&#41;", ")")
                .replace("&#183;", "·").replace("&amp;", "&").replace("&bull;", "·")
                .replace("&lt;", "<").replace("&#60;", "<").replace("&gt;", ">")
                .replace("&#62;", ">").replace("&nbsp;", "").replace("&#160;", " ")
                .replace("&tilde;", "~").replace("&mdash;", "—").replace("&copy;", "@")
                .replace("&#169;", "@").replace("♂", ""))

        replace_list = replace_list or (' ', '_', '\r', '\t', '\u3000')
        for i in replace_list:
            text = text.replace(i, '')

        return text

    def extract(self, html: str,
                smooth_windows=5, start_eps=20, end_eps=10) -> list:
        html = self.fix_text(html)
        text = re.sub(r'(?is)<pre.*?</pre>|'
                      r'(?is)<style.*?</style>|'
                      r'(?is)<script.*?</script>|'
                      r'(?is)<!--.*?-->|'
                      r'(?is)<.*?>|'
                      r'(?is)<head.*?</head>|',
                      '',
                      html)  # sub areas of pre, style, script, label comment, labels

        strip_list = [' ', '\\']  # only replace characters at the line's beginning and ending

        text_list = text.split('\n')

        for i in range(len(text_list)):
            for s in strip_list:
                text_list[i] = text_list[i].strip(s)

        # 计算每一行的单词数
        count = []
        for t in text_list:
            nan_chinese = re.findall('[a-zA-Z0-9_-]+', t)
            count.append(len(t) - len(nan_chinese) / 2.)  # 2个英文字符换算成1个中文字符

        # 段落平滑处理，防止过于尖锐
        smooth_count = [sum(count[i - smooth_windows:i + smooth_windows + 1]) / smooth_windows
                        for i in range(smooth_windows, len(count) - smooth_windows - 1)]

        flag = 0
        contents = []
        for i in range(smooth_windows, len(count) - smooth_windows - 1):
            # 一段文字开始的标准，这个标准应该是宽容的
            if all([flag == 0, count[i] > start_eps/2, smooth_count[i - smooth_windows] > start_eps]):
                flag = 1
                contents.append('')

            if flag == 1:
                if text_list[i]:
                    contents[-1] += text_list[i] + '\n'

            # 一段文字结束的标准，这个标准应该是严格的
            if all([flag == 1, count[i] < end_eps/2, smooth_count[i - smooth_windows] < end_eps]):
                flag = 0

        return contents


if __name__ == '__main__':
    from basic_crawler import Crawler

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

    extractor = Extractor()
    crawler = Crawler()
    contents = extractor.extract(crawler.start4url(url).text)

    for content in contents:
        print(content)
        print('--------')
