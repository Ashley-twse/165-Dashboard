import requests
import json

def json_to_sheet():
    # 165 官方後台最新數據 API
    url = "https://165dashboard.tw/api/v1/home/dashboard-data"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        res_data = response.json()
        
        # 直接抓取 165 官網目前最新吐出來的這筆數據物件
        target_data = None
        if isinstance(res_data, dict):
            # 嘗試抓取 data 欄位，若沒有就直接用整個 dict
            target_data = res_data.get('data', res_data)
        elif isinstance(res_data, list) and len(res_data) > 0:
            target_data = res_data[0]
            
        if not target_data:
            print("錯誤：無法解析 165 官方數據結構")
            return

        # 👑 核心修正：直接使用 165 後台這筆資料「真正的日期」，不再用程式硬猜昨天
        date_val = target_data.get('date', target_data.get('Date'))
        
        # 如果後台連日期都沒給，才用預備文字
        if not date_val:
            print("錯誤：165 後台資料目前為空或無有效日期")
            return
            
        total_cases = target_data.get('total_cases', target_data.get('totalCases', target_data.get('total_count', 0)))
        total_loss = target_data.get('total_loss', target_data.get('totalLoss', target_data.get('total_amount', 0)))
        inv_cases = target_data.get('inv_cases', target_data.get('invCases', target_data.get('investment_count', 0)))
        inv_loss = target_data.get('inv_loss', target_data.get('invLoss', target_data.get('investment_amount', 0)))

        payload = {
            "date": str(date_val),
            "total_cases": total_cases,
            "total_loss": total_loss,
            "inv_cases": inv_cases,
            "inv_loss": inv_loss
        }
        
        # 你的專屬 Google Sheet 接收端網址
        google_sheet_api_url = "https://script.google.com/macros/s/AKfycbxrln86Bf0gB0qONPqgpWFPNfWaW9hNJsx5xoK4jICMkuANXzwCQL4TrNECGoOUm0hf/exec"
        
        headers = {"Content-Type": "application/json"}
        post_res = requests.post(google_sheet_api_url, data=json.dumps(payload), headers=headers, timeout=15)
        
        print(f"成功抓取 165 官網最新資料!!")
        print(f"發送數據內容: {payload}")
        print(f"Google Sheet 處理回應: {post_res.text}")
        
    except Exception as e:
        print(f"系統執行期間發生錯誤: {str(e)}")

if __name__ == "__main__":
    json_to_sheet()
