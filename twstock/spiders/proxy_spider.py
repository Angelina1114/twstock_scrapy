# spiders/proxy_spider.py
import scrapy

class ProxySpider(scrapy.Spider):
    name = 'proxy_spider'
    start_urls = ['http://httpbin.org/ip']  # 用來驗證你的代理

    def parse(self, response):
        # httpbin 會回傳實際外部 IP，確認代理生效
        self.logger.info(f"🔍 透過代理取得的 IP：{response.text}")
