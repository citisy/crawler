from common_crawler import Crawler
import re
import time
import os
from urllib.parse import urlparse
from tqdm import tqdm


class CrawlStaticStream(Crawler):
    def do_something(self, html, **kwargs):
        home = 'https://www.ku6.com'
        urls = re.findall('<a class="video-image-warp" target="_blank" href="(.*?)">', html.text)
        for url in urls:
            if url.startswith('/video/'):
                html = self.get_html(home + url)
                video_urls = re.findall('<source src="(.*?)" type="video/mp4">', html.text) or re.findall(
                    'type: "video/mp4", src: "(.*?)"', html.text)
                if video_urls:
                    for video_url in video_urls:
                        title = url.split('/')[-1]
                        self.download_big_file(video_url, 'video/%s.mp4' % title)
                time.sleep(1)


class CrawlDynamicStream(Crawler):
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

    def do_something(self, html, **kwargs):
        if hasattr(self, 'm3u8_save_path'):
            self.save(html.content, self.m3u8_save_path)

        text = html.text

        i = 0
        ts_urls = []
        home_url = urlparse(url).scheme + '://' + urlparse(url).netloc
        for line in text.split('\n'):
            if not line.startswith('#'):
                if line.startswith('http'):
                    line = line
                elif line.startswith('/'):
                    line = home_url + line
                else:
                    line = os.path.split(url)[0] + '/' + line
                ts_urls.append(line)
                i += 1

            if line == '#EXT-X-ENDLIST':
                break

        if hasattr(self, 'video_save_path'):
            with open(self.video_save_path, 'wb') as f:
                for ts_url in tqdm(ts_urls):
                    ts = self.session.get(ts_url)
                    f.write(ts.content)


if __name__ == '__main__':
    # crawler = CrawlStaticStream()
    # url = 'https://www.ku6.com/index'
    # crawler.crawl(url)

    crawler = CrawlDynamicStream()

    """todo:
    1. 字幕文件抓取
    2. 批量抓取m3u8列表
    3. m3u8链接会过期，目测是链接中带有时间戳信息"""

    # 火影忍者第一集
    url = 'https://valipl.cp31.ott.cibntv.net/6975B808BDD4D71FB961D26C4/03000600005D89BF8AF8D76011BA6AFC417C00-AB9B-4585-B00D-9D19D8447341-1-114.m3u8?ccode=0502&duration=1419&expire=18000&psid=212015f63154d3b142ba81e8b57ec12c&ups_client_netip=671b1a91&ups_ts=1575719129&ups_userid=&utid=2JYPFrwZDksCAXnuS%2FGJSivn&vid=XNTQwMTgxMTE2&vkey=A55d792395482b64a42af5c50560ab916&sm=1&operate_type=1&dre=u37&si=28&bc=2'
    crawler.m3u8_save_path = 'video/index.m3u8'
    crawler.video_save_path = 'video/NARUTO_1.ts'
    crawler.crawl(url)
