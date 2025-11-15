# MODBUS 設備模擬器架構設計
## MODBUS Device Simulator Architecture

**文件版本**: 1.0  
**建立日期**: 2025.11.15  
**狀態**: 設計階段

---

## 📋 概述

本文件描述幫浦測試平台的 MODBUS 設備模擬器架構，用於在沒有實體設備時進行開發和測試。模擬器完全符合真實設備的 MODBUS RTU 通訊規格，並提供 Web UI 管理介面。

---

## 🎯 設計目標

1. **完全符合規格**: 模擬器必須完全符合真實設備的 MODBUS RTU 通訊規格
2. **易於管理**: 提供 Web UI 管理介面，可即時調整模擬數據
3. **容器化部署**: 所有組件使用 Docker Compose 管理
4. **可擴展性**: 易於添加新的模擬設備或功能
5. **真實性**: 模擬真實設備的行為（延遲、錯誤處理等）

---

## 🏗️ 架構設計

### 系統架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                    Admin UI (React)                          │
│              Port 3001 (http://localhost:3001)               │
│  - 設備狀態管理                                               │
│  - 模擬數據設定                                               │
│  - 場景管理                                                   │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ HTTP REST API
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Simulator Admin API (FastAPI)                   │
│                    Port 8001                                 │
│  - 設備配置管理                                               │
│  - 模擬數據設定                                               │
│  - 場景控制                                                   │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ Internal API
                              ▼
┌─────────────────────────────────────────────────────────────┐
│         MODBUS Simulator Service (Python)                    │
│                    Port 5020-5027                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Flow Meter   │  │ Power Meters │  │ Pressure     │      │
│  │ Simulator    │  │ Simulator    │  │ Sensors      │      │
│  │ (Slave ID 1) │  │ (Slave 1-4)  │  │ (Slave 2-3)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐                                           │
│  │ Relay IO     │                                           │
│  │ Simulator    │                                           │
│  │ (Slave ID 1) │                                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ Modbus TCP (Virtual Serial)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│         Virtual Serial Port Bridge                           │
│  - socat / pyserial                                          │
│  - TCP → Virtual Serial Port                                 │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ Virtual Serial Ports
                              │ /dev/ttyUSB0-3 (虛擬)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Python Backend (Existing)                       │
│         (連接虛擬串口，而非真實 USB-RS485)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 組件說明

### 1. MODBUS 模擬器服務 (Python)

**技術選型**: 
- `pymodbus` (Modbus Server)
- `asyncio` (非同步處理)
- `pydantic` (數據驗證)

**功能**:
- 模擬 8 台 MODBUS RTU 設備
- 支援所有功能碼（0x02, 0x03, 0x05, 0x0F）
- 符合真實設備的寄存器映射
- 支援動態數據更新

**設備列表**:

| 設備 | Slave ID | 模擬器端口 | 功能 |
|------|----------|-----------|------|
| 流量計 | 1 | 5020 | AFM07 流量計模擬 |
| DC 電表 | 1 | 5021 | JX3101 DC 電表模擬 |
| AC110V 電表 | 2 | 5022 | JX3101 AC110V 電表模擬 |
| AC220V 電表 | 3 | 5023 | JX3101 AC220V 電表模擬 |
| AC220V 3P 電表 | 4 | 5024 | JX8304M 三相電表模擬 |
| 壓力計 右 (正壓) | 2 | 5025 | Delta DPA 正壓模擬 |
| 壓力計 左 (真空) | 3 | 5026 | Delta DPA 真空模擬 |
| 繼電器 IO 模組 | 1 | 5027 | Waveshare Relay 模擬 |

### 2. 虛擬串口橋接器

**技術選型**:
- `socat` (TCP → Virtual Serial)
- 或 `pyserial` + `pyserial-asyncio`

**功能**:
- 將 Modbus TCP 連接轉換為虛擬串口
- 模擬 USB-RS485 轉換器的行為
- 支援多個虛擬串口（對應 4 個 USB 轉換器）

**虛擬串口映射**:

| USB 轉換器 | 虛擬串口 | TCP 端口 | 連接設備 |
|-----------|---------|---------|---------|
| USB-Enhanced-SERIAL-A | /dev/ttySIM0 | 5021-5024 | 電表 (4台) |
| USB-Enhanced-SERIAL-C | /dev/ttySIM1 | 5020 | 流量計 (1台) |
| USB-Enhanced-SERIAL-D | /dev/ttySIM2 | 5027 | 繼電器 IO (1台) |
| MOXA USB Serial Port | /dev/ttySIM3 | 5025-5026 | 壓力計 (2台) |

### 3. Admin API (FastAPI)

**技術選型**:
- FastAPI
- SQLite (配置存儲)
- WebSocket (即時更新)

**API 端點**:

```
GET    /api/devices              # 獲取所有設備狀態
GET    /api/devices/{device_id}  # 獲取單一設備狀態
PUT    /api/devices/{device_id}  # 更新設備模擬數據
POST   /api/devices/{device_id}/scenarios  # 設定場景
GET    /api/scenarios            # 獲取所有場景
POST   /api/scenarios            # 創建場景
DELETE /api/scenarios/{id}       # 刪除場景
```

### 4. Admin UI (React)

**技術選型**:
- React + Vite
- Tailwind CSS
- React Query (數據管理)
- WebSocket (即時更新)

**功能頁面**:
1. **設備狀態總覽**: 顯示所有設備的當前狀態
2. **設備配置**: 編輯每個設備的模擬數據
3. **場景管理**: 創建和管理測試場景
4. **數據生成器**: 設定數據變化模式（線性、正弦波、隨機等）

---

## 🐳 Docker Compose 架構

### docker-compose.yml 結構

```yaml
version: '3.8'

services:
  # MODBUS 模擬器服務
  modbus-simulator:
    build: ./simulator
    ports:
      - "5020-5027:5020-5027"  # Modbus TCP 端口
    volumes:
      - ./simulator/data:/app/data
      - ./simulator/config:/app/config
    environment:
      - LOG_LEVEL=INFO
    networks:
      - simulator-network

  # 虛擬串口橋接器
  serial-bridge:
    build: ./serial-bridge
    privileged: true  # 需要創建虛擬串口
    devices:
      - /dev/ttySIM0:/dev/ttySIM0
      - /dev/ttySIM1:/dev/ttySIM1
      - /dev/ttySIM2:/dev/ttySIM2
      - /dev/ttySIM3:/dev/ttySIM3
    depends_on:
      - modbus-simulator
    networks:
      - simulator-network

  # Admin API
  simulator-admin-api:
    build: ./admin-api
    ports:
      - "8001:8001"
    volumes:
      - ./admin-api/data:/app/data
    depends_on:
      - modbus-simulator
    networks:
      - simulator-network

  # Admin UI
  simulator-admin-ui:
    build: ./admin-ui
    ports:
      - "3001:3000"
    depends_on:
      - simulator-admin-api
    networks:
      - simulator-network

  # MQTT Broker (共用)
  mqtt-broker:
    image: eclipse-mosquitto:latest
    ports:
      - "1883:1883"
      - "8083:8083"
    volumes:
      - ./mqtt/config:/mosquitto/config
      - ./mqtt/data:/mosquitto/data
    networks:
      - simulator-network

networks:
  simulator-network:
    driver: bridge
```

---

## 📁 目錄結構

```
pump_simulator/
│
├── docker-compose.yml
├── README.md
│
├── simulator/                    # MODBUS 模擬器服務
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── config/
│   │   ├── devices.yaml         # 設備配置
│   │   └── scenarios.yaml       # 場景配置
│   ├── devices/
│   │   ├── __init__.py
│   │   ├── base.py              # 基礎模擬器類別
│   │   ├── flow_meter.py        # 流量計模擬器
│   │   ├── power_meter.py       # 電表模擬器
│   │   ├── pressure_sensor.py   # 壓力計模擬器
│   │   └── relay_io.py          # 繼電器 IO 模擬器
│   └── data/
│       └── .gitkeep
│
├── serial-bridge/                # 虛擬串口橋接器
│   ├── Dockerfile
│   ├── requirements.txt
│   └── bridge.py
│
├── admin-api/                    # Admin API
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── models/
│   │   ├── device.py
│   │   └── scenario.py
│   ├── routers/
│   │   ├── devices.py
│   │   └── scenarios.py
│   └── data/
│       └── simulator.db
│
├── admin-ui/                     # Admin UI
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── DeviceConfig.jsx
│   │   │   └── Scenarios.jsx
│   │   └── components/
│   │       ├── DeviceCard.jsx
│   │       └── DataGenerator.jsx
│   └── public/
│
└── mqtt/                         # MQTT 配置
    ├── config/
    │   └── mosquitto.conf
    └── data/
```

---

## 🔧 技術實作細節

### 1. MODBUS 模擬器實作

**基礎模擬器類別**:

```python
# simulator/devices/base.py
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
from typing import Dict, Any
import asyncio
import yaml

class BaseModbusSimulator:
    """MODBUS 模擬器基礎類別"""
    
    def __init__(self, slave_id: int, port: int, config: Dict[str, Any]):
        self.slave_id = slave_id
        self.port = port
        self.config = config
        self.store = ModbusSlaveContext(
            di=ModbusSequentialDataBlock(0, [0]*100),  # Discrete Inputs
            co=ModbusSequentialDataBlock(0, [0]*100),  # Coils
            hr=ModbusSequentialDataBlock(0, [0]*1000), # Holding Registers
            ir=ModbusSequentialDataBlock(0, [0]*100)   # Input Registers
        )
        self.context = ModbusServerContext(slaves={slave_id: self.store}, single=False)
        self._running = False
    
    async def start(self):
        """啟動模擬器"""
        await StartTcpServer(
            context=self.context,
            address=("0.0.0.0", self.port)
        )
    
    def update_register(self, address: int, value: int):
        """更新寄存器值"""
        self.store.setValues(3, address, [value])  # 3 = Holding Registers
    
    def get_register(self, address: int) -> int:
        """讀取寄存器值"""
        return self.store.getValues(3, address, 1)[0]
```

**流量計模擬器範例**:

```python
# simulator/devices/flow_meter.py
from .base import BaseModbusSimulator
import asyncio
import random

class FlowMeterSimulator(BaseModbusSimulator):
    """AFM07 流量計模擬器"""
    
    def __init__(self, slave_id: int = 1, port: int = 5020):
        config = {
            'instantaneous_flow': 0.0,  # L/min
            'cumulative_flow': 0.0,     # L
            'enabled': True
        }
        super().__init__(slave_id, port, config)
        
        # 初始化寄存器
        # 0x0000: 瞬时流量 (Unsigned Int16, 倍數 10)
        # 0x0001-0x0002: 累計流量 (Unsigned Int32, 倍數 10)
        self.update_register(0x0000, 0)
        self.update_register(0x0001, 0)
        self.update_register(0x0002, 0)
    
    async def simulate_loop(self):
        """模擬數據更新迴圈"""
        while self._running:
            if self.config['enabled']:
                # 更新瞬时流量 (0-50 L/min)
                instant_flow = self.config.get('instantaneous_flow', 0.0)
                instant_flow_raw = int(instant_flow * 10)  # 倍數 10
                self.update_register(0x0000, instant_flow_raw)
                
                # 更新累計流量
                cumulative_flow = self.config.get('cumulative_flow', 0.0)
                cumulative_flow_raw = int(cumulative_flow * 10)
                # 拆分為高 16 位和低 16 位
                high_word = (cumulative_flow_raw >> 16) & 0xFFFF
                low_word = cumulative_flow_raw & 0xFFFF
                self.update_register(0x0001, high_word)
                self.update_register(0x0002, low_word)
            
            await asyncio.sleep(1.0)  # 1Hz 更新
    
    def set_instantaneous_flow(self, value: float):
        """設定瞬时流量 (L/min)"""
        self.config['instantaneous_flow'] = max(0.0, min(50.0, value))
    
    def set_cumulative_flow(self, value: float):
        """設定累計流量 (L)"""
        self.config['cumulative_flow'] = max(0.0, value)
```

### 2. 虛擬串口橋接器

```python
# serial-bridge/bridge.py
import socket
import serial
import threading
from typing import Dict

class SerialBridge:
    """TCP 到虛擬串口的橋接器"""
    
    def __init__(self, tcp_port: int, serial_port: str, baudrate: int):
        self.tcp_port = tcp_port
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.running = False
    
    def start(self):
        """啟動橋接器"""
        self.running = True
        
        # 創建 TCP 服務器
        tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server.bind(('0.0.0.0', self.tcp_port))
        tcp_server.listen(1)
        
        # 創建虛擬串口
        ser = serial.Serial(self.serial_port, self.baudrate, timeout=1)
        
        # 啟動雙向轉發
        client_socket, _ = tcp_server.accept()
        
        def tcp_to_serial():
            while self.running:
                try:
                    data = client_socket.recv(1024)
                    if data:
                        ser.write(data)
                except:
                    break
        
        def serial_to_tcp():
            while self.running:
                try:
                    data = ser.read(1024)
                    if data:
                        client_socket.send(data)
                except:
                    break
        
        threading.Thread(target=tcp_to_serial, daemon=True).start()
        threading.Thread(target=serial_to_tcp, daemon=True).start()
```

### 3. Admin API 範例

```python
# admin-api/routers/devices.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(prefix="/api/devices", tags=["devices"])

class DeviceUpdate(BaseModel):
    enabled: bool = None
    data: Dict[str, Any] = None

@router.get("/")
async def get_all_devices():
    """獲取所有設備狀態"""
    # 從模擬器服務獲取狀態
    return {"devices": [...]}

@router.get("/{device_id}")
async def get_device(device_id: str):
    """獲取單一設備狀態"""
    # ...
    pass

@router.put("/{device_id}")
async def update_device(device_id: str, update: DeviceUpdate):
    """更新設備模擬數據"""
    # 發送更新到模擬器服務
    # ...
    pass
```

---

## 🎨 Admin UI 功能設計

### 主要功能

1. **設備狀態總覽**
   - 顯示所有 8 台設備的當前狀態
   - 即時數據更新（WebSocket）
   - 設備健康狀態指示

2. **設備配置編輯**
   - 編輯每個設備的模擬數據
   - 支援數據生成器（線性、正弦波、隨機）
   - 即時預覽數據變化

3. **場景管理**
   - 創建測試場景（如：正常測試、異常測試）
   - 保存和載入場景
   - 場景執行控制

4. **數據記錄**
   - 查看歷史模擬數據
   - 匯出數據為 CSV

---

## 🚀 部署步驟

### 1. 準備環境

```bash
# 創建項目目錄
mkdir -p pump_simulator
cd pump_simulator

# 創建目錄結構
mkdir -p {simulator,serial-bridge,admin-api,admin-ui,mqtt}/{config,data}
```

### 2. 構建和啟動

```bash
# 構建所有服務
docker-compose build

# 啟動所有服務
docker-compose up -d

# 查看日誌
docker-compose logs -f
```

### 3. 訪問服務

- **Admin UI**: http://localhost:3001
- **Admin API**: http://localhost:8001
- **API 文檔**: http://localhost:8001/docs

---

## 📊 數據模擬策略

### 1. 靜態數據
- 固定值，用於基本功能測試

### 2. 動態數據生成器
- **線性變化**: 用於測試數據趨勢
- **正弦波**: 模擬週期性變化
- **隨機變化**: 模擬真實環境的波動
- **場景驅動**: 根據測試場景自動變化

### 3. 場景範例

**正常測試場景**:
- 流量: 20-30 L/min (緩慢變化)
- 壓力: 0.5-0.8 MPa (穩定)
- 電流: 5-10 A (正常範圍)

**異常測試場景**:
- 流量: 突然降至 0 (模擬故障)
- 壓力: 超過上限 (觸發保護)
- 電流: 超過額定值 (觸發過載保護)

---

## ⚠️ 注意事項

1. **虛擬串口權限**: 需要適當的權限創建虛擬串口
2. **端口衝突**: 確保 Modbus TCP 端口不衝突
3. **數據一致性**: 確保模擬數據符合設備規格
4. **性能**: 模擬器應能處理 100Hz 的 IO 讀取

---

## 🔄 與真實設備的切換

當有真實設備時，只需：
1. 停止模擬器服務
2. 修改後端配置，將串口從 `/dev/ttySIM*` 改為真實串口
3. 重新啟動後端服務

**配置範例**:
```python
# config/modbus_devices.py
USE_SIMULATOR = False  # 切換為 False 使用真實設備

if USE_SIMULATOR:
    FLOW_METER_PORT = "/dev/ttySIM1"
else:
    FLOW_METER_PORT = "/dev/ttyUSB0"  # 真實串口
```

---

## 📝 下一步行動

1. ✅ 創建模擬器基礎架構
2. ✅ 實作各設備模擬器
3. ✅ 開發 Admin API
4. ✅ 開發 Admin UI
5. ✅ 整合到 Docker Compose
6. ✅ 測試與真實後端的整合

---

**文件結束**

