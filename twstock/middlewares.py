from scrapy import signals

class TwstockMiddleware:
    """
    自定義中介軟體類別
    用於攔截和處理 Scrapy 的請求(Request)和回應(Response)
    """
    
    @classmethod
    def from_crawler(cls, crawler):
        """
        類別方法：從 Crawler 物件建立 Middleware 實例
        這是 Scrapy 建立 Middleware 的標準方式
        
        Args:
            crawler: Scrapy 的 Crawler 物件
            
        Returns:
            TwstockMiddleware: 中介軟體實例
        """
        # 建立中介軟體實例
        mw = cls()
        # 連接信號：當爬蟲開始時會觸發 spider_opened 方法
        crawler.signals.connect(mw.spider_opened, signal=signals.spider_opened)
        return mw

    def process_request(self, request, spider):
        """
        處理每個發出的請求
        在請求發送到目標網站之前會被呼叫
        
        Args:
            request: Scrapy Request 物件
            spider: 當前的爬蟲實例
            
        Returns:
            None: 繼續處理請求
            Response: 直接返回回應，跳過實際請求
            Request: 返回新的請求來替代原請求
        """
        # 移除重複的 Accept-Language 設定（已在 settings.py 中設定）
        # request.headers.setdefault('Accept-Language', 'zh-TW,zh;q=0.9')
        
        # 可以在這裡做其他請求處理，例如：
        # 動態設定 User-Agent
        # request.headers.setdefault('User-Agent', spider.settings.get('USER_AGENT'))
        
        # 如需使用代理伺服器，可在此設置：
        # request.meta['proxy'] = 'http://your.proxy:port'
        
        # 記錄請求信息（可選）
        spider.logger.debug(f"處理請求: {request.url}")
        
        # 返回 None 表示繼續正常處理請求
        return None

    def process_response(self, request, response, spider):
        """
        處理每個收到的回應
        在回應傳遞給爬蟲的 callback 方法之前會被呼叫
        
        Args:
            request: 原始的 Request 物件
            response: 收到的 Response 物件
            spider: 當前的爬蟲實例
            
        Returns:
            Response: 回傳處理過的回應物件
            Request: 回傳新請求以重新發送
        """
        # 檢查回應狀態碼，如果不是 200 則記錄警告
        if response.status != 200:
            spider.logger.warning(f"非預期狀態碼 {response.status} for {request.url}")
        
        # 回傳原始回應物件給下一個處理階段
        return response

    def process_exception(self, request, exception, spider):
        """
        處理請求過程中發生的例外
        當請求處理過程中發生錯誤時會被呼叫
        
        Args:
            request: 發生錯誤的 Request 物件
            exception: 發生的例外物件
            spider: 當前的爬蟲實例
            
        Returns:
            None: 讓其他中介軟體繼續處理
            Response: 回傳假的回應物件
            Request: 回傳新請求以重試
        """
        # 記錄錯誤信息到日誌
        spider.logger.error(f"Request exception {exception} for {request.url}")
        
        # 返回 None 讓其他中介軟體或 Scrapy 的重試機制處理
        return None

    def spider_opened(self, spider):
        """
        爬蟲開始時的回調方法
        當爬蟲開始運行時會被自動呼叫
        
        Args:
            spider: 開始運行的爬蟲實例
        """
        # 記錄爬蟲開始的信息
        spider.logger.info(f"Spider {spider.name} 開始爬取。")