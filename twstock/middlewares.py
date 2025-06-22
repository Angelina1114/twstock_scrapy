from scrapy import signals
from twstock.logger import init_log_file, append_log

class TwstockMiddleware:
    """
    通用中介軟體：處理所有爬蟲共用的邏輯
    主要負責：
    1. 系統級別的錯誤記錄
    2. 通用的請求/回應處理
    3. 與業務邏輯無關的基礎功能
    """
    
    def __init__(self):
        # 系統級別的錯誤日誌，與具體爬蟲業務無關
        self.log_path = init_log_file('個股日成交資訊/logs')
    
    @classmethod
    def from_crawler(cls, crawler):
        mw = cls()
        crawler.signals.connect(mw.spider_opened, signal=signals.spider_opened)
        return mw

    def process_request(self, request, spider):
        # 只記錄系統級的請求信息，不重複業務日誌
        spider.logger.debug(f"🔄 中介軟體處理請求: {request.url}")
        return None

    def process_response(self, request, response, spider):
        # 只處理系統級的狀態碼問題，不處理業務邏輯
        if response.status >= 500:  # 只記錄伺服器錯誤
            spider.logger.error(f"❌ 伺服器錯誤 {response.status}: {request.url}")
            append_log(
                self.log_path,
                'SYSTEM',
                'SERVER_ERROR',
                f"HTTP {response.status}: {request.url}"
            )
        return response

    def process_exception(self, request, exception, spider):
        # 只記錄系統級異常（網路、連線等），不重複業務異常
        error_type = type(exception).__name__
        if error_type in ['TimeoutError', 'ConnectionError', 'DNSLookupError']:
            spider.logger.error(f"❌ 系統異常 {error_type}: {request.url}")
            append_log(
                self.log_path,
                'SYSTEM',
                error_type,
                f"{exception} for {request.url}"
            )
        return None

    def spider_opened(self, spider):
        spider.logger.info(f"🚀 {spider.name} 爬蟲已啟動")


class ProxyMiddleware:
    """
    代理中介軟體：專門處理代理相關功能
    """
    
    def __init__(self, proxy_pool):
        self.proxy_pool = proxy_pool
        # 代理專用日誌
        self.log_path = init_log_file('代理管理/logs')

    @classmethod
    def from_crawler(cls, crawler):
        proxy_pool = crawler.settings.get('PROXY_POOL_INSTANCE')
        if not proxy_pool:
            raise ValueError("未設定 PROXY_POOL_INSTANCE")
        return cls(proxy_pool)

    def process_request(self, request, spider):
        try:
            proxy = self.proxy_pool.get_proxy()
            request.meta['proxy'] = proxy
            spider.logger.debug(f"🔄 分配代理: {proxy}")
        except Exception as e:
            spider.logger.error(f"❌ 代理分配失敗: {e}")
            append_log(
                self.log_path,
                'PROXY',
                'ALLOCATION_FAILED',
                f"代理分配失敗: {e}"
            )
        return None

    def process_response(self, request, response, spider):
        proxy = request.meta.get('proxy')
        
        if response.status == 200:
            # 成功使用代理
            if proxy and hasattr(self.proxy_pool, 'return_proxy'):
                self.proxy_pool.return_proxy(proxy)
        elif response.status in [403, 407, 429]:  # 代理相關錯誤
            spider.logger.warning(f"⚠️ 代理被封: {proxy} (狀態: {response.status})")
            append_log(
                self.log_path,
                'PROXY',
                'BLOCKED',
                f"代理 {proxy} 被封鎖: HTTP {response.status}"
            )
        
        return response

    def process_exception(self, request, exception, spider):
        proxy = request.meta.get('proxy')
        
        # 只處理代理相關異常
        if 'proxy' in str(exception).lower() or 'tunnel' in str(exception).lower():
            spider.logger.warning(f"❌ 代理異常: {proxy} - {exception}")
            append_log(
                self.log_path,
                'PROXY',
                'CONNECTION_FAILED',
                f"代理 {proxy} 連線失敗: {exception}"
            )
        
        return None
