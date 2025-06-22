import scrapy

class DailyItem(scrapy.Item):
    stock_no        = scrapy.Field()  # 股票代號
    stock_name      = scrapy.Field()  # 股票名稱
    market_tag      = scrapy.Field()  # 市場標籤："上市" 或 "上櫃"
    date            = scrapy.Field()  # 交易日期，格式 YYYYMMDD
    volume_shares   = scrapy.Field()  # 成交股數
    turnover_amount = scrapy.Field()  # 成交金額
    open_price      = scrapy.Field()  # 開盤價
    high_price      = scrapy.Field()  # 最高價
    low_price       = scrapy.Field()  # 最低價
    close_price     = scrapy.Field()  # 收盤價
    change          = scrapy.Field()  # 漲跌價差
    transactions    = scrapy.Field()  # 成交筆數
