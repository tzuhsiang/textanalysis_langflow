# 使用官方 Python 3.10 作為基底映像
FROM python:3.10

# 設定工作目錄
WORKDIR /app

# 設定代理伺服器
ENV http_proxy=http://10.160.3.88:8080
ENV https_proxy=http://10.160.3.88:8080


# 複製 requirements.txt 並安裝所需套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式到容器內
COPY . .

# 指定開放的 Port
EXPOSE 8501

# 執行 Streamlit 應用
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
