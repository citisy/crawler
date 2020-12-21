自定义爬虫框架

# 个人笔记

[python网络爬虫常用工具](http://www.citisy.site/posts/30422.html)

[python网络爬虫常用框架（一）--scrapy](http://www.citisy.site/posts/61679.html)

[python网络爬虫常用框架（二）--selenium](http://www.citisy.site/posts/38838.html)

[网页正文自动抽取器](http://www.citisy.site/posts/57557.html)

- **多线程爬虫**

  python中的多线程是虚假的多线程。由于python的GIL(Global Interpreter Lock)机制，同一时间只能运行一条线程，所以对于CPU密集型任务，多线程运行效果不如单线程。但对于爬虫这种I/O密集型任务，多线程的效果还是不错的。

- **协程爬虫**

  解决python的GIL问题。本质上也是多线程，但只开了一条线程，程序内部自行对线程资源进行调度。

- **多进程爬虫**

  不建议在Windows下使用python的多进程。因为Windows下没有fork机制，是虚假的多进程。

- **模拟浏览器爬虫**

  真正意义上的万能爬虫方法。但由于要渲染js，故爬虫速度较慢。

# 文件结构

```
.
├── basic_crawler.py                 # 爬虫框架基类
├── crawler_by_simulate_browser.py   # 模拟浏览器爬虫定义类
├── crawl_media.py                   # 媒体流文件定义类
├── crawler_by_coroutine.py          # 协程爬虫demo
├── crawler_by_multiprocess.py       # 多进程爬虫demo
├── crawler_by_multithread.py        # 多线程爬虫demo
├── crawler_examples.py              # 使用爬虫框架爬虫的一些例子
└── web_content_extractor.py         # 通用网页正文抽取器
```

