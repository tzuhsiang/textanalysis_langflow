#!/bin/bash

echo "等待 Langflow 服務啟動..."
sleep 30  # 等待服務完全啟動

echo "執行流程導入..."
docker compose run --rm import_flow

echo "獲取流程 ID..."
docker compose run --rm -v $(pwd)/get_flow_id.py:/app/get_flow_id.py analysis_app python /app/get_flow_id.py

echo "完成設定！"
echo "請複製上方輸出的 Emotion 流程 ID，並更新 env/app.env 中的 URL"
