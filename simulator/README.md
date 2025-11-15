# MODBUS 設備模擬器

根據 `MODBUS_all_devices.md` 規格實作的 MODBUS RTU 設備模擬器，用於在沒有實體設備時進行開發和測試。

## 📋 功能

- ✅ 完全符合真實設備的 MODBUS RTU 通訊規格
- ✅ 支援 8 台設備模擬（流量計、電表、壓力計、繼電器 IO）
- ✅ 異步 MODBUS TCP 服務器
- ✅ 動態數據更新（支援不同輪詢頻率）
- ✅ 容器化部署

## 🏗️ 設備列表

| 設備 | Slave ID | Port | 類型 |
|------|----------|------|------|
| 流量計 | 1 | 5020 | AFM07 |
| DC 電表 | 1 | 5021 | JX3101 |
| AC110V 電表 | 2 | 5022 | JX3101 |
| AC220V 電表 | 3 | 5023 | JX3101 |
| AC220V 3P 電表 | 4 | 5024 | JX8304M |
| 壓力計 右 (正壓) | 2 | 5025 | Delta DPA |
| 壓力計 左 (真空) | 3 | 5026 | Delta DPA |
| 繼電器 IO 模組 | 1 | 5027 | Waveshare |

## 🚀 使用方式

### 本地開發

```bash
# 安裝依賴
pip install -r requirements.txt

# 運行模擬器
python main.py
```

### Docker 構建

```bash
# 構建映像
docker build -t pump-modbus-simulator .

# 運行容器
docker run -d \
  --name modbus-simulator \
  -p 5020-5027:5020-5027 \
  pump-modbus-simulator
```

### Docker Compose

```bash
# 從專案根目錄啟動
cd /home/datavan/pump_202510
docker compose up -d modbus-simulator
```

## 📝 配置

配置文件位於 `config/devices.yaml`，可以調整各設備的默認值。

## 🔧 技術細節

- **Python**: 3.11+
- **pymodbus**: 3.5.0+ (異步 MODBUS 服務器)
- **asyncio**: 異步事件循環
- **loguru**: 日誌記錄

## 📚 參考文檔

- `docs/MODBUS_all_devices.md` - 設備規格
- `docs/SIMULATOR_ARCHITECTURE.md` - 架構設計

