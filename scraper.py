import requests
import json

def json_to_sheet():
    # 165 官方後台最新數據 API
    url = "https://165dashboard.tw/api/v1/home/dashboard-data"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        res_data = response.json()
        
        # 確保解析到最內層的 data 物件
        target_data = res_data.get('data', res_data) if isinstance(res_data, dict) else res_data
        
        if not target_data:
            print("錯誤：無法解析 165 官方數據結構")
            return

        # 🚀 關鍵升級：建立一個待發送的清單，把撈得到的資料都塞進去
        payload_list = []
        
        # 1. 先抓取當天最新的這筆摘要（也就是你昨天抓到 5/25 全是 0 的這筆）
        date_val = target_data.get('date')
        if date_val:
            payload_list.append({
                "date": str(date_val),
                "total_cases": target_data.get('total_cases', 0),
                "total_loss": target_data.get('total_loss', 0),
                "inv_cases": target_data.get('inv_cases', 0),
                "inv_loss": target_data.get('inv_loss', 0)
            })
            
        # 2. 智慧挖掘：看看 API 裡面有沒有藏過去幾天的歷史紀錄陣列 (通常在資料庫的列表欄位裡)
        # 我們掃描常見的歷史欄位名稱，例如 'history', 'trend', 'list'
        history_list = target_data.get('history', target_data.get('trend', target_data.get('list', [])))
        
        if isinstance(history_list, list):
            for item in history_list:
                h_date = item.get('date')
                if h_date:
                    payload_list.append({
                        "date": str(h_date),
                        "total_cases": item.get('total_cases', item.get('totalCases', 0)),
                        "total_loss": item.get('total_loss', item.get('totalLoss', 0)),
                        "inv_cases": item.get('inv_cases', item.get('invCases', 0)),
                        "inv_loss": item.get('inv_loss', item.get('invLoss', 0))
                    })

        # 3. 開始把資料發送給 Google Sheet
        google_sheet_api_url = "https://script.google.com/macros/s/AKfycbxrln86Bf0gB0qONPqgpWFPNfWaW9hNJsx5xoK4jICMkuANXzwCQL4TrNECGoOUm0hf/exec"
        headers = {"Content-Type": "application/json"}
        
        if not payload_list:
            print("未偵測到任何有效數據")
            return
            
        print(f"準備發送 {len(payload_list)} 筆資料至 Google Sheet...")
        
        # 逐筆發送，讓 Google Sheet 透過防重複機制自己篩選
        for payload in payload_list:
            post_res = requests.post(google_sheet_api_url, data=json.dumps(payload), headers=headers, timeout=15)
            print(f"日期 {payload['date']} 發送結果 -> {post_res.text}")
        
    except Exception as e:
        print(f"系統執行期間發生錯誤: {str(e)}")

if __name__ == "__main__":
    json_to_sheet()
