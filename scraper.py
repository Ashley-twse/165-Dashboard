import requests
import json

def json_to_sheet():
    # 使用政府開放平台 167232 資料集的標準 JSON 直連網址
    url = "https://data.gov.tw/api/v2/rest/dataset/167232"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        print("正在透過政府開放資料通道讀取 165 數據...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        res_data = response.json()
        
        # 👑 核心破案：精準剝開政府資料的外殼
        # 政府 API 格式通常是 {"success": true, "result": {"records": [...]}}
        data_list = []
        if isinstance(res_data, dict):
            if 'result' in res_data and isinstance(res_data['result'], dict):
                data_list = res_data['result'].get('records', [])
            elif 'records' in res_data:
                data_list = res_data['records']
            else:
                data_list = res_data.get('data', [])
        elif isinstance(res_data, list):
            data_list = res_data

        if not data_list:
            # 預備方案：如果外殼不對，直接把整個物件當成單筆處理，或者尋找任何列表
            if isinstance(res_data, dict):
                for key, val in res_data.items():
                    if isinstance(val, list):
                        data_list = val
                        break
        
        if not data_list:
            print("錯誤：無法拆解政府開放平臺的資料層級")
            return

        payload_list = []
        print(f"成功剝離外殼！偵測到資料庫包含 {len(data_list)} 筆原始紀錄。正在對齊欄位...")

        # 掃描前 5 筆資料，進行中英文欄位智慧配對
        for item in data_list[:5]:
            # 1. 尋找日期 (相容 統計日期, 統計日, date, Date)
            date_val = None
            for d_key in ['統計日期', '統計日', 'date', 'Date', '統計日前一天']:
                if d_key in item and item[d_key]:
                    date_val = str(item[d_key]).replace('/', '-').strip()
                    break
            
            if not date_val:
                continue # 沒日期就跳過
                
            # 2. 尋找各項指標金額與件數 (自動過濾掉中文字、千分號，強制轉數字)
            def clean_num(val):
                if val is None: return 0
                cleaned = ''.join(c for c in str(val) if c.isdigit() or c == '.')
                return int(float(cleaned)) if cleaned else 0

            total_cases = clean_num(item.get('總受理件數', item.get('受理件數', item.get('total_cases', item.get('totalCases', 0)))))
            total_loss = clean_num(item.get('總財損金額', item.get('財損金額', item.get('total_loss', item.get('totalLoss', 0)))))
            inv_cases = clean_num(item.get('假投資件數', item.get('假投資件數(件)', item.get('inv_cases', item.get('invCases', 0)))))
            inv_loss = clean_num(item.get('假投資財損', item.get('假投資總財損金額', item.get('inv_loss', item.get('invLoss', 0)))))

            payload_list.append({
                "date": date_val,
                "total_cases": total_cases,
                "total_loss": total_loss,
                "inv_cases": inv_cases,
                "inv_loss": inv_loss
            })

        # 妳的專屬 Google Sheet 接收端網址
        google_sheet_api_url = "https://script.google.com/macros/s/AKfycbxrln86Bf0gB0qONPqgpWFPNfWaW9hNJsx5xoK4jICMkuANXzwCQL4TrNECGoOUm0hf/exec"
        sheet_headers = {"Content-Type": "application/json"}
        
        if not payload_list:
            print("錯誤：未能成功辨識政府資料內的中文欄位名稱。")
            # 終極相容：如果欄位真的完全找不到，列印出政府吐出來的第一筆資料結構，方便肉眼看
            print(f"政府資料的第一筆結構為: {data_list[0]}")
            return
            
        print(f"欄位對齊完畢！準備傳送 {len(payload_list)} 筆歷史資料至 Google Sheet...")
        
        for payload in payload_list:
            post_res = requests.post(google_sheet_api_url, data=json.dumps(payload), headers=sheet_headers, timeout=15)
            print(f"日期 {payload['date']} -> 傳送結果: {post_res.text}")
            
    except Exception as e:
        print(f"系統執行期間發生錯誤: {str(e)}")

if __name__ == "__main__":
    json_to_sheet()
