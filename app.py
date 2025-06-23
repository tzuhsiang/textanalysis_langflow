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
langflow_api_4 = os.getenv("LANGFLOW_API_4")  # 關鍵字分析
langflow_api_5 = os.getenv("LANGFLOW_API_5")  # 對話修飾


# 使用 CSS 調整頁面寬度和側邊欄樣式

def format_dialogue_refinement(refinement):
    import json
    try:
        if isinstance(refinement, str):
            data = json.loads(refinement)
        else:
            data = refinement
        if not isinstance(data, list):
            return str(refinement)
        role_map = {"agent": "客服", "customer": "民眾"}
        lines = []
        for item in data:
            role = role_map.get(item.get("type", ""), item.get("type", ""))
            time = item.get("starttime", "")
            content = item.get("content", "")
            lines.append(f"[{role}]  {time}\n{content}")
        return "\n".join(lines)
    except Exception:
        return str(refinement)
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

                    # 對話修飾
                    st.info("🔄 進行對話修飾分析...")
                    start_time = time.time()
                    response = requests.post(langflow_api_5, headers=headers, json=data)
                    response.raise_for_status()
                    dialogue_refinement = response.json()['outputs'][0]['outputs'][0]['results']['text'].get("text", "無法獲取對話修飾")
                    st.session_state.dialogue_refinement = dialogue_refinement
                    st.session_state.dialogue_refinement_time = time.time() - start_time
                    st.session_state.dialogue_refinement_type = type(dialogue_refinement).__name__

                    # 對話摘要分析
                    st.info("🔄 進行對話摘要分析...")

                    start_time = time.time()
                    response = requests.post(langflow_api_1, headers=headers, json=data)
                    response.raise_for_status()
                    summary = response.json()['outputs'][0]['outputs'][0]['results']['text'].get("text", "無法獲取對話摘要")
                    st.session_state.summary = summary
                    st.session_state.summary_time = time.time() - start_time
                    st.session_state.summary_type = type(summary).__name__

                    # 意圖分析
                    st.info("🔄 進行意圖分析...")
                    start_time = time.time()
                    response = requests.post(langflow_api_2, headers=headers, json=data)
                    response.raise_for_status()
                    intention = response.json()['outputs'][0]['outputs'][0]['results']['text'].get("text", "無法獲取意圖分析")
                    st.session_state.intention = intention
                    st.session_state.intention_time = time.time() - start_time
                    st.session_state.intention_type = type(intention).__name__

                    # 情緒分析
                    st.info("🔄 進行情緒分析...")
                    start_time = time.time()
                    response = requests.post(langflow_api_3, headers=headers, json=data)
                    response.raise_for_status()
                    emotion = response.json()['outputs'][0]['outputs'][0]['results']['text'].get("text", "無法獲取情緒分析")
                    st.session_state.emotion = emotion
                    st.session_state.emotion_time = time.time() - start_time
                    st.session_state.emotion_type = type(emotion).__name__


                    # 關鍵字分析
                    st.info("🔄 進行關鍵字分析...")
                    start_time = time.time()
                    response = requests.post(langflow_api_4, headers=headers, json=data)
                    response.raise_for_status()
                    keyword = response.json()['outputs'][0]['outputs'][0]['results']['text'].get("text", "無法獲取關鍵字")
                    st.session_state.keyword = keyword
                    st.session_state.keyword_time = time.time() - start_time
                    st.session_state.keyword_type = type(keyword).__name__

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

        # # 顯示原始對話內容
        # with st.expander("查看原始對話", expanded=False):
        #     st.text(latest_text)

        # 顯示所有分析結果
        if "dialogue_refinement" in st.session_state:
            with st.container():
                st.subheader("✏️ 對話修飾")
                st.write(f"分析時間: {st.session_state.dialogue_refinement_time:.2f} 秒, 回傳資料型別: {st.session_state.dialogue_refinement_type}")
                with st.expander("查看修飾後對話", expanded=False):
                    formatted = format_dialogue_refinement(st.session_state.dialogue_refinement)
                    st.text(formatted)

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
                    # 這裡假設情緒分析結果是 JSON 格式的字串
                    # 例如: {"positive": 0.8, "neutral": 0.1, "negative": 0.1}
                    # 將 JSON 字串轉換為 Python 字典
                    # 如果情緒分析結果是字典格式，則直接使用

                    st.success(st.session_state.emotion)

                    if isinstance(st.session_state.emotion, str):
                        emotion_data = json.loads(st.session_state.emotion)
                    else:
                        emotion_data = st.session_state.emotion

                    positive = emotion_data.get("positive", 0)
                    neutral = emotion_data.get("neutral", 0)
                    negative = emotion_data.get("negative", 0)

                    #顯示進度條與百分比
                    # st.progress(positive)
                    # st.success(f"正面情緒比例: {positive*100:.1f}%")
                    # st.progress(neutral)
                    # st.success(f"中性情緒比例: {neutral*100:.1f}%")
                    # st.progress(negative)
                    # st.success(f"負面情緒比例: {negative*100:.1f}%")
  
                    # 合併成一條彩色進度條
                    bar_html = f"""
                    <div style='display: flex; height: 32px; width: 100%; border-radius: 8px; overflow: hidden; border: 1px solid #DDD; margin-bottom: 8px;'>
                    <div style='width: {positive*100}%; background: #4CAF50;'></div>
                    <div style='width: {neutral*100}%; background: #2196F3;'></div>
                    <div style='width: {negative*100}%; background: #F44336;'></div>
                    </div>
                    <div>
                    <span style='color:#66b3ff;'>正面 {positive*100:.1f}%</span>　
                    <span style='color:#ffcc99;'>中性 {neutral*100:.1f}%</span>　
                    <span style='color:#ff9999;'>負面 {negative*100:.1f}%</span>
                    </div>
                    """
                    st.markdown(bar_html, unsafe_allow_html=True)



                except Exception as e:
                    # 如果解析失敗，顯示原始文字
                    st.success(st.session_state.emotion)
        

        if "keyword" in st.session_state:
            with st.container():
                st.subheader("🔍 關鍵字分析")
                st.write(f"分析時間: {st.session_state.keyword_time:.2f} 秒, 回傳資料型別: {st.session_state.keyword_type}")
                st.warning(st.session_state.keyword)

