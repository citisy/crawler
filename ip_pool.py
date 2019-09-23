import requests
from urllib import request
from bs4 import BeautifulSoup
from pymongo import MongoClient
import os
import re
from urllib.parse import quote

max_retries = 5
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=max_retries)
headers = {
    'Connection': 'Keep-Alive',
    'Accept': 'text/html, application/xhtml+xml, */*',
    'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
}

html = session.get('http://www.xicidaili.com/nn/', headers=headers)
html.encoding = 'utf8'
soup = BeautifulSoup(html.text, 'lxml')
trs = soup.find_all('tr', class_='odd')
ip_list = []
for i in trs:
    tds = i.find_all('td')
    ip_list.append(tds[1].text+':'+tds[2].text)

act_ip = []
for i in ip_list[:8]:
    print(i)
    try:
        proxy_handler = request.ProxyHandler({'http': i})
        opener = request.build_opener(proxy_handler)
        opener.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36')]
        request.install_opener(opener)
        response = request.urlopen('http://www.baidu.com')
        act_ip.append(i)
        print('ok!')
    except:
        continue
print('ip get!')
conn = MongoClient('127.0.0.1', 27017)
db = conn.citisy
collection = db.baidu

dp = 'root/自然科学/生物'
fn = os.listdir(dp)
word = []
for i in fn:
    for line in open(os.path.join(dp, i), 'r', encoding='utf-8'):
        line = line.replace('\n', '').replace('\r', '')
        word.append(line)

base_url = 'http://www.baidu.com/s?wd='
nip = 0
for i in word:
    if collection.find_one({'word': i}):
        continue
    print(i)
    ret = {}
    url = base_url + i + '&tn=monline_dg&ie=utf-8'
    url = quote(url, safe='/:?=')
    proxy_handler = request.ProxyHandler({'http': act_ip[nip]})
    nip += 1
    if nip >= len(act_ip):
        nip = 0
    opener = request.build_opener(proxy_handler)
    opener.addheaders = [('User-Agent',
                          'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36')]
    request.install_opener(opener)
    response = request.urlopen(url)
    html = response.read().decode("utf-8")
    soup = BeautifulSoup(html, 'lxml')
    crawl_list = soup.find_all('h3', class_='t c-gap-bottom-small')
    ret['word'] = i
    ret['sen'] = []
    for crawl in crawl_list:
        crawl_url = crawl.find('a')['href']
        try:
            crawl_html = session.get(crawl_url, headers=headers)
        except ConnectionError:
            continue
        crawl_html.encoding = 'utf8'
        match = re.findall('[^。？！>"\']*' + i + '[^。？！<"\']*', crawl_html.text)
        for a in match:
            a = a.replace(' ', '').replace('_', '').replace('\n', '').replace('百度图片搜索', '')
            if len(a) > 10 and a not in ret['sen']:
                ret['sen'].append(a)
    collection.insert(ret)