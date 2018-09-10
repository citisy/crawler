"""often used to crawl news"""

from common_crawler import *
import numpy as np

strip_list = [' ', '\\']  # only replace characters at the line's beginning and ending

sess = requests.Session()


def get_html(url):
    try:
        html = sess.get(url, headers=headers, timeout=2)
    except:
        logging.info('connect error: %s', url)
        return None

    encoding = re.findall('charset=["]*([^\s";]+)', html.text)  # get html encoding automatically
    try:
        html.encoding = encoding[0]
    except:
        html.encoding = 'utf8'
    return html


def fix_html(text):
    match = re.sub(r'(?is)<pre.*?</pre>|'
                   r'(?is)<style.*?</style>|'
                   r'(?is)<script.*?</script>|'
                   r'(?is)<!--.*?-->|'
                   r'(?is)<.*?>|'
                   r'(?is)<head.*?</head>|',
                   '',
                   text)  # sub areas of pre, style, script, label comment, labels

    match = fix_text(match, repalce_list)
    return match


def div(match):
    li = match.split('\n')

    for i in range(len(li)):
        for j in strip_list:
            li[i] = li[i].strip(j)

    count = []
    for i in li:
        words = re.findall(u'[a-zA-Z]+', i)
        count.append(len(i) - len(words) / 2)       # 2 English characters equals 1 chinese character

    kc = 2
    c = []
    for i in range(kc, len(count) - kc - 1):
        c.append(sum(count[i - kc:i + kc + 1]) / 5.)

    # k = 10
    # rat = []
    # for i in range(k, len(c) - k - 1):
    #     rat.append((sum(c[i + 1:i + 1 + k]) + k + 1.) / (sum(c[i - k:i]) + k + 1.))
    # rat = np.array(rat)
    #
    # argmax = rat.argmax()

    flag = 0
    ret = []
    for i in range(kc, len(count) - kc - 1):
        if flag == 0 and count[i] > 7 and c[i - kc] > 10:
            flag = 1
            ret.append('')
        if flag == 1:
            ret[-1] += li[i]
        if flag == 1 and count[i] < 4 and c[i - kc] < 10:
            flag = 0

    return ret


if __name__ == '__main__':
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
    url = 'http://www.xinhuanet.com/2018-09/05/c_129947770.htm'
    html = get_html(url)
    print(html.text)
    soup = BeautifulSoup(html.text, 'lxml')
    ct = re.findall('(15[0-9]{8})[^0-9]', html.text)
    title = soup.head.title.text
    match = fix_html(html.text)
    ret = div(match)
    for i in ret:
        print(i)
