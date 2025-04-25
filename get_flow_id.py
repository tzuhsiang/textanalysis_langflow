#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

URL="http://langflow:7860"

def get_flows():
    """獲取所有 flows 的資訊"""
    try:
        response = requests.get(f"{URL}/api/v1/flows/")
        if response.ok:
            flows = response.json()
            for flow in flows:
                print(f"名稱: {flow.get('name')}")
                print(f"ID: {flow.get('id')}")
                print("---")
            return flows
        else:
            print(f"獲取 flows 失敗: {response.status_code}")
            return []
    except Exception as e:
        print(f"發生錯誤: {str(e)}")
        return []

if __name__ == "__main__":
    flows = get_flows()
    if flows:
        print(f"\n總共找到 {len(flows)} 個 flows")
