# 使用官方 Python 3.10 作為基底映像
FROM python:3.10

# 設定工作目錄
WORKDIR /app

# 接收代理設定的構建參數
ARG http_proxy
ARG https_proxy
ARG HTTP_PROXY
ARG HTTPS_PROXY

# 設定代理環境變數
ENV http_proxy=$http_proxy \
    https_proxy=$https_proxy \
    HTTP_PROXY=$HTTP_PROXY \
    HTTPS_PROXY=$HTTPS_PROXY


# 複製 requirements.txt 並安裝所需套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式到容器內
COPY . .

# 指定開放的 Port
EXPOSE 8501

# 執行 Streamlit 應用
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
