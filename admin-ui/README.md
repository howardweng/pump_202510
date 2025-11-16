# MODBUS 模擬器 Admin UI

React Web 管理介面，用於管理 MODBUS 設備模擬器。

## 功能

- ✅ 設備狀態總覽（即時顯示所有設備狀態）
- ✅ 設備配置編輯（更新設備模擬數據）
- ✅ 場景管理（創建、更新、刪除測試場景）
- ✅ 響應式設計（支援桌面和移動設備）

## 技術棧

- React 18
- Vite
- Tailwind CSS
- React Query（數據管理）
- React Router（路由）

## 使用方式

### 本地開發

```bash
# 安裝依賴
npm install

# 開發模式
npm run dev

# 構建
npm run build

# 預覽構建結果
npm run preview
```

### Docker Compose

```bash
# 從專案根目錄啟動
cd /home/datavan/pump_202510
docker compose up -d simulator-admin-ui
```

## 環境變數

- `VITE_API_URL` - Admin API URL（預設: http://localhost:8001）
- `VITE_MQTT_WS_URL` - MQTT WebSocket URL（預設: ws://localhost:8083）

## 訪問

- Web UI: http://localhost:3001

## 頁面說明

### 設備總覽
顯示所有 8 台設備的當前狀態，包括：
- 設備名稱和類型
- Slave ID 和端口
- 啟用/停用狀態
- 關鍵配置值（流量、壓力、電壓等）

### 設備配置
編輯每個設備的模擬數據：
- 啟用/停用設備
- 更新設備配置參數
- 根據設備類型顯示不同的配置項

### 場景管理
創建和管理測試場景：
- 創建新場景
- 查看場景列表
- 刪除場景



