# 台灣股市日成交資料爬蟲

## 📋 專案概述

這是一個基於 Scrapy 框架開發的台灣股市日成交資料爬蟲，能夠自動抓取台灣證券交易所（TWSE）和台灣證券櫃買中心（TPEX）的股票日成交資訊，並輸出為 CSV 格式。

## 🎯 功能特色

- ✅ **全市場覆蓋**：同時支援上市與上櫃股票
- ✅ **高效並行**：交錯發送請求，提升抓取效率
- ✅ **智能重試**：自動處理網路異常和暫時性錯誤
- ✅ **詳細日誌**：完整記錄執行過程和錯誤資訊
- ✅ **資料驗證**：自動檢查和轉換資料格式
- ✅ **CSV 輸出**：結構化資料輸出，便於後續分析

## 📁 專案結構

```
股票資料scrapy/
├── scrapy.cfg                 # Scrapy 專案配置
├── 全部股票清單.json           # 股票清單資料
├── run.py                     # 執行腳本
├── README.md                  # 專案說明文件
├── twstock/
│   ├── __init__.py
│   ├── settings.py           # Scrapy 設定檔
│   ├── items.py              # 資料結構定義
│   ├── pipelines.py          # 資料處理管道
│   ├── middlewares.py        # 中介軟體
│   ├── logger.py             # 日誌工具
│   └── spiders/
│       ├── __init__.py
│       └── daily.py          # 主要爬蟲邏輯
└── 個股日成交資訊/
    └── logs/                 # 執行日誌目錄
        └── YYYY-MM-DD.txt    # 每日日誌檔案
```

## 🚀 快速開始

### 環境需求

- Python 3.7+
- Scrapy 2.0+

### 安裝依賴

```bash
pip install scrapy
```

### 執行爬蟲

#### 方法 1：使用 Scrapy 命令（推薦）

```bash
# 切換到專案目錄
cd /path/to/股票資料scrapy

# 執行爬蟲
scrapy crawl daily

# 查看詳細輸出
scrapy crawl daily -L DEBUG

# 直接輸出到檔案
scrapy crawl daily -o stock_data.csv
```

## 📊 資料來源

### 上市股票（TWSE）
- **API 端點**：`https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY`
- **請求方式**：GET
- **參數**：
  - `date`：查詢日期 (YYYYMMDD)
  - `stockNo`：股票代碼
  - `response`：json

### 上櫃股票（TPEX）
- **API 端點**：`https://www.tpex.org.tw/www/zh-tw/afterTrading/tradingStock`
- **請求方式**：POST
- **參數**：
  - `date`：查詢日期 (YYYY/MM/DD)
  - `code`：股票代碼
  - `response`：json

## 📋 輸出欄位

爬蟲會為每筆交易資料產生以下欄位：

| 欄位名稱 | 說明 | 範例 |
|---------|------|------|
| stock_no | 股票代碼 | 2330 |
| stock_name | 股票名稱 | 台積電 |
| market_tag | 市場類別 | 上市/上櫃 |
| date | 交易日期 | 20240622 |
| volume_shares | 成交股數 | 15000000 |
| turnover_amount | 成交金額 | 9750000000 |
| open_price | 開盤價 | 650.00 |
| high_price | 最高價 | 655.00 |
| low_price | 最低價 | 648.00 |
| close_price | 收盤價 | 652.00 |
| change | 漲跌價差 | +2.00 |
| transactions | 成交筆數 | 12500 |

## ⚙️ 配置說明

### 主要設定（settings.py）

```python
# 請求延遲設定
DOWNLOAD_DELAY = 1.5
RANDOMIZE_DOWNLOAD_DELAY = True

# 併發控制
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# 自動限速
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_MAX_DELAY = 5.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# 重試機制
RETRY_ENABLED = True
RETRY_TIMES = 5
```

### 日誌配置

爬蟲會自動在 `個股日成交資訊/logs/` 目錄下建立每日日誌檔案，記錄：

- 🟡 **警告事件**：API 回應異常、無交易資料
- 🔴 **錯誤事件**：網路錯誤、JSON 解析失敗

### 日誌檔案格式

```
[YYYY-MM-DD HH:MM:SS] Stock: 股票代碼_股票名稱 - Error: 錯誤訊息
```

## 🔧 常見問題

### Q1: 部分股票顯示「沒有符合條件的資料」

**A:** 這是正常現象，可能原因：
- 股票暫停交易或下市
- 特別股當日無交易
- 海外企業（KY股）的特殊交易規則

### Q2: 請求被拒絕或速度過慢

**A:** 可以調整以下設定：
```python
# 增加請求延遲
DOWNLOAD_DELAY = 2.0

# 降低併發數
CONCURRENT_REQUESTS_PER_DOMAIN = 1
```

