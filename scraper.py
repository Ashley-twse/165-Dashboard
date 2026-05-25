import requests
import json
from datetime import datetime

def fetch_and_send():
    url = "https://165dashboard.tw/api/v1/home/dashboard-data"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://165dashboard.tw/",
        "Accept": "application/json, text/plain, */*"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"165 網站連線狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            data = result.get("data", {})
            
            stat_date = data.get("date", datetime.today().strftime('%Y-%m-%d'))
            total_cases = data.get("total_cases", 0)       
            total_loss = data.get("total_amount", 0)       
            
            fraud_types = data.get("fraud_types", [])
            inv_cases, inv_loss = 0, 0
            for item in fraud_types:
                if "假投資" in item.get("name", ""):
                    inv_cases = item.get("cases", 0)
                    inv_loss = item.get("amount", 0)
                    break
            
            payload = {
                "date": stat_date,
                "total_cases": total_cases,
                "total_loss": total_loss,
                "inv_cases": inv_cases,
                "inv_loss": inv_loss
            }
            
            google_sheet_api_url = "https://script.google.com/macros/s/AKfycbwMRFlkro3Vi2j7g_bjB732ZIhmtDB-0_pxvreFGbQvXhqybT1xmG5rmbo_b79Si499/exec"
            
            sheet_response = requests.post(google_sheet_api_url, json=payload)
            print(f"Google Sheet 回應結果: {sheet_response.text}")
            
        else:
            print(f"連線 165 失敗")
    except Exception as e:
        print(f"執行過程中發生異常: {e}")

if __name__ == "__main__":
    fetch_and_send()
