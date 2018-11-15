# [common_crawler.py](common_crawler.py)
一般的爬虫。<br>
如果用多线程或多进程频繁访问同一个网站，会对其造成很多的困扰，加大了ip被封的可能性，其实速度是下降，既不利人也不利己，所以建议使用这种爬虫就满足基本需求了

# [coroutine_crawler.py](coroutine_crawler.py)
协程爬虫，不能用于linux系统

# [multiprocess_crawl.py](multiprocess_crawl.py)
多进程爬虫，建议用于linux系统

# [multithread_crawl.py](multithread_crawl.py)
多线程爬虫，建议用于windows系统

# [simulate_browser.py](simulate_browser.py)
模拟浏览器爬虫，能够适用于基本全部的情况，但是速度慢

# [general_crawler_by_count.py](general_crawler_by_count.py)
通用爬虫，可用于绝大部分的网页的正文提取
### 效果展示

新闻链接：[习主席的12个小时](http://www.xinhuanet.com/2018-09/05/c_129947770.htm)

网页截图： 
![image](img/printscreen.png)

提取结果：
```text
>>> ret = get_ret(url)
>>> ret
>>> http://vod.xinhuanet.com/v/vod.html?vid=534647【简介】9月4日，2018年中非合作论坛北京峰会闭幕。这一天，习主席参加了多少场外事活动？新华社“第1视点”为你呈现。
```

提取出来的文本中的url是视频的url，后期根据需要可以正则去掉