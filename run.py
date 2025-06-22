# run.py
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def run_with_proxy():
    """使用代理運行爬蟲"""
    try:
        # 嘗試匯入代理相關模組
        from twstock.proxy import get_proxies, check_proxy, ProxyPool
        from twstock.logger import init_log_file, append_log
        
        print("🔍 開始檢查代理...")
        
        # 初始化日誌
        log_path = init_log_file('個股日成交資訊/logs')
        
        # 1. 抓取並篩選出有效代理
        all_proxies = get_proxies()
        print(f"📋 取得 {len(all_proxies)} 個代理")
        
        valid_proxies = []
        for proxy in all_proxies:
            print(f"🔍 檢查代理: {proxy}")
            if check_proxy(proxy):
                valid_proxies.append(proxy)
                print(f"✅ 代理有效: {proxy}")
        
        if not valid_proxies:
            print("❌ 沒有任何有效代理！改用無代理模式...")
            return run_without_proxy()
        
        print(f"✅ 找到 {len(valid_proxies)} 個有效代理")
        append_log(log_path, '代理管理', '系統', f'有效代理數量: {len(valid_proxies)}')
        
        # 2. 建立代理池實例
        proxy_pool = ProxyPool(valid_proxies)
        
        # 3. 獲取並修改設定
        settings = get_project_settings()
        settings.set('PROXY_POOL', valid_proxies)
        settings.set('PROXY_POOL_INSTANCE', proxy_pool)
        
        # 4. 啟用代理中介軟體
        middlewares = settings.get('DOWNLOADER_MIDDLEWARES', {})
        middlewares['twstock.middlewares.ProxyMiddleware'] = 100
        settings.set('DOWNLOADER_MIDDLEWARES', middlewares)
        
        print("🚀 使用代理模式啟動爬蟲...")
        
        # 5. 啟動爬蟲
        process = CrawlerProcess(settings)
        process.crawl('daily')  # 使用你的爬蟲名稱
        process.start()
        
    except ImportError as e:
        print(f"⚠️ 無法匯入代理模組: {e}")
        print("💡 改用無代理模式...")
        return run_without_proxy()
    except Exception as e:
        print(f"❌ 代理設定失敗: {e}")
        print("💡 改用無代理模式...")
        return run_without_proxy()

def run_without_proxy():
    """不使用代理運行爬蟲"""
    print("🚀 無代理模式啟動爬蟲...")
    
    try:
        # 獲取專案設定
        settings = get_project_settings()
        
        # 確保代理中介軟體被停用
        middlewares = settings.get('DOWNLOADER_MIDDLEWARES', {})
        if 'twstock.middlewares.ProxyMiddleware' in middlewares:
            del middlewares['twstock.middlewares.ProxyMiddleware']
            settings.set('DOWNLOADER_MIDDLEWARES', middlewares)
        
        # 啟動爬蟲
        process = CrawlerProcess(settings)
        process.crawl('daily')
        process.start()
        
    except Exception as e:
        print(f"❌ 爬蟲執行失敗: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主程式"""
    print("=" * 50)
    print("🕷️ Taiwan Stock Daily Data Crawler")
    print("=" * 50)
    
    # 檢查目錄
    if not os.path.exists('scrapy.cfg'):
        print("❌ 找不到 scrapy.cfg，請確認在專案根目錄執行")
        return
    
    # 詢問運行模式
    print("\n請選擇運行模式:")
    print("1. 無代理模式 (推薦)")
    print("2. 代理模式")
    
    try:
        choice = input("請輸入選擇 (1 或 2，預設為 1): ").strip()
        
        if choice == "2":
            run_with_proxy()
        else:
            run_without_proxy()
            
    except KeyboardInterrupt:
        print("\n👋 用戶取消運行")
    except Exception as e:
        print(f"❌ 執行失敗: {e}")

if __name__ == "__main__":
    main()
