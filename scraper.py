import requests
import json

def find_the_list(obj):
    """【神級萬能鑰匙】全自動深度搜尋物件裡面的陣列資料"""
    if isinstance(obj, list) and len(obj) > 0:
        return obj
    if isinstance(obj, dict):
        # 優先尋找政府開放平台常見的幾種包裝欄位
        for key in ['records', 'result', 'data', 'recordsGrid']:
            if key in obj:
                res = find_the_list(obj[key])
                if res: return res
        # 如果還是沒找到，就地毯式搜索任何含有陣列的欄位
        for key, val in obj.items():
            if isinstance(val, list) and len(val) > 0:
                # 排除可能誤判的無用短列表
                if isinstance(val[0], (dict, list)):
                    return val
    return None

def json_to_sheet():
    # 走 data.gov.tw 的 165 開放資料接口
    url = "https://data.gov.tw/api/v2/rest/dataset/167232"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        print("正在透過政府開放資料通道讀取 165 數據...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        res_data = response.json()
        
        # 👑 呼叫萬能搜尋器，強制把深藏在洋蔥核心的歷史資料陣列挖出來
        data_list = find_the_list(res_data)

        if not data_list:
            print("【終極防護啟動】無法解析到列表，印出原始包裝格式供 debug:")
            print(str(res_data)[:500]) # 印出前500個字看格式
            return

        payload_list = []
        print(f"【成功破門】全自動定位出資料庫！共包含 {len(data_list)} 筆原始紀錄。開始對齊中文欄位...")

        # 掃描資料，進行欄位智慧配對
        for item in data_list:
            if not isinstance(item, dict):
                continue
                
            # 1. 智慧尋找日期
            date_val = None
            for d_key in ['統計日期', '統計日', 'date', 'Date', '統計日前一天']:
                if d_key in item and item[d_key]:
                    date_val = str(item[d_key]).replace('/', '-').strip()
                    break
            
            if not date_val:
                continue # 沒日期的垃圾資料就跳過
                
            # 2. 智慧數字清理器（過濾掉中文文字、千分號，強制安全轉數字）
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
            print("錯誤：未能成功從物件中辨識出任何有效的 165 資料欄位。")
            print(f"第一筆範例樣本為: {data_list[0]}")
            return
            
        # 限制最多發送最近 5 筆，免得洗板
        print(f"欄位智慧對齊成功！準備將最近 {min(len(payload_list), 5)} 筆歷史資料外送到 Google Sheet...")
        
        for payload in payload_list[:5]:
            post_res = requests.post(google_sheet_api_url, data=json.dumps(payload), headers=sheet_headers, timeout=15)
            print(f"日期 {payload['date']} -> 傳送結果: {post_res.text}")
            
    except Exception as e:
        print(f"系統執行期間發生錯誤: {str(e)}")

if __name__ == "__main__":
    json_to_sheet()
