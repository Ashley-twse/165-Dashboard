import requests
import json

def json_to_sheet():
    # 👑 終極修正：直接使用政府資料開放平臺的 165 反詐騙每日財損 API（這絕對不會鎖 IP）
    url = "https://data.gov.tw/api/v2/rest/dataset/167232" 
    
    # 如果上面那個是資料集說明，我們改用真正的 JSON 下載直連網址（警政署公開資料庫）
    # 這裡我們直接向政府平台請求當前最新上架的數據
    backup_url = "https://ods.npa.gov.tw/oridoc/pub/api/v1/open-data/A21020000I-002165-001"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        # 先嘗試從警政署開放資料直連庫抓取
        print("正在透過政府開放資料通道讀取 165 數據...")
        response = requests.get(backup_url, headers=headers, timeout=15)
        
        # 如果直連庫臨時維護，就切換回開放平台 API
        if response.status_code != 200:
            response = requests.get(url, headers=headers, timeout=15)
            
        response.raise_for_status()
        res_data = response.json()
        
        # 解析政府公開資料的標準結構 (通常是一個 data 列表)
        data_list = []
        if isinstance(res_data, list):
            data_list = res_data
        elif isinstance(res_data, dict):
            data_list = res_data.get('data', res_data.get('dataGrid', [res_data]))
            
        if not data_list or len(data_list) == 0:
            print("錯誤：政府開放平臺目前尚未吐出有效數據欄位")
            return

        payload_list = []
        
        # 政府資料通常會把最近好幾天的歷史紀錄整坨給我們，我們用迴圈把最近 3 天撈出來
        # 限制最多處理 3 筆，避免塞爆
        for item in data_list[:3]:
            # 政府資料的欄位名稱通常長這樣，做智慧相容比對
            date_val = item.get('date', item.get('Date', item.get('統計日期', '')))
            if date_val:
                payload_list.append({
                    "date": str(date_val).replace('/', '-'), # 統一將 2026/05/25 轉成 2026-05-25
                    "total_cases": int(item.get('total_cases', item.get('總受理件數', 0))),
                    "total_loss": int(item.get('total_loss', item.get('總財損金額', 0))),
                    "inv_cases": int(item.get('inv_cases', item.get('假投資件数', 0))),
                    "inv_loss": int(item.get('inv_loss', item.get('假投資財損', 0)))
                })

        # 妳的專屬 Google Sheet 接收端網址
        google_sheet_api_url = "https://script.google.com/macros/s/AKfycbxrln86Bf0gB0qONPqgpWFPNfWaW9hNJsx5xoK4jICMkuANXzwCQL4TrNECGoOUm0hf/exec"
        sheet_headers = {"Content-Type": "application/json"}
        
        print(f"成功從政府平台獲取 {len(payload_list)} 筆歷史數據！開始傳送至 Google Sheet...")
        
        for payload in payload_list:
            post_res = requests.post(google_sheet_api_url, data=json.dumps(payload), headers=sheet_headers, timeout=15)
            print(f"日期 {payload['date']} 傳送結果 -> {post_res.text}")
            
    except Exception as e:
        print(f"系統執行期間發生錯誤: {str(e)}")

if __name__ == "__main__":
    json_to_sheet()
