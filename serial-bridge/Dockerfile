FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴（包括 socat 用於創建虛擬串口）
RUN apt-get update && apt-get install -y \
    gcc \
    socat \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式代碼
COPY . .

# 需要特權模式來創建虛擬串口
# 在 docker-compose.yml 中設置 privileged: true

# 啟動命令
CMD ["python", "bridge.py"]

