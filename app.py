import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os

# 讀取 .env 檔案中的環境變數
load_dotenv()

# 從環境變數讀取 Langchain API URL
langchain_api_url = os.getenv("LANGCHAIN_API_URL")

# 設定頁面標題
st.set_page_config(page_title="對話輸入介面", layout="wide")

# 使用 CSS 調整頁面寬度
st.markdown("""
    <style>
        /* 調整頁面整體內容的最大寬度 */
        .block-container {
            max-width: 90% !important;  /* 設定寬度為 90% */
            padding-left: 5% !important;
            padding-right: 5% !important;
        }
    </style>
""", unsafe_allow_html=True)

# 初始化對話歷史，只存一筆
if "latest_message" not in st.session_state:
    st.session_state.latest_message = {"role": "user", "content": ""}

# 創建左右兩個欄位
col1, col2 = st.columns([1, 2])


# **左側：對話輸入區**
with col1:

    st.header("💬 輸入對話")
    user_input = st.text_area("請輸入你的訊息：", key="user_input", height=150)

    if st.button("送出"):
        if user_input.strip():  # 避免空白輸入
             # **儲存最新的訊息，只保留一筆**
            st.session_state.latest_input = user_input  # 儲存輸入內容
            
            # 呼叫 Langchain API 進行對話摘要分析
            headers = {"Content-Type": "application/json"}
            data = {
                "input_value": user_input
            }

            # 發送 POST 請求給 Langflow API
            response = requests.post(langchain_api_url, headers=headers, json=data)
            response.raise_for_status()  # 若發生錯誤會觸發例外

            # 解析回應
            summary=response.json()['outputs'][0]['outputs'][0]['results']['message'].get("text", "無法獲取對話")
            st.session_state.summary = summary

            # try:
            #     # 發送 POST 請求給 Langchain API
            #     response = requests.post(langchain_api_url, headers=headers, json=data)
            #     response.raise_for_status()  # 若發生錯誤會觸發例外

            #     # 解析回應
            #     summary=response.json()['outputs'][0]['outputs'][0]['results']['message'].get("text", "無法獲取對話")
            #     st.session_state.summary = summary

            # except requests.exceptions.RequestException as e:
            #     st.error(f"呼叫 Langchain API 時發生錯誤: {e}")


            # **清空輸入框並更新畫面**
            st.rerun()  

# **右側：顯示對話分析紀錄**
with col2:

    st.header("📜 對話分析")
    
    # 讀取最新輸入的字數
    latest_text = st.session_state.get("latest_input", "")
    word_count = len(latest_text.strip())  # 計算字數（去掉前後空白）

    # st.write(f"輸入內容:{latest_text}")
    st.write(f"輸入字數 **{word_count}** 個字")

    if "summary" in st.session_state:
        st.write(f"**對話摘要**: {st.session_state.summary}")
