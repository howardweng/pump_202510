# MODBUS 模擬器 Admin API

FastAPI 管理介面，用於管理 MODBUS 設備模擬器。

## 功能

- ✅ 設備管理 API（獲取、更新設備狀態和配置）
- ✅ 場景管理 API（創建、更新、刪除測試場景）
- ✅ PostgreSQL 資料庫整合
- ✅ CORS 支援（用於前端連接）

## API 端點

### 設備管理

- `GET /api/devices` - 獲取所有設備狀態
- `GET /api/devices/{device_id}` - 獲取單一設備狀態
- `PUT /api/devices/{device_id}` - 更新設備模擬數據

### 場景管理

- `GET /api/scenarios` - 獲取所有場景
- `GET /api/scenarios/{scenario_id}` - 獲取單一場景
- `POST /api/scenarios` - 創建場景
- `PUT /api/scenarios/{scenario_id}` - 更新場景
- `DELETE /api/scenarios/{scenario_id}` - 刪除場景

### 其他

- `GET /` - API 資訊
- `GET /health` - 健康檢查
- `GET /docs` - Swagger API 文檔

## 使用方式

### 本地開發

```bash
# 安裝依賴
pip install -r requirements.txt

# 運行 API
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Docker Compose

```bash
# 從專案根目錄啟動
cd /home/datavan/pump_202510
docker compose up -d simulator-admin-api
```

## 環境變數

- `LOG_LEVEL` - 日誌級別（預設: INFO）
- `MQTT_BROKER` - MQTT Broker 主機（預設: mqtt-broker）
- `MQTT_PORT` - MQTT 端口（預設: 1883）
- `POSTGRES_HOST` - PostgreSQL 主機（預設: postgres）
- `POSTGRES_PORT` - PostgreSQL 端口（預設: 5432）
- `POSTGRES_DB` - 資料庫名稱（預設: pump_testing）
- `POSTGRES_USER` - 資料庫用戶（預設: pump_user）
- `POSTGRES_PASSWORD` - 資料庫密碼

## 訪問

- API: http://localhost:8001
- API 文檔: http://localhost:8001/docs
- 健康檢查: http://localhost:8001/health

