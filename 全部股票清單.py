from playwright.sync_api import sync_playwright
import json
import time

stock_data = {
    "上市股票": {
        "類別": {}
    },
    "上櫃股票": {
        "類別": {}
    }
}

def listed_stock_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("🔵 正在前往：上市公司整合資訊")
        page.goto("https://www.twse.com.tw/zh/listed/profile/company.html")
        page.wait_for_load_state("networkidle")
        page.click("a.stock-code-browse")
        time.sleep(1)
        page.wait_for_selector("button[data-sub='TIB']", state="visible")
        page.click("button[data-sub='TIB']")

        # 創新板
        category = "創新板"
        page.wait_for_selector("div.panel.sub_TIB button", state="visible")
        buttons = page.locator("div.panel.sub_TIB button")
        stock_data["上市股票"]["類別"][category] = []

        for i in range(buttons.count()):
            text = buttons.nth(i).inner_text()
            if " " in text:
                code, name = text.split(" ", 1)
            else:
                code = text.split()[0]
                name = text[len(code):].strip()
            print(f"📂 抓取：{category} - {code} {name}")
            stock_data["上市股票"]["類別"][category].append({"代碼": code, "名稱": name})

        page.click("a.back")

        # 其他產業分類
        handles = page.locator("button[data-sub]").element_handles()
        subs = [
            h.get_attribute("data-sub")
            for h in handles
            if h.get_attribute("data-sub") and h.get_attribute("data-sub").isdigit() and len(h.get_attribute("data-sub")) == 2
        ]

        for sub in subs:
            try:
                page.click(f"button[data-sub='{sub}']")
                page.wait_for_selector(f"div.panel.sub_{sub} button", timeout=3000)
                category = page.locator(f"div.face2 h3").inner_text().strip()
                buttons = page.locator(f"div.panel.sub_{sub} button")

                stock_data["上市股票"]["類別"].setdefault(category, [])

                for i in range(buttons.count()):
                    text = buttons.nth(i).inner_text()
                    if " " in text:
                        code, name = text.split(" ", 1)
                    else:
                        code = text.split()[0]
                        name = text[len(code):].strip()
                    print(f"📂 抓取：{category} - {code} {name}")
                    stock_data["上市股票"]["類別"][category].append({"代碼": code, "名稱": name})
            except Exception as e:
                print(f"⚠️ 類別代碼 {sub} 無資料，跳過")
            finally:
                page.click("a.back")


def otc_stock_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("🟠 正在前往：上櫃公司產業分類")
        page.goto("https://www.tpex.org.tw/zh-tw/mainboard/listed/company.html")
        page.wait_for_load_state("networkidle")
        page.wait_for_selector("select[name='cate']")

        options = page.locator("select[name='cate'] option")
        for i in range(options.count()):
            value = options.nth(i).get_attribute("value")
            label = options.nth(i).inner_text().strip()

            if not value or not value.isdigit():
                continue

            print(f"📂 抓取：{label}（value={value}）")
            page.click("select[name='cate']")
            time.sleep(0.5)  # 等待下拉選單展開
            page.select_option("select[name='cate']", value=value)
            page.keyboard.press("Enter")

            try:
                page.wait_for_selector("table.C1_.R3.C4", timeout=1000)
            except:
                print(f"⚠️ {label} 無資料，略過")
                continue

            rows = page.locator("table.C1_ tbody tr")
            records = []
            for j in range(rows.count()):
                cells = rows.nth(j).locator("td")
                if cells.count() >= 2:
                    code = cells.nth(0).inner_text().strip()
                    name = cells.nth(1).inner_text().strip()
                    records.append({"代碼": code, "名稱": name})
                    print(f"📂 抓取：{label} - {code} {name}")
            stock_data["上櫃股票"]["類別"][label] = records
            print(f"✅ {label} 共擷取 {len(records)} 筆")

            time.sleep(0.5)

# 執行兩個流程
listed_stock_data()
otc_stock_data()


# 合併上市＋上櫃資料為單一列表格式
merged_list = []

for market in ["上市股票", "上櫃股票"]:
    for category, stocks in stock_data[market]["類別"].items():
        for stock in stocks:
            stock["類別"] = category
            stock["市場"] = "上市" if market == "上市股票" else "上櫃"
            merged_list.append(stock)

# 輸出合併後的 JSON 檔案
with open("twstock/全部股票清單.json", "w", encoding="utf-8") as f:
    json.dump(merged_list, f, ensure_ascii=False, indent=2)

print("📦 已輸出合併後格式")
