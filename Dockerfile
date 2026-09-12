FROM python:3.12-slim

WORKDIR /app

# 設定時區為台北 (UTC+8) 與禁止輸出 .pyc 快取
ENV TZ=Asia/Taipei \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/app/data

# 設定系統時區與建立資料持久化目錄
RUN apt-get update && apt-get install -y --no-install-recommends tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /app/data

# 安裝依賴
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# 複製程式碼
COPY backend /app/backend
COPY frontend /app/frontend

EXPOSE 8000

# 綁定 0.0.0.0 以允許從容器外部與本機網路存取
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]