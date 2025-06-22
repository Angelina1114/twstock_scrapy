# spiders/daily.py: 日成交資料爬取邏輯
import json
import os
import scrapy
from datetime import datetime
from twstock.items import DailyItem
from twstock.logger import init_log_file, append_log

class DailySpider(scrapy.Spider):
    name = 'daily'
    allowed_domains = ['twse.com.tw', 'tpex.org.tw']
    
    # 處理重定向狀態碼
    handle_httpstatus_list = [307, 302, 301]

    def __init__(self):
        # 初始化 log 檔案
        self.log_path = init_log_file('個股日成交資訊/logs')
        # self.logger.info("🚀 DailySpider 初始化完成")

    def convert_roc_to_western_date(self, date_str):
        """將民國年日期轉換為西元年 YYYYMMDD 格式"""
        parts = date_str.split('/')
        if len(parts)==3:
            try:
                roc_year = int(parts[0])
                western_year = roc_year + 1911
                month = f"{int(parts[1]):02d}"
                day = f"{int(parts[2]):02d}"
                return f"{western_year}{month}{day}"
            except ValueError:
                append_log(self.log_path, '日期轉換', date_str, '日期格式錯誤')
                return None
        # fallback：移除斜線並補零，或直接回傳原字串
        return date_str.replace('/', '')

    def start_requests(self):
        self.logger.info("📋 開始讀取股票清單...")
        # 1) 讀 JSON 清單
        project_root = os.path.dirname(os.path.dirname(__file__))
        json_path = os.path.join(project_root, '全部股票清單.json')
        try:
            with open(json_path, encoding='utf-8') as f:
                stocks = json.load(f)
            self.logger.info(f"✅ 成功讀取 {len(stocks)} 支股票")
        except Exception as e:
            self.logger.error(f"❌ 無法讀取股票清單: {e}")
            append_log(self.log_path, 'SYSTEM', '系統', f'讀取股票清單失敗: {e}')
            return

        # 2) 今日參數
        today = datetime.now().strftime('%Y%m%d')
        date_str = f"{today[:4]}/{today[4:6]}/{today[6:]}"

        # 3) 篩選
        listed_stocks = [s for s in stocks if s.get('市場') == '上市']
        otc_stocks    = [s for s in stocks if s.get('市場') == '上櫃']
        self.logger.info(f"📊 將處理 {len(listed_stocks)} 支上市，{len(otc_stocks)} 支上櫃")

        # 4) 同一迴圈交錯發出上市與上櫃請求
        max_len = max(len(listed_stocks), len(otc_stocks))
        for i in range(max_len):
            # 上市請求
            if i < len(listed_stocks):
                s = listed_stocks[i]
                code, name = s['代碼'], s['名稱']
                url = (
                    'https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY'
                    f'?date={today}&stockNo={code}&response=json'
                )
                yield scrapy.Request(
                    url,
                    callback=self.parse_listed,
                    meta={'stock': s},
                    errback=self.handle_error
                )

            # 上櫃請求
            if i < len(otc_stocks):
                s = otc_stocks[i]
                code, name = s['代碼'], s['名稱']
                yield scrapy.FormRequest(
                    url='https://www.tpex.org.tw/www/zh-tw/afterTrading/tradingStock',
                    formdata={'date': date_str, 'code': code, 'response': 'json'},
                    callback=self.parse_otc,
                    meta={'stock': s},
                    errback=self.handle_error
                )

    def handle_error(self, failure):
        """統一錯誤處理"""
        request = failure.request
        stock = request.meta.get('stock', {})
        code = stock.get('代碼', 'Unknown')
        name = stock.get('名稱', 'Unknown')
        
        self.logger.error(f"❌ 請求失敗 {code} {name}: {failure.value}")
        append_log(self.log_path, code, name, f'請求失敗: {failure.value}')

    def parse_listed(self, response):
        # 處理上市日成交 API 回傳
        s = response.meta['stock']
        code = s['代碼']
        name = s['名稱']
        
        self.logger.info(f"📥 收到上市回應: {code} {name} (狀態碼: {response.status})")
        
        # 處理重定向
        if response.status in [301, 302, 307]:
            self.logger.warning(f"🔄 {code} {name} 收到重定向 {response.status}")
            append_log(self.log_path, code, name, f'收到重定向狀態碼 {response.status}')
            return
            
        try:
            text = getattr(response, 'text', response.body.decode('utf-8'))
            data = json.loads(text)
            self.logger.debug(f"✅ {code} {name} JSON 解析成功")
        except Exception as e:
            self.logger.error(f"❌ {code} {name} JSON 解析失敗: {e}")
            append_log(self.log_path, code, name, f'JSON 解析失敗: {e}')
            return
            
        if data.get('stat') != 'OK':
            status = data.get('stat', 'Unknown')
            self.logger.warning(f"⚠️ {code} {name} API 狀態異常: {status}")
            append_log(self.log_path, code, name, f'API 狀態異常: {status}')
            return
            
        data_rows = data.get('data', [])
        self.logger.info(f"📊 {code} {name} 取得 {len(data_rows)} 筆交易資料")
        
        items_count = 0
        for row in data_rows:
            if len(row) < 9: 
                continue
            
            # 使用函式轉換日期
            date = self.convert_roc_to_western_date(row[0])
            
            if date:  # 確保日期轉換成功
                yield DailyItem(
                    stock_no        = code,
                    stock_name      = name,
                    market_tag      = '上市',
                    date            = date,
                    volume_shares   = row[1].replace(',', ''),
                    turnover_amount = row[2].replace(',', ''),
                    open_price      = row[3],
                    high_price      = row[4],
                    low_price       = row[5],
                    close_price     = row[6],
                    change          = row[7],
                    transactions    = row[8],
                )
                items_count += 1
        
        self.logger.info(f"✅ {code} {name} 成功產生 {items_count} 筆 DailyItem")

    def parse_otc(self, response):
        # 處理上櫃日成交 API 回傳
        s = response.meta['stock']
        code = s['代碼']
        name = s['名稱']
        
        self.logger.info(f"📥 收到上櫃回應: {code} {name} (狀態碼: {response.status})")
        
        # 處理重定向
        if response.status in [301, 302, 307]:
            self.logger.warning(f"🔄 {code} {name} 收到重定向 {response.status}")
            append_log(self.log_path, code, name, f'收到重定向狀態碼 {response.status}')
            return
            
        try:
            data = json.loads(response.text)
            self.logger.debug(f"✅ {code} {name} JSON 解析成功")
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ {code} {name} JSON 解析失敗: {e}")
            append_log(self.log_path, code, name, f'JSON 解析失敗: {e}')
            return
            
        tables = data.get('tables') or []
        if not tables:
            self.logger.warning(f"⚠️ {code} {name} 無上櫃交易資料")
            append_log(self.log_path, code, name, '無上櫃日成交資料')
            return
            
        data_rows = tables[0].get('data', [])
        self.logger.info(f"📊 {code} {name} 取得 {len(data_rows)} 筆交易資料")
        
        items_count = 0
        for row in data_rows:
            if len(row) < 9: 
                continue
            try:
                vol = str(int(row[1].replace(',', '')) * 1000)
                amt = str(int(row[2].replace(',', '')) * 1000)
            except ValueError as e:
                self.logger.warning(f"⚠️ {code} {name} 數據轉換失敗: {e}")
                continue
            
            # 使用函式轉換日期
            date = self.convert_roc_to_western_date(row[0])
            
            if date:  # 確保日期轉換成功
                yield DailyItem(
                    stock_no        = code,
                    stock_name      = name,
                    market_tag      = '上櫃',
                    date            = date,
                    volume_shares   = vol,
                    turnover_amount = amt,
                    open_price      = row[3],
                    high_price      = row[4],
                    low_price       = row[5],
                    close_price     = row[6],
                    change          = row[7],
                    transactions    = row[8],
                )
                items_count += 1
        
        self.logger.info(f"✅ {code} {name} 成功產生 {items_count} 筆 DailyItem")
