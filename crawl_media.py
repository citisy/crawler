import re
import os
import traceback
import logging
import requests
from urllib.parse import urlparse
from tqdm import tqdm
from Crypto.Cipher import AES
from basic_crawler import Crawler, add_try, add_delay, add_callback


class StaticStreamCrawler(Crawler):
    """静态流文件抓取"""
    @add_delay()
    def repeat_crawl(self, url, *args, **kwargs):
        video_save_path = args[0] if len(args) > 0 else None
        self.save_as_big_file(url, video_save_path)


class DynamicStreamCrawler(Crawler):
    """m3u8视频文件抓取"""
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

    def start4url(self, url, *args,
                  get_response_kwargs=dict(),
                  run_kwargs=dict(),
                  **kwargs):
        return super(DynamicStreamCrawler, self).start4url(
            url,
            get_response_kwargs=dict(auto_encoding=False, **get_response_kwargs),
            run_kwargs=run_kwargs
        )

    def run(self, response, *args, m3u8_save_path=None, video_save_path=None, **kwargs):
        if m3u8_save_path:
            self.save_as_file(response.content, m3u8_save_path)

        response.encoding = 'utf8'
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

        if 'EXT-X-KEY' in text:
            key_uri = re.findall('URI="(.+)"', text)[0]
            key_url = home_url + '/' + key_uri
            key = self.session.get(key_url).content
            with open('key', 'wb') as f:
                f.write(key)
            aes = AES.new(key, AES.MODE_CBC, key)

        if os.path.exists('cache_url'):     # 从上次下载失败的地方重新下载
            with open('cache_url', 'r', encoding='utf8') as f:
                cache_url = f.read().split('\n')
            video_output_file = open(video_save_path, 'ab')
        else:
            cache_url = []
            video_output_file = open(video_save_path, 'wb')

        if video_save_path:
            try:
                for ts_url in tqdm(ts_urls):
                    if ts_url in cache_url:
                        continue

                    ts = self.get_repeat_response(ts_url, *args, timeout=10)

                    if 'EXT-X-KEY' in text:
                        video_output_file.write(aes.decrypt(ts.content))
                    else:
                        video_output_file.write(ts.content)

                    cache_url.append(ts_url)

                video_output_file.close()

                if os.path.exists('cache_url'):
                    os.remove('cache_url')

            except Exception:  # 程序失败时，缓存已经下载的url，以便后面重新下载
                with open('cache_url', 'w', encoding='utf8') as f:
                    f.write('\n'.join(cache_url))

                video_output_file.close()

                traceback.print_exc()
                exit(1)

    @add_try(count=3, err_type=requests.exceptions.ReadTimeout)
    def get_repeat_response(self, url: str, *args, **kwargs):
        response = self.session.get(url, **kwargs)

        response.raise_for_status()

        assert response, f'{response = }'

        return response