### Q3: 如何只抓取特定股票？

**A:** 修改 `全部股票清單.json`，只保留需要的股票資料。

### Q4: 輸出檔案在哪裡？

**A:** CSV 檔案會依據 `pipelines.py` 的設定輸出到指定目錄，預設為專案根目錄。

### Q5: 如何檢查爬蟲執行狀況？

**A:** 可以透過以下方式：
```bash
# 查看即時日誌
tail -f 個股日成交資訊/logs/$(date +%Y-%m-%d).txt

# 檢查爬蟲狀態
scrapy crawl daily -L INFO
```

## 📈 執行統計

典型的執行結果：
- **處理股票數**：~1,400 支
- **抓取資料筆數**：~19,000 筆
- **執行時間**：30-40 分鐘
- **成功率**：>95%
- **無交易資料**：~130 支（正常現象）

### 執行完成後的統計範例

```
Scrapy stats:
- 總請求數: 1,443
- 成功回應: 1,443 (100%)
- 資料筆數: 19,646
- 執行時間: 36 分 50 秒
- 記憶體使用: ~88MB
```

## 🛠️ 開發說明

### 核心模組

1. **daily.py**：主要爬蟲邏輯
   - 處理上市/上櫃股票的不同 API
   - 民國年與西元年日期轉換
   - JSON 解析和資料驗證

2. **middlewares.py**：中介軟體
   - 通用錯誤處理
   - 請求/回應日誌記錄
   - 系統級異常管理

3. **logger.py**：日誌系統
   - 自動建立日誌目錄
   - 按日期分類日誌檔案
   - 結構化錯誤記錄

4. **pipelines.py**：資料處理
   - CSV 格式輸出
   - 資料清理和驗證

### 擴展功能

1. **新增資料欄位**：修改 `items.py` 和解析邏輯
2. **支援其他市場**：在 `daily.py` 中新增解析方法
3. **客製化輸出**：修改 `pipelines.py` 支援其他格式
4. **代理支援**：未來可加入 `proxy.py` 模組

### 除錯模式

```bash
# 開啟詳細日誌
scrapy crawl daily -L DEBUG

# 只處理少量股票進行測試
# 修改 start_requests() 方法，限制股票清單大小

# 檢查特定股票
grep "股票代碼" 個股日成交資訊/logs/$(date +%Y-%m-%d).txt
```

## 📦 輸出檔案

### CSV 檔案結構

```csv
stock_no,stock_name,market_tag,date,volume_shares,turnover_amount,open_price,high_price,low_price,close_price,change,transactions
2330,台積電,上市,20240622,15000000,9750000000,650.00,655.00,648.00,652.00,+2.00,12500
2317,鴻海,上市,20240622,8500000,850000000,100.00,102.00,99.50,101.50,+1.50,9800
...
```

### 日誌檔案範例

```
[2024-06-22 14:44:15] Stock: SYSTEM_daily - Error: 爬蟲啟動
[2024-06-22 14:45:30] Stock: 2330_台積電 - Error: 成功產生 31 筆 DailyItem
[2024-06-22 14:46:45] Stock: 1225_福懋油 - Error: API 狀態異常: 很抱歉，沒有符合條件的資料!
```

## ⚠️ 注意事項

1. **合理使用**：請遵守網站的 robots.txt 和服務條款
2. **頻率控制**：避免過於頻繁的請求，以免被封鎖 IP
3. **資料用途**：僅供個人研究和學習使用
4. **時間考量**：建議在非交易時間執行，避免影響交易系統
5. **網路環境**：確保網路連線穩定，避免請求中斷

## 🔮 未來改進

- [ ] 新增代理 IP 支援，提升穩定性
- [ ] 支援歷史資料批量抓取
- [ ] 新增資料庫輸出選項
- [ ] 實作即時監控介面
- [ ] 支援其他金融商品（ETF、權證等）
- [ ] 新增資料視覺化功能

## 📞 技術支援

如遇到問題，請檢查：
1. 網路連線是否正常
2. 股票清單檔案是否存在
3. 日誌檔案中的錯誤訊息
4. Scrapy 版本是否相容
5. Python 環境是否正確設定

### 常見錯誤排除

```bash
# 檢查 Scrapy 安裝
scrapy version

# 檢查專案設定
scrapy check

# 測試單一股票
scrapy parse --spider=daily "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY?date=20240622&stockNo=2330&response=json"
```

---

**免責聲明**：本工具僅供學術研究和個人學習使用，使用者應遵守相關法律法規和網站服務條款。作者不對使用本工具所產生的任何後果承擔責任。

**最後更新**：2025年6月