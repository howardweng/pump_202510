# 幫浦測試平台
## Pump Testing Platform

---

## 📋 專案概述

本專案是一個幫浦測試平台系統，包含前端、後端、基礎設施和模擬器等組件。

---

## 🏗️ 專案結構

```
pump_202510/
├── docker-compose.yml          # 統一 Docker Compose 配置
├── .env.example                # 環境變數範例
├── README.md                   # 本文件
│
├── infrastructure/             # 基礎設施配置
│   ├── mqtt/                   # MQTT Broker 配置
│   └── postgres/               # PostgreSQL 配置
│
├── pump_backend/               # 後端服務 (TODO)
│   └── ...
│
├── pump_app/                   # 前端應用
│   └── ...
│
├── simulator/                  # MODBUS 模擬器服務
│   ├── devices/                # 設備模擬器實作
│   ├── config/                 # 配置文件
│   └── ...
│
├── serial-bridge/              # 串口橋接器 (RTU 到 TCP)
│   └── ...
│
├── admin-api/                  # 模擬器管理 API (FastAPI)
│   ├── models/                 # 數據模型
│   ├── routers/                # API 路由
│   └── ...
│
└── admin-ui/                   # 模擬器管理 UI (React)
    ├── src/
    │   ├── pages/              # 頁面組件
    │   └── api/                # API 客戶端
    └── ...
│
└── docs/                       # 文檔
    ├── PRD.md                  # 產品需求文檔
    ├── BACKEND_ARCHITECTURE_PLAN.md
    ├── MODBUS_all_devices.md
    └── ...
```

---

## 🚀 快速開始

### 1. 準備環境

```bash
# 複製環境變數文件
cp env.example .env

# 編輯環境變數（可選，預設值可用於開發環境）
nano .env
```

### 2. 啟動服務

```bash
# 啟動所有服務（基礎設施 + 模擬器）
docker compose up -d

# 查看服務狀態
docker compose ps

# 查看日誌
docker compose logs -f
```

### 3. 啟動特定服務

```bash
# 只啟動基礎設施
docker compose up -d mqtt-broker postgres

# 啟動模擬器系統
docker compose up -d modbus-simulator simulator-admin-api simulator-admin-ui

# 啟動包含 pgAdmin（資料庫管理工具）
docker compose --profile tools up -d
```

### 4. 停止服務

```bash
# 停止所有服務
docker compose down

# 停止並刪除數據卷（⚠️ 警告：會刪除所有數據）
docker compose down -v
```

---

## 📦 服務說明

### 基礎設施服務

| 服務 | 端口 | 說明 |
|------|------|------|
| **MQTT Broker** | 1883 (TCP)<br>8083 (WebSocket) | 訊息匯流排，用於前後端通訊 |
| **PostgreSQL** | 5432 | 資料庫，儲存測試數據和歷史記錄 |
| **pgAdmin** | 5050 | 資料庫管理工具（可選） |

### 模擬器服務 ✅

| 服務 | 端口 | 說明 |
|------|------|------|
| **MODBUS 模擬器** | 5020-5027 | 8 台 MODBUS 設備模擬器（流量計、電表、壓力計、繼電器 IO） |
| **Admin API** | 8001 | FastAPI 管理介面，設備和場景管理 |
| **Admin UI** | 3001 | React Web 管理介面 |

**功能**:
- ✅ 8 台設備模擬器（完全符合 MODBUS_all_devices.md 規格）
- ✅ 設備狀態總覽和配置管理
- ✅ 場景管理（創建、更新、刪除測試場景）
- ✅ 串口橋接器（RTU 到 TCP）

### 後端服務 (TODO)

- Python 後端服務
- MODBUS 設備驅動
- 安全監控服務

### 前端服務 (TODO)

- React 前端應用
- 即時數據顯示
- 測試控制介面

---

## 🔧 配置說明

### 環境變數

主要環境變數定義在 `.env` 文件中：

