from basic_crawler import *
import re
import os
from urllib.parse import urlparse
from tqdm import tqdm


class StaticStreamCrawler(Crawler):
    @add_delay()
    def repeat_crawl(self, url, *args, **kwargs):
        video_save_path = args[0] if len(args) > 0 else None
        self.save_as_big_file(url, video_save_path)


class DynamicStreamCrawler(Crawler):
    """HLS(HTTP Live Streaming)是一个由苹果公司提出的基于HTTP的流媒体网络传输协议。
    m3u即为一种比较经典的播放标准，其中编码格式为utf-8即为m3u8标准
    m3u8具体格式含义：
    https://blog.csdn.net/langeldep/article/details/8603045
    部分格式：
    EXT-X-TARGETDURATION    每个片段的最大的时间
    EXT-X-MEDIA-SEQUENCE    当前m3u8文件中第一个文件的序列号
    EXT-X-KEY               定义加密方式和key文件的url
    EXT-X-PROGRAM-DATE-TIME 第一个文件的绝对时间
    EXT-X-ALLOW-CACHE       是否允许cache
    EXT-X-ENDLIST           表明m3u8文件的结束
    EXT-X-STREAM-INF        码率
    EXT-X-DISCONTINUITY     某属性发生了变化
    EXT-X-VERSION           该属性用不用都可以，可以没有
    爬取直播流文件难点在于如何获取.m3u8文件。"""

    def run(self, response, *args, **kwargs):
        m3u8_save_path, video_save_path = args[0], args[1]

        if m3u8_save_path:
            self.save_as_file(response.content, m3u8_save_path)

        text = response.text

        i = 0
        ts_urls = []
        home_url = urlparse(response.url).scheme + '://' + urlparse(response.url).netloc
        for line in text.split('\n'):
            if not line.startswith('#'):
                if line.startswith('http'):
                    line = line
                elif line.startswith('/'):
                    line = home_url + line
                else:
                    line = os.path.split(response.url)[0] + '/' + line

                ts_urls.append(line)
                i += 1

            if line == '#EXT-X-ENDLIST':
                break

        if video_save_path:
            with open(video_save_path, 'wb') as f:
                for ts_url in tqdm(ts_urls):
                    ts = self.repeat_crawl(ts_url, *args, **kwargs)
                    f.write(ts.content)


class ku6_Crawler(StaticStreamCrawler):
    def run(self, response, *args, **kwargs):
        urls = re.findall('<a class="video-image-warp" target="_blank" href="(.*?)">', response.text)
        for url in tqdm(urls):
            self.repeat_crawl(url, *args, **kwargs)

    @add_delay()
    def repeat_crawl(self, url, *args, **kwargs):
        video_save_root = args[0] if len(args) > 0 else None
        home_url = args[1] if len(args) > 1 else None

        if url.startswith('/video/'):
            if home_url:
                url = home_url + url
            response = self.get_repeat_response(url, *args, **kwargs)
            video_urls = re.findall('<source src="(.*?)" type="video/mp4">', response.text) or re.findall(
                'type: "video/mp4", src: "(.*?)"', response.text)
            if video_urls:
                video_url = video_urls[0]
                title = re.findall('document.title = "(.*?)"', response.text)[0]
                self.save_as_big_file(video_url, f'{video_save_root}/{title}.mp4')


if __name__ == '__main__':
    # crawler = ku6_Crawler()
    # url = 'https://www.ku6.com/index'
    # home_url = 'https://www.ku6.com'
    # crawler.start4url(url, 'video_', home_url)

    """todo:
    1. 字幕文件抓取
    2. 批量抓取m3u8列表
    3. m3u8链接会过期，目测是链接中带有时间戳信息"""

    # crawler = CrawlDynamicStream()
    # with open('m3u8_list4', 'r', encoding='utf8') as f:
    #     for i, url in enumerate(f.read().split('\n')):
    #         if i < 18:
    #             continue
    #         logging.info(i)
    #         crawler.start4url(url, 'video/index.m3u8', 'video/%d.ts' % i, timeout=10)
