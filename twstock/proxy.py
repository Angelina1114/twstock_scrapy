import requests                 # 用於發送 HTTP 請求
from bs4 import BeautifulSoup   # 用於解析 HTML 頁面
from queue import Queue         # 用於實作代理池的佇列結構

def get_proxies():
    """抓取公開代理列表並回傳清單"""
    url = "https://www.free-proxy-list.net/"                      # 來源網站 URL
    response = requests.get(url)                                  # 發送 GET 請求取得 HTML
    soup = BeautifulSoup(response.text, "html.parser")            # 解析 HTML 為 BeautifulSoup 物件
    proxies = []                                                  # 初始化空清單存放代理
    for row in soup.find_all("tr"):                               # 遍歷所有資料列
        cols = row.find_all("td")                                 # 取得每個儲存格
        if len(cols) > 0:                                         # 如果這列有資料
            ip = cols[0].text                                     # 取第一欄為 IP
            port = cols[1].text                                   # 取第二欄為 Port
            proxies.append(f"http://{ip}:{port}")                 # 組成 HTTP 代理字串並加入清單
    return proxies                                                # 回傳所有抓到的代理

def check_proxy(proxy):
    """測試單一代理是否可用，能連到 Google 即視為可用"""
    try:
        r = requests.get(
            "http://www.google.com",
            proxies={"http": proxy, "https": proxy},              # 同時設定 HTTP/HTTPS 代理
            timeout=1                                            # 連線逾時時間
        )
        return r.status_code == 200                              # 回傳是否 HTTP 200
    except:
        return False                                             # 任一例外則視為無效

class ProxyPool:
    """簡單的代理池實作，內部使用 FIFO 佇列管理"""
    def __init__(self, proxies):
        self.pool = Queue()                                      # 建立佇列
        for p in proxies:                                        # 把每個代理放入佇列
            self.pool.put(p)

    def get_proxy(self):
        """取得一個代理（阻塞直到有可用代理）"""
        return self.pool.get()                                   # 從佇列取出並回傳

    def return_proxy(self, proxy):
        """將使用後的代理放回佇列底部"""
        self.pool.put(proxy)                                     # 重新加入佇列
