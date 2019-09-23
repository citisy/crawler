from common_crawler import Crawler
import re
import time
import os


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
        self.save(html.content, 'video/index.m3u8')
        text = html.text

        if not os.path.exists('video/cache'):
            os.mkdir('video/cache')

        i = 0
        for line in text.split('\n'):
            if line.startswith('http'):
                self.download_big_file(line, 'video/cache/{:0>5d}.ts'.format(i))
                i += 1

            if line == '#EXT-X-ENDLIST':
                break

        with open('video/new.ts', 'wb') as f:
            for file in os.listdir('video/cache'):
                with open(os.path.join('video/cache', file), 'rb') as f1:
                    f.write(f1.read())


if __name__ == '__main__':
    # crawler = CrawlStaticStream()
    # url = 'https://www.ku6.com/index'
    # crawler.crawl(url)

    crawler = CrawlDynamicStream()
    url = 'https://valipl.cp31.ott.cibntv.net/657344BC5A13A717B1EAD3FDC/03000600005C6B7F4EF8D76011BA6AF2A6E978-5325-4768-BCED-3C6668DB0AC6-1-114.m3u8?ccode=0502&duration=1419&expire=18000&psid=e2b2b213da82530ee43969f5cbb8f9e6&ups_client_netip=3da04502&ups_ts=1569220919&ups_userid=&utid=JcbvFXIlWxICAT2gRQLMSpoT&vid=XNTQwMTgxMTE2&vkey=A98d3dfab78184f8f86b8a6b24f9269dc&sm=1&operate_type=1&bc=2&sp=400'
    crawler.crawl(url)
