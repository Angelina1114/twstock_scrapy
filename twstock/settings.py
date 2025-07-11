# Scrapy settings for twstock project
# settings.py: Scrapy

BOT_NAME = 'twstock'

SPIDER_MODULES = ['twstock.spiders']
NEWSPIDER_MODULE = 'twstock.spiders'

# 基本下載限制
# DOWNLOAD_DELAY: 每次請求後的等待時間（秒），避免請求過快導致被封 IP
DOWNLOAD_DELAY = 1.5        # 基準延遲時間
RANDOMIZE_DOWNLOAD_DELAY = True   # 隨機化因子

# CONCURRENT_REQUESTS_PER_DOMAIN: 同一域名的最大併發請求數
# 控制與單一網站的同時連線數，減少對伺服器的壓力
CONCURRENT_REQUESTS_PER_DOMAIN = 2  # 同站點最多2個併發請求

# AutoThrottle 自動限速設置
# 根據伺服器回應時間動態調整請求速率，讓爬蟲更智能地控制流量
AUTOTHROTTLE_ENABLED = True                   # 開啟自動限速功能
AUTOTHROTTLE_START_DELAY = 0.5               # 初始限速延遲為0.5秒
AUTOTHROTTLE_MAX_DELAY = 5.0                 # 當伺服器回應慢時，最大延遲不超過5秒
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0        # 目標並發數量，每秒向相同站點發送1次請求

# Retry 重試配置
# 遇到暫時性錯誤（如5xx）或連線中斷，允許自動重試
RETRY_ENABLED = True    # 啟用重試機制
RETRY_TIMES = 5         # 最多重試3次
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]  # 可重試的 HTTP 狀態碼

# Pipeline: 處理解析後的 Item 並輸出 CSV
# 數字越小，優先級越高，300為中等優先
ITEM_PIPELINES = {
    'twstock.pipelines.DailyCsvPipeline': 300,
}

# 更換 User-Agent，模擬不同的瀏覽器
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/121.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0',
}

# Logging 日誌設定
LOG_LEVEL = 'INFO'    # 可設為 'DEBUG' 查看更詳細的執行資訊

SPIDER_MIDDLEWARES = {
    'twstock.middlewares.TwstockMiddleware': 543,
}

