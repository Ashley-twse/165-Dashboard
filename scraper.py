import requests
import json
from datetime import datetime, timedelta

def json_to_sheet():
    # 1. 取得昨天的日期 (台灣時間格式)
    yesterday = (datetime.utcnow() + timedelta(hours=8) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 2. 165 官方開放數據網址
    url = "https://165.npa.gov.tw/api/open/daily-stats"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        res_data = response.json()
        
        # 智慧相容：自動尋找昨天的數據，若找不到則抓最新一筆
        target_data = None
        if isinstance(res_data, list) and len(res_data) > 0:
            for row in res_data:
                if row.get('date') == yesterday or row.get('Date') == yesterday:
                    target_data = row
                    break
            if not target_data:
                target_data = res_data[0] # 備用方案：抓最新一筆
        elif isinstance(res_data, dict):
            target_data = res_data.get('data', res_data)
            
        if not target_data:
            print("錯誤：無法解析 165 官方數據結構")
            return

        # 智慧相容：欄位名稱大掃描 (相容大小寫與新舊名稱)
        date_val = target_data.get('date', target_data.get('Date', yesterday))
        total_cases = target_data.get('total_cases', target_data.get('totalCases', target_data.get('total_count', 0)))
        total_loss = target_data.get('total_loss', target_data.get('totalLoss', target_data.get('total_amount', 0)))
        inv_cases = target_data.get('inv_cases', target_data.get('invCases', target_data.get('investment_count', 0)))
        inv_loss = target_data.get('inv_loss', target_data.get('invLoss', target_data.get('investment_amount', 0)))

        payload = {
            "date": date_val,
            "total_cases": total_cases,
            "total_loss": total_loss,
            "inv_cases": inv_cases,
            "inv_loss": inv_loss
        }
        
        # 🔥 你的專屬 Google Sheet 接收端網址 (確保使用最新綁定表的版本)
        google_sheet_api_url = "https://script.google.com/macros/s/AKfycbxrln86Bf0gB0qONPqgpWFPNfWaW9hNJsx5xoK4jICMkuANXzwCQL4TrNECGoOUm0hf/exec"
        
        headers = {"Content-Type": "application/json"}
        post_res = requests.post(google_sheet_api_url, data=json.dumps(payload), headers=headers, timeout=15)
        
        print(f"發送數據: {payload}")
        print(f"Google Sheet 回應結果: {post_res.text}")
        
    except Exception as e:
        print(f"系統執行期間發生錯誤: {str(e)}")

if __name__ == "__main__":
    json_to_sheet()
