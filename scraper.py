import requests
import json

def json_to_sheet():
    url = "https://165dashboard.tw/api/v1/home/dashboard-data"
    
    # 👑 核心修復：加入超級偽裝頭（Headers），假裝自己是 Windows 上的 Chrome 瀏覽器
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://165dashboard.tw/fraud-method",
        "Origin": "https://165dashboard.tw"
    }
    
    try:
        # 💡 將偽裝頭 headers 加進請求中
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        res_data = response.json()
        
        target_data = res_data.get('data', res_data) if isinstance(res_data, dict) else res_data
        
        if not target_data:
            print("錯誤：無法解析 165 官方數據結構")
            return

        payload_list = []
        
        # 1. 抓取當天最新摘要
        date_val = target_data.get('date')
        if date_val:
            payload_list.append({
                "date": str(date_val),
                "total_cases": target_data.get('total_cases', 0),
                "total_loss": target_data.get('total_loss', 0),
                "inv_cases": target_data.get('inv_cases', 0),
                "inv_loss": target_data.get('inv_loss', 0)
            })
            
        # 2. 抓取趨勢歷史列表
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

        google_sheet_api_url = "https://script.google.com/macros/s/AKfycbxrln86Bf0gB0qONPqgpWFPNfWaW9hNJsx5xoK4jICMkuANXzwCQL4TrNECGoOUm0hf/exec"
        sheet_headers = {"Content-Type": "application/json"}
        
        if not payload_list:
            print("未偵測到任何有效數據")
            return
            
        print(f"成功突破防護！準備發送 {len(payload_list)} 筆資料至 Google Sheet...")
        
        for payload in payload_list:
            post_res = requests.post(google_sheet_api_url, data=json.dumps(payload), headers=sheet_headers, timeout=15)
            print(f"日期 {payload['date']} 發送結果 -> {post_res.text}")
        
    except Exception as e:
        print(f"系統執行期間發生錯誤: {str(e)}")

if __name__ == "__main__":
    json_to_sheet()