# 系統設定頁面
elif st.session_state.current_page == "系統設定":
    st.header("⚙️ 系統設定")
    
    # 顯示當前設定
    st.subheader("🔗 API 端點設定")
    st.write("在此設定各個分析功能的 API 端點")

    # 建立設定表單
    with st.form("api_settings"):
        # Langflow 基礎 URL
        base_url = st.text_input(
            "Langflow 基礎 URL",
            value=os.getenv("LANGFLOW_URL", "http://langflow:7860"),
            help="Langflow 服務的基礎 URL"
        )
        
        # 對話摘要 API
        api_1 = st.text_input(
            "對話摘要 API",
            value=os.getenv("LANGFLOW_API_1", ""),
            help="用於對話摘要分析的 API 端點"
        )
        
        # 意圖分析 API
        api_2 = st.text_input(
            "意圖分析 API",
            value=os.getenv("LANGFLOW_API_2", ""),
            help="用於意圖分析的 API 端點"
        )
        
        # 情緒分析 API
        api_3 = st.text_input(
            "情緒分析 API",
            value=os.getenv("LANGFLOW_API_3", ""),
            help="用於情緒分析的 API 端點"
        )
        # 關鍵字分析 API
        api_4 = st.text_input(
            "關鍵字分析 API",
            value=os.getenv("LANGFLOW_API_4", ""),
            help="用於關鍵字分析的 API 端點"
        )

         # 對話修飾 API
        api_5 = st.text_input(
            "對話修飾分析 API",
            value=os.getenv("LANGFLOW_API_5", ""),
            help="用於對話修飾分析的 API 端點"
        )


        # 儲存按鈕
        if st.form_submit_button("💾 儲存設定"):
            try:

                # 準備新的環境變數內容
                env_content = f"""# langflow 網址
                LANGFLOW_URL="{base_url}"

                #對話摘要
                LANGFLOW_API_1="{api_1}"

                #意圖分析
                LANGFLOW_API_2="{api_2}"

                #情緒分析
                LANGFLOW_API_3="{api_3}"
                """
                # 寫入檔案
                with open("/app/env/app.env", "w", encoding="utf-8") as f:
                    f.write(env_content)
                
                # 重新載入環境變數
                load_dotenv("/app/env/app.env", override=True)
                
                st.success("✅ 設定已成功儲存！")
                st.info("🔄 請重新整理頁面以套用新設定")
            except Exception as e:
                st.error(f"❌ 儲存設定時發生錯誤: {str(e)}")

    # 顯示設定說明
    with st.expander("ℹ️ 設定說明"):
        st.markdown("""
        ### 設定項目說明
        
        1. **Langflow 基礎 URL**
           - Langflow 服務的基本網址
           - 預設值: `http://langflow:7860`
        
        2. **對話摘要 API**
           - 用於分析並摘要對話內容的 API 端點
           - 格式: `[基礎 URL]/api/v1/run/[Flow ID]?stream=false`
        
        3. **意圖分析 API**
           - 用於分析對話意圖的 API 端點
           - 格式: `[基礎 URL]/api/v1/run/[Flow ID]?stream=false`
        
        4. **情緒分析 API**
           - 用於分析對話情緒的 API 端點
           - 格式: `[基礎 URL]/api/v1/run/[Flow ID]?stream=false`
        
        ### 注意事項
        - 修改設定後需要重新整理頁面才會生效
        - 請確保輸入的 API 端點格式正確
        - Flow ID 可以從 Langflow 介面中獲取
        """)