- **PostgreSQL**: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- **pgAdmin**: `PGADMIN_EMAIL`, `PGADMIN_PASSWORD`
- **MQTT**: 預設使用 localhost，無需配置

### 網路配置

所有服務都在 `pump-network` 網路中，可以通過服務名稱互相訪問：

- MQTT Broker: `mqtt-broker`
- PostgreSQL: `postgres`
- pgAdmin: `pgadmin`
- MODBUS 模擬器: `modbus-simulator`
- Admin API: `simulator-admin-api`

---

## 🔗 連接資訊

### MQTT Broker

**後端 Python 連接**:
```python
broker = "mqtt-broker"  # 從容器內
# 或
broker = "localhost"    # 從主機
port = 1883
```

**前端 React 連接**:
```javascript
const wsUrl = "ws://localhost:8083";
```

### PostgreSQL

**連接字串**:
```
Host: postgres (從容器內) 或 localhost (從主機)
Port: 5432
Database: pump_testing (預設)
User: pump_user (預設)
Password: (從 .env 文件讀取)
```

**Python 連接範例**:
```python
import asyncpg

conn = await asyncpg.connect(
    host='postgres',  # 從容器內使用服務名稱
    port=5432,
    user='pump_user',
    password='pump_password_change_me',
    database='pump_testing'
)
```

### MODBUS 模擬器

**Modbus TCP 連接**:
```
Host: localhost (從主機) 或 modbus-simulator (從容器內)
Port: 5020-5027 (每台設備獨立端口)
```

**設備端口映射**:
- 5020: 流量計
- 5021: DC 電表
- 5022: AC110V 電表
- 5023: AC220V 電表
- 5024: AC220V 3P 電表
- 5025: 壓力計 (正壓)
- 5026: 壓力計 (真空)
- 5027: 繼電器 IO 模組

### Admin API

**API 端點**:
- Base URL: http://localhost:8001
- API 文檔: http://localhost:8001/docs
- 健康檢查: http://localhost:8001/health

### Admin UI

**Web 介面**:
- URL: http://localhost:3001
- 功能: 設備狀態總覽、設備配置、場景管理

---

## 📚 文檔

- [產品需求文檔](docs/PRD.md)
- [後端架構設計](docs/BACKEND_ARCHITECTURE_PLAN.md)
- [MODBUS 設備規格](docs/MODBUS_all_devices.md)
- [模擬器架構設計](docs/SIMULATOR_ARCHITECTURE.md)
- [基礎設施文檔](infrastructure/README.md)

---

## 🛠️ 開發指南

### 添加新服務

1. 在 `docker-compose.yml` 中添加服務定義
2. 在 `.env.example` 中添加相關環境變數
3. 更新本 README 文件

### 測試服務

```bash
# 測試 MQTT
docker compose exec mqtt-broker mosquitto_sub -h localhost -t '$SYS/broker/uptime' -C 1

# 測試 PostgreSQL
docker compose exec postgres psql -U pump_user -d pump_testing -c "SELECT version();"
```

---

## ⚠️ 注意事項

1. **數據持久化**: 所有數據都保存在 Docker volumes 中
2. **端口衝突**: 確保以下端口未被佔用：
   - 基礎設施: 1883, 8083, 5432, 5050
   - 模擬器: 5020-5027, 8001, 3001
3. **環境變數**: 生產環境請修改 `.env` 中的預設密碼
4. **網路隔離**: 所有服務都在 `pump-network` 網路中
5. **模擬器使用**: 模擬器用於開發和測試，可通過 Admin UI 管理設備配置

---

## 📝 更新日誌

- **2025.11.15**: 
  - ✅ 完成 MODBUS 模擬器系統實作
    - MODBUS 模擬器服務（8台設備）
    - 串口橋接器（RTU 到 TCP）
    - Admin API（FastAPI）
    - Admin UI（React）
  - ✅ 創建統一 Docker Compose 配置，整合基礎設施服務

---

**最後更新**: 2025.11.15

