import requests
import csv
import io
import json

def json_to_sheet():
    # 👑 終極直擊：直接下載 165 網站每天公開給民眾下載的歷史數據 CSV 檔案！
    url = "https://165dashboard.tw/api/v1/home/download-daily-stats-csv"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://165dashboard.tw/fraud-method"
    }
    
    try:
        print("正在嘗試直連 165 檔案庫，強制下載歷史 CSV 檔案...")
        response = requests.get(url, headers=headers, timeout=20)
        
        # 萬一連下載檔案也被阻擋，回報錯誤
        if response.status_code == 403:
            print("錯誤：165 下載區也對 GitHub 機房實施了 IP 封鎖。")
            return
            
        response.raise_for_status()
        
        # 將下載下來的文字轉換成 CSV 讀取器 (支援 UTF-8-SIG 防亂碼)
        csv_file = io.StringIO(response.content.decode('utf-8-sig', errors='ignore'))
        reader = csv.reader(csv_file)
        
        # 讀取表頭
        header = next(reader, None)
        print(f"檔案下載成功！偵測到欄位表頭為: {header}")
        
        payload_list = []
        
        # 逐行讀取 CSV 內容
        for row in reader:
            if not row or len(row) < 5:
                continue
            
            # 智慧欄位對齊：CSV 裡面的第一欄通常是日期，後面依序是受理件數、財損、假投資、假投資財損
            date_val = str(row[0]).strip().replace('/', '-')
            
            def safe_int(val):
                cleaned = ''.join(c for c in str(val) if c.isdigit())
                return int(cleaned) if cleaned else 0

            payload_list.append({
                "date": date_val,
                "total_cases": safe_int(row[1]),
                "total_loss": safe_int(row[2]),
                "inv_cases": safe_int(row[3]),
                "inv_loss": safe_int(row[4])
            })
            
        if not payload_list:
            print("錯誤：下載的 CSV 檔案內容為空或無法解析。")
            return
            
        # 👑 你的 Google Sheet 接收端網址
        google_sheet_api_url = "https://script.google.com/macros/s/AKfycbxrln86Bf0gB0qONPqgpWFPNfWaW9hNJsx5xoK4jICMkuANXzwCQL4TrNECGoOUm0hf/exec"
        sheet_headers = {"Content-Type": "application/json"}
        
        # 限制只抓最近最新的 5 筆歷史資料外送，免得洗板
        print(f"CSV 解析完畢！成功撈出 {len(payload_list)} 筆歷史紀錄。準備傳送最新 5 筆至 Google Sheet...")
        
        for payload in payload_list[:5]:
            post_res = requests.post(google_sheet_api_url, data=json.dumps(payload), headers=sheet_headers, timeout=15)
            print(f"日期 {payload['date']} -> 傳送結果: {post_res.text}")
            
    except Exception as e:
        print(f"系統執行期間發生錯誤: {str(e)}")

if __name__ == "__main__":
    json_to_sheet()
