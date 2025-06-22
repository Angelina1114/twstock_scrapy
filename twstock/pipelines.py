# Define your item pipelines here
# pipelines.py: 處理 Item，並依股票產生 CSV

# useful for handling different item types with a single interface
import os
import csv
from datetime import datetime

class DailyCsvPipeline:
    def open_spider(self, spider):
        # 啟動爬蟲時，建立根資料夾
        self.root_folder = os.path.join('個股日成交資訊')
        os.makedirs(self.root_folder, exist_ok=True)
        # 管理已開啟的檔案與已寫入日期：key=(stock_no, market_tag, year_month)
        self.files = {}
        self.written_dates = {}
        # CSV 欄位順序
        self.fields = [
            '股票代號', '股票名稱', '日期', '成交股數', '成交金額',
            '開盤價', '最高價', '最低價', '收盤價', '漲跌價差', '成交筆數'
        ]

    def process_item(self, item, spider):
        # 每支股票一個子資料夾
        stock_folder = f"{item['stock_no']}_{item['stock_name']}_{item['market_tag']}"
        folder_path = os.path.join(self.root_folder, stock_folder)
        os.makedirs(folder_path, exist_ok=True)

        # 以年月作為檔名，例如 '202506.csv'
        year_month = item['date'][:6]
        filename = f"{year_month}.csv"
        filepath = os.path.join(folder_path, filename)

        key = (item['stock_no'], item['market_tag'], year_month)
        # 若尚未開啟此檔案，就建立、初始化 writer 與已寫入日期集合
        if key not in self.files:
            # 檢查檔案是否已存在
            exists = os.path.exists(filepath)
            # 開啟檔案為 append 模式
            f = open(filepath, 'a', encoding='utf-8-sig', newline='')
            writer = csv.writer(f)

            # 若為新檔案或檔案大小為 0，先寫入標頭
            if not exists or os.path.getsize(filepath) == 0:
                writer.writerow(self.fields)
                written = set()
            else:
                # 讀取已存在的日期欄位以避免重複寫入
                written = set()
                with open(filepath, encoding='utf-8-sig') as rf:
                    reader = csv.reader(rf)
                    headers = next(reader, [])
                    if '日期' in headers:
                        idx = headers.index('日期')
                        for r in reader:
                            if len(r) > idx:
                                written.add(r[idx])
            self.files[key] = (f, writer)
            self.written_dates[key] = written
        else:
            f, writer = self.files[key]
            written = self.written_dates[key]

        # 若該日期已寫入，跳過
        if item['date'] in written:
            return item

        # 準備寫入一列資料
        row = [
            item.get('stock_no',''), item.get('stock_name',''), item.get('date',''),
            item.get('volume_shares',''), item.get('turnover_amount',''),
            item.get('open_price',''), item.get('high_price',''),
            item.get('low_price',''), item.get('close_price',''),
            item.get('change',''), item.get('transactions','')
        ]
        writer.writerow(row)
        # 標記此日期已寫入
        written.add(item['date'])
        return item

    def close_spider(self, spider):
        # 爬蟲結束時關閉所有檔案
        for f, _ in self.files.values():
            f.close()
