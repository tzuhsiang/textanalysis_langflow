#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import os
import time


# URL="http://langflow:7860"
URL="http://localhost:7860"

def wait_for_langflow():
    max_retries = 30
    retry_interval = 10
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{URL}/health")
            if response.ok:
                print("Langflow 服務已就緒")
                return True
        except requests.exceptions.RequestException:
            print(f"等待 Langflow 服務... ({i+1}/{max_retries})")
            time.sleep(retry_interval)
    
    print("無法連接到 Langflow 服務")
    return False

# 等待 Langflow 服務準備就緒
if not wait_for_langflow():
    exit(1)

def get_existing_flows():
    """獲取現有的 flows 列表"""
    try:
        response = requests.get(f"{URL}/api/v1/flows/")
        if response.ok:
            flows = response.json()
            return {flow.get('name'): flow.get('id') for flow in flows}
        return {}
    except Exception as e:
        print(f"獲取現有 flows 時發生錯誤: {str(e)}")
        return {}

# 獲取現有的 flows
existing_flows = get_existing_flows()
print(f"發現 {len(existing_flows)} 個現有的 flows")

# 讀取 flows 目錄的 JSON 檔案
flows_dir = "flows"
json_files = [f for f in os.listdir(flows_dir) if f.endswith(".json")]

for json_file in json_files:
    try:
        with open(os.path.join(flows_dir, json_file), "r", encoding="utf-8") as f:
            flow_data = json.load(f)
            flow_name = flow_data.get('name', '')
            
            # 檢查是否已存在同名 flow
            if flow_name in existing_flows:
                print(f"跳過已存在的 flow: {flow_name}")
                continue
                
            # 移除 user_id 和 folder_id
            if "user_id" in flow_data:
                del flow_data["user_id"]
            if "folder_id" in flow_data:
                del flow_data["folder_id"]

        # 發送請求並指定正確的 Content-Type
        response = requests.post(
            f"{URL}/api/v1/flows/",
            json=flow_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.ok:
            print(f"Flow {json_file} 匯入成功")
        else:
            print(f"匯入失敗: {json_file}")
            print(f"狀態碼: {response.status_code}")
            print(f"錯誤訊息: {response.text}")
            
    except Exception as e:
        print(f"處理 {json_file} 時發生錯誤: {str(e)}")
