# 🛠️ 模擬器 Admin 頁面本地開發指南

## 📋 推薦方案：混合模式開發

**為什麼選擇混合模式？**
- ✅ **快速迭代**：本地開發支持熱重載，修改代碼立即生效
- ✅ **調試方便**：可以直接使用 IDE 調試器、斷點
- ✅ **資源節省**：只運行必要的基礎設施服務
- ✅ **環境一致**：基礎設施（MQTT、PostgreSQL）與生產環境一致

## 🏗️ 架構說明

```
┌─────────────────────────────────────────┐
│  本地開發（熱重載）                        │
├─────────────────────────────────────────┤
│  Admin UI (React)    →  http://localhost:3000 │
│  Admin API (FastAPI) →  http://localhost:8001 │
└─────────────────────────────────────────┘
              │              │
              ▼              ▼
┌─────────────────────────────────────────┐
│  Docker 容器（基礎設施）                   │
├─────────────────────────────────────────┤
│  MQTT Broker        →  localhost:1883   │
│  PostgreSQL         →  localhost:5432   │
│  Modbus Simulator   →  localhost:5020-5027 │
└─────────────────────────────────────────┘
```

## 🚀 快速開始

### 方式 1: 一鍵啟動（推薦）⚡

```bash
# 從專案根目錄運行
cd /home/datavan/pump_202510
./start-dev.sh
```

這個腳本會自動：
- ✅ 啟動 Docker 基礎設施（MQTT、PostgreSQL、Modbus Simulator）
- ✅ 啟動 Admin API（後台運行）
- ✅ 啟動 Admin UI（後台運行）
- ✅ 自動創建 `.env.local` 配置文件

**停止服務**:
```bash
./stop-dev.sh
```

---

### 方式 2: 手動啟動（逐步）

#### 1. 啟動基礎設施（Docker）

```bash
# 從專案根目錄啟動基礎設施服務
cd /home/datavan/pump_202510

# 啟動 MQTT、PostgreSQL、Modbus Simulator
docker compose up -d mqtt-broker postgres modbus-simulator

# 檢查服務狀態
docker compose ps
```

#### 2. 啟動 Admin API（本地開發）

```bash
cd admin-api

# 方式 1: 使用開發腳本（推薦）
chmod +x dev.sh
./dev.sh

# 方式 2: 手動啟動
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export $(cat .env.local | grep -v '^#' | xargs)
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

**訪問地址**:
- API: http://localhost:8001
- API 文檔: http://localhost:8001/docs
- 健康檢查: http://localhost:8001/health

#### 3. 啟動 Admin UI（本地開發）

```bash
cd admin-ui

# 方式 1: 使用開發腳本（推薦）
chmod +x dev.sh
./dev.sh
# 腳本會自動：
# - 安裝 npm 依賴（如果不存在）
# - 從 .env.local.example 創建 .env.local（如果不存在）
# - 啟動開發服務器（Vite 熱重載）

# 方式 2: 手動啟動
npm install
# Vite 會自動從 .env.local 載入環境變數
npm run dev
```

**訪問地址**:
- Web UI: http://localhost:3000

## 🔧 環境變數配置

### Admin API (`admin-api/.env.local`)

```bash
LOG_LEVEL=DEBUG
MQTT_BROKER=localhost        # 本地開發使用 localhost
MQTT_PORT=1883
POSTGRES_HOST=localhost      # 本地開發使用 localhost
POSTGRES_PORT=5432
POSTGRES_DB=pump_testing
POSTGRES_USER=pump_user
POSTGRES_PASSWORD=pump_password_change_me
```

### Admin UI (`admin-ui/.env.local`)

```bash
VITE_API_URL=http://localhost:8001
VITE_MQTT_WS_URL=ws://localhost:8083
```

## 📝 開發工作流程

### 修改 Admin API

1. 編輯 `admin-api/` 目錄下的 Python 文件
2. 保存後，uvicorn 會自動重載（`--reload` 模式）
3. 查看終端輸出確認重載成功
4. 測試 API: http://localhost:8001/docs

### 修改 Admin UI

1. 編輯 `admin-ui/src/` 目錄下的 React 組件
2. Vite 會自動熱重載，瀏覽器自動刷新
3. 查看終端輸出確認編譯狀態

### 修改 Modbus Simulator

如果需要修改模擬器邏輯：

```bash
# 方式 1: 修改後重建容器
cd /home/datavan/pump_202510
docker compose up -d --build modbus-simulator

