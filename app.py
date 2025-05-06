import streamlit as st
import requests
import json
import glob
from dotenv import load_dotenv
import os
import time

# 設定頁面標題（必須是第一個 Streamlit 命令）
st.set_page_config(page_title="對話輸入介面", layout="wide")

# 讀取 env/app.env 檔案中的環境變數
load_dotenv("/app/env/app.env")

# 從環境變數讀取所有 API URL
langflow_api_1 = os.getenv("LANGFLOW_API_1")  # 對話摘要
langflow_api_2 = os.getenv("LANGFLOW_API_2")  # 意圖分析
langflow_api_3 = os.getenv("LANGFLOW_API_3")  # 情緒分析

# 使用 CSS 調整頁面寬度和側邊欄樣式
st.markdown("""
    <style>
        /* 調整頁面整體內容的最大寬度 */
        .block-container {
            max-width: 95% !important;
            padding-left: 2% !important;
            padding-right: 2% !important;
        }
        /* 調整側邊欄寬度和間距 */
        [data-testid="stSidebar"][aria-expanded="true"] {
            min-width: 200px;
            max-width: 200px;
            padding-right: 0 !important;
            margin-right: -1rem;
        }
        /* 主要內容區域的間距調整 */
        .main .block-container {
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# 初始化 session state
if "latest_message" not in st.session_state:
    st.session_state.latest_message = {"role": "user", "content": ""}
if "current_page" not in st.session_state:
    st.session_state.current_page = "對話分析"

# 側邊選單
with st.sidebar:
    st.title("功能選單")
    selected_page = st.radio(
        "選擇功能：",
        ["對話分析", "系統設定"]
    )
    st.session_state.current_page = selected_page

# 對話分析頁面
if st.session_state.current_page == "對話分析":
    # 創建左右兩個欄位
    col1, col2 = st.columns([1, 2])

    # **左側：對話輸入區**
    with col1:
        st.header("💬 輸入對話")
        
        # 讀取對話檔案列表
        dialogue_files = glob.glob("/app/dialogue/*.json")
        dialogue_names = [os.path.basename(f) for f in dialogue_files]
        st.write(f"📁 已找到 **{len(dialogue_names)}** 個對話檔案")
    
        # 添加下拉式選單
        selected_dialogue = st.selectbox(
            "選擇預設對話：",
            [""] + dialogue_names,
            format_func=lambda x: "請選擇對話檔案..." if x == "" else x
        )
        
        # 讀取並格式化內容
        initial_text = ""
        if selected_dialogue:
            st.info(f"🔍 當前載入的對話: {selected_dialogue}")
            try:
                with open(f"/app/dialogue/{selected_dialogue}", 'r', encoding='utf-8') as f:
                    dialogue_content = json.load(f)
                    # 格式化對話內容
                    if isinstance(dialogue_content, list):
                        # 使用第一個元素的內容，並整理對話格式
                        raw_dialogue = dialogue_content[0].split(',')
                        formatted_lines = []
                        for line in raw_dialogue:
                            if "agent:" in line:
                                formatted_lines.append("客服: " + line.replace("agent:", "").strip())
                            elif "customer:" in line:
                                formatted_lines.append("客戶: " + line.replace("customer:", "").strip())
                        initial_text = "\n".join(formatted_lines)
            except Exception as e:
                st.error(f"讀取對話檔案時發生錯誤: {str(e)}")
                initial_text = ""
        
        # 顯示文本輸入區域
        user_input = st.text_area(
            "請輸入或編輯對話內容：",
            value=initial_text,
            height=300,
            key="dialogue_input"
        )

        if st.button("送出"):
            if user_input.strip():  # 避免空白輸入
                st.session_state.latest_input = user_input  # 儲存輸入內容
                
                # 準備 API 請求
                headers = {"Content-Type": "application/json"}
                data = {
                    "input_value": user_input
                }

                # 進行所有分析
                try:
                    # 對話摘要分析
                    st.info("🔄 進行對話摘要分析...")

                    start_time = time.time()
                    response1 = requests.post(langflow_api_1, headers=headers, json=data)
                    response1.raise_for_status()
                    summary = response1.json()['outputs'][0]['outputs'][0]['results']['text'].get("text", "無法獲取對話摘要")
                    st.session_state.summary = summary
                    st.session_state.summary_time = time.time() - start_time
                    st.session_state.summary_type = type(summary).__name__

                    # 意圖分析
                    st.info("🔄 進行意圖分析...")
                    start_time = time.time()
                    response2 = requests.post(langflow_api_2, headers=headers, json=data)
                    response2.raise_for_status()
                    intention = response2.json()['outputs'][0]['outputs'][0]['results']['text'].get("text", "無法獲取意圖分析")
                    st.session_state.intention = intention
                    st.session_state.intention_time = time.time() - start_time
                    st.session_state.intention_type = type(intention).__name__

                    # 情緒分析
                    st.info("🔄 進行情緒分析...")
                    start_time = time.time()
                    response3 = requests.post(langflow_api_3, headers=headers, json=data)
                    response3.raise_for_status()
                    emotion = response3.json()['outputs'][0]['outputs'][0]['results']['text'].get("text", "無法獲取情緒分析")
                    st.session_state.emotion = emotion
                    st.session_state.emotion_time = time.time() - start_time
                    st.session_state.emotion_type = type(emotion).__name__
                    
                    st.success("✅ 分析完成！")
                    st.rerun()

                except requests.exceptions.RequestException as e:
                    st.error(f"API 呼叫錯誤: {str(e)}")
                except Exception as e:
                    st.error(f"發生未預期的錯誤: {str(e)}")

    # **右側：顯示對話分析紀錄**
    with col2:
        st.header("📊 分析結果")
        
        # 讀取最新輸入的字數
        latest_text = st.session_state.get("latest_input", "")
        word_count = len(latest_text.strip())
        st.write(f"輸入字數 **{word_count}** 個字")

        # 顯示原始對話內容
        with st.expander("查看原始對話", expanded=False):
            st.text(latest_text)

        # 顯示所有分析結果
        if "summary" in st.session_state:
            with st.container():
                st.subheader("📝 對話摘要")
                st.write(f"分析時間: {st.session_state.summary_time:.2f} 秒, 回傳資料型別: {st.session_state.summary_type}")
                st.info(st.session_state.summary)

        if "intention" in st.session_state:
            with st.container():
                st.subheader("🎯 意圖分析")
                st.write(f"分析時間: {st.session_state.intention_time:.2f} 秒, 回傳資料型別: {st.session_state.intention_type}")
                st.warning(st.session_state.intention)

        if "emotion" in st.session_state:
            with st.container():
                st.subheader("😊 情緒分析")
                st.write(f"分析時間: {st.session_state.emotion_time:.2f} 秒, 回傳資料型別: {st.session_state.emotion_type}")
                try:
                    # 解析情緒分析結果中的數值
                    emotion_value = float(st.session_state.emotion)
                    emotion_percent = emotion_value * 100
                    
                    # 顯示進度條和百分比
                    st.progress(emotion_value)
                    st.success(f"負面情緒比例: {emotion_percent:.1f}%")
                except Exception as e:
                    # 如果解析失敗，顯示原始文字
                    st.success(st.session_state.emotion)

# 系統設定頁面
elif st.session_state.current_page == "系統設定":
    st.header("⚙️ 系統設定")
    st.info("此頁面用於設定系統參數，目前尚在開發中...")