# 方式 2: 本地開發模擬器（需要額外配置）
cd simulator
# ... 本地運行模擬器
```

## 🐛 調試技巧

### Admin API 調試

1. **使用 FastAPI 自動文檔**:
   - Swagger UI: http://localhost:8001/docs
   - ReDoc: http://localhost:8001/redoc

2. **查看日誌**:
   - 終端會顯示所有請求日誌
   - 設置 `LOG_LEVEL=DEBUG` 查看詳細日誌

3. **使用 Python 調試器**:
   ```python
   # 在代碼中添加斷點
   import pdb; pdb.set_trace()
   ```

### Admin UI 調試

1. **瀏覽器開發者工具**:
   - F12 打開開發者工具
   - Console 查看錯誤和日誌
   - Network 查看 API 請求

2. **React DevTools**:
   - 安裝 Chrome 擴展: React Developer Tools
   - 檢查組件狀態和 Props

## 🔍 常見問題

### Q: 無法連接到 MQTT/PostgreSQL？

**A**: 確保基礎設施服務正在運行：
```bash
docker compose ps
# 應該看到 mqtt-broker, postgres, modbus-simulator 都是 "Up"
```

### Q: Admin UI 無法連接到 API？

**A**: 檢查環境變數：
```bash
# 確認 .env.local 文件存在且配置正確
cat admin-ui/.env.local
# 確認 VITE_API_URL=http://localhost:8001
```

### Q: 端口被佔用？

**A**: 檢查並停止佔用端口的進程：
```bash
# 檢查端口
lsof -i :8001  # Admin API
lsof -i :3000  # Admin UI

# 或修改端口
# Admin API: 修改 dev.sh 中的 --port 參數
# Admin UI: 修改 vite.config.js 中的 port
```

### Q: 需要重置資料庫？

**A**: 
```bash
# 停止並刪除 PostgreSQL 數據卷
docker compose down postgres
docker volume rm pump_202510_postgres_data

# 重新啟動
docker compose up -d postgres
```

## 🎯 開發建議

1. **使用 Git 分支**: 為新功能創建獨立分支
2. **頻繁提交**: 小步快跑，頻繁提交代碼
3. **測試優先**: 修改後立即測試相關功能
4. **查看日誌**: 關注終端和瀏覽器控制台輸出
5. **API 文檔**: 充分利用 FastAPI 自動生成的文檔

## 📚 相關文檔

- [Admin API README](./admin-api/README.md)
- [Admin UI README](./admin-ui/README.md)
- [Simulator Architecture](./docs/SIMULATOR_ARCHITECTURE.md)

## 🆚 Docker vs 本地開發對比

| 特性 | Docker 開發 | 本地開發（推薦） |
|------|------------|----------------|
| 熱重載 | ❌ 需要重建容器 | ✅ 自動重載 |
| 調試 | ⚠️ 需要進入容器 | ✅ IDE 直接調試 |
| 啟動速度 | ⚠️ 較慢（需要構建） | ✅ 快速 |
| 環境一致性 | ✅ 完全一致 | ⚠️ 需要配置 |
| 資源消耗 | ⚠️ 較高 | ✅ 較低 |
| **適合場景** | 生產部署、CI/CD | **日常開發** ✅ |

---

**結論**: 對於日常開發，**強烈推薦使用本地開發模式**，可以大大提高開發效率！

