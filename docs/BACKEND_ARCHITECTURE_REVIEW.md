# 後端架構設計評估報告
## Backend Architecture Review Report

**文件版本**: 1.0  
**評估日期**: 2025.11.15  
**評估者**: AI Code Review  
**狀態**: 待審核

---

## 執行摘要

整體架構設計**良好**，符合工業自動化系統需求。但存在幾個**關鍵技術問題**需要修正，特別是**非同步實作**和**效能瓶頸**。建議優先處理高優先級問題，確保系統穩定性和即時性。

**總體評分**: 7.5/10

---

## 1. 架構優點 ✅

### 1.1 設計原則清晰
- ✅ **事件驅動架構**: MQTT 解耦前後端，符合現代設計模式
- ✅ **安全優先**: 100Hz 安全監控符合工業安全標準
- ✅ **模組化設計**: 分層清晰，易於維護和測試
- ✅ **文檔完整**: 涵蓋設計、部署、測試全流程

### 1.2 技術選型合理
- ✅ **Python + asyncio**: 適合工業自動化場景
- ✅ **MQTT**: 輕量、可靠，支援 WebSocket
- ✅ **SQLite**: 輕量級，適合嵌入式系統
- ✅ **pymodbus**: 成熟的 Modbus 實作

---

## 2. 關鍵問題與改進建議 ⚠️

### 2.1 🔴 **高優先級: MQTT 客戶端非同步問題**

**問題描述**:
- `paho-mqtt` 是**同步庫**，使用 `loop_start()` 會建立背景執行緒
- 與 `asyncio` 混用可能導致：
  - 回調函數在非主執行緒執行，無法直接使用 `await`
  - 訊息處理可能阻塞事件循環
  - 難以正確處理異常和資源清理

**當前實作問題**:
```python
# ❌ 問題代碼
self.client.loop_start()  # 背景執行緒
while not self.connected:
    await asyncio.sleep(0.1)  # 忙等待

def _on_message(self, client, userdata, msg):
    # 這個回調在背景執行緒執行，無法直接 await
    self.subscriptions[topic](payload)  # 如果 callback 是 async 會出問題
```

**建議解決方案**:

**方案 A: 使用 `aiomqtt` (推薦)**
```python
# ✅ 推薦方案
import asyncio
from aiomqtt import Client
from loguru import logger

class MQTTClient:
    def __init__(self, broker: str, port: int, username: str = "", password: str = ""):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.subscriptions: Dict[str, Callable] = {}
        self.client: Optional[Client] = None
        self._message_task: Optional[asyncio.Task] = None

    async def start(self):
        """啟動 MQTT 連線"""
        try:
            self.client = Client(
                hostname=self.broker,
                port=self.port,
                username=self.username if self.username else None,
                password=self.password if self.password else None
            )
            await self.client.__aenter__()
            logger.info(f"✅ MQTT 已連線至 {self.broker}:{self.port}")
            
            # 啟動訊息處理任務
            self._message_task = asyncio.create_task(self._message_loop())
            
        except Exception as e:
            logger.exception(f"❌ MQTT 連線失敗: {e}")
            raise

    async def _message_loop(self):
        """訊息處理迴圈"""
        async with self.client.messages() as messages:
            await self.client.subscribe([(topic, 1) for topic in self.subscriptions.keys()])
            async for message in messages:
                topic = message.topic.value
                try:
                    payload = json.loads(message.payload.decode())
                    if topic in self.subscriptions:
                        callback = self.subscriptions[topic]
                        if asyncio.iscoroutinefunction(callback):
                            await callback(payload)
                        else:
                            callback(payload)
                except Exception as e:
                    logger.error(f"❌ MQTT 訊息處理失敗 [{topic}]: {e}")

    async def publish(self, topic: str, payload: dict, qos: int = 1):
        """發布訊息"""
        try:
            message = json.dumps(payload, ensure_ascii=False)
            await self.client.publish(topic, message, qos=qos)
        except Exception as e:
            logger.error(f"❌ MQTT 發布異常 [{topic}]: {e}")

    async def disconnect(self):
        """斷線"""
        if self._message_task:
            self._message_task.cancel()
        if self.client:
            await self.client.__aexit__(None, None, None)
        logger.info("🔌 MQTT 已斷線")
```

**方案 B: 使用 `asyncio-mqtt` (替代方案)**
```python
from asyncio_mqtt import Client

async def start(self):
    self.client = Client(self.broker, self.port)
    await self.client.connect()
    # ... 類似實作
```

**影響評估**:
- **修改範圍**: 中等（需重寫 MQTT 客戶端）
- **風險**: 低（`aiomqtt` 是成熟庫）
- **效益**: 高（解決非同步問題，提升穩定性）

---

### 2.2 🔴 **高優先級: 100Hz 輪詢效能問題**

**問題描述**:
- Python 的 `asyncio.sleep(0.01)` 在實際環境中可能無法精確達到 10ms
- MODBUS 讀取操作本身需要時間（通常 10-50ms），可能導致：
  - 實際輪詢頻率低於 100Hz
  - 緊急停止反應時間超過 100ms 要求
  - CPU 使用率過高

**當前實作問題**:
```python
# ❌ 可能無法達到 100Hz
while True:
    io_status = await self.io_driver.read_digital_inputs()  # 可能需要 10-50ms
    # ... 處理邏輯
    await asyncio.sleep(0.01)  # 10ms，但加上上面的時間，實際間隔可能 > 10ms
```

**建議解決方案**:

**方案 A: 使用專用執行緒 + 高精度定時器**
```python
import threading
import time
from queue import Queue

class SafetyMonitor:
    def __init__(self, mqtt_client: MQTTClient):
        self.mqtt = mqtt_client
        self.io_driver = RelayIODriver()
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._status_queue = Queue()  # 用於與主執行緒通信

    def start(self):
        """啟動安全監控（在專用執行緒中）"""
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop_thread,
            daemon=True,
            name="SafetyMonitor"
        )
        self._monitor_thread.start()
        logger.info("🛡️ 安全監控器已啟動 (100Hz, 專用執行緒)")

    def _monitor_loop_thread(self):
        """專用執行緒中的監控迴圈"""
        target_interval = 0.01  # 10ms
        
        while not self._stop_event.is_set():
            loop_start = time.perf_counter()
            
            try:
                # 讀取 IO 狀態（同步操作）
                io_status = self.io_driver.read_digital_inputs_sync()
                
                if io_status is not None:
                    emergency_pressed = bool(io_status & 0x01)
                    cover_closed = bool(io_status & 0x02)
                    
                    # 將狀態放入佇列，由主執行緒處理 MQTT 發布
                    self._status_queue.put({
                        'emergency_stop': emergency_pressed,
                        'cover_closed': cover_closed,
                        'timestamp': time.time()
                    })
                    
                    # 緊急停止處理（立即執行，不等待 MQTT）
                    if emergency_pressed and not self.emergency_stop_active:
                        self._handle_emergency_stop_sync()
                        
            except Exception as e:
                logger.exception(f"❌ 安全監控異常: {e}")
            
            # 精確睡眠，補償執行時間
            elapsed = time.perf_counter() - loop_start
            sleep_time = max(0, target_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                logger.warning(f"⚠️ 安全監控迴圈超時: {elapsed*1000:.2f}ms > 10ms")

    async def _publish_status_loop(self):
        """在主執行緒中處理 MQTT 發布"""
        while True:
            try:
                # 非阻塞讀取佇列
                status = self._status_queue.get_nowait()
                await self.mqtt.publish('pump/safety/status', status)
            except:
                await asyncio.sleep(0.001)  # 1ms
```

**方案 B: 使用硬體中斷（如果 IO 模組支援）**
- 如果 Waveshare 繼電器模組支援硬體中斷，優先使用中斷而非輪詢
- 可大幅降低 CPU 使用率，提升反應速度

**影響評估**:
- **修改範圍**: 中等（需重構安全監控器）
- **風險**: 中（需充分測試）
- **效益**: 高（確保 100ms 反應時間）

---

### 2.3 🟡 **中優先級: MODBUS 驅動非同步實作問題**

**問題描述**:
- `pymodbus` 的 `ModbusSerialClient` 是**同步**的
- 在 `asyncio` 環境中使用會阻塞事件循環
- 多個設備同時讀取時可能造成延遲累積

**當前實作問題**:
```python
# ❌ 同步操作會阻塞事件循環
async def read_holding_registers(self, address: int, count: int):
    result = self.client.read_holding_registers(...)  # 同步操作，阻塞！
    return result.registers
```

**建議解決方案**:

**方案 A: 使用 `run_in_executor` 包裝同步操作**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ModbusDevice:
    def __init__(self, ...):
        # ... 初始化
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix=f"Modbus-{port}")

    async def read_holding_registers(self, address: int, count: int):
        """在執行緒池中執行同步 MODBUS 操作"""
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                self._executor,
                self._read_holding_registers_sync,
                address,
                count
            )
            return result
        except Exception as e:
            logger.error(f"❌ MODBUS 讀取異常: {e}")
            return None

    def _read_holding_registers_sync(self, address: int, count: int):
        """同步 MODBUS 讀取（在執行緒池中執行）"""
        result = self.client.read_holding_registers(
            address=address,
            count=count,
            slave=self.slave_id
        )
        if result.isError():
            raise ModbusException(f"讀取錯誤: {result}")
        return result.registers
```

**方案 B: 使用非同步 Modbus 庫（如果存在）**
- 搜尋是否有支援 `asyncio` 的 Modbus 庫
- 或考慮使用 `pymodbus` 的異步版本（如果有的話）

**影響評估**:
- **修改範圍**: 小（只需包裝現有方法）
- **風險**: 低
- **效益**: 中（提升並發效能）

---

### 2.4 🟡 **中優先級: 錯誤處理與重試機制不足**

**問題描述**:
- MODBUS 通訊可能因硬體問題、電磁干擾等導致失敗
- 當前實作缺少：
  - 自動重試機制
  - 錯誤計數和降級策略
  - 設備健康狀態監控

**建議改進**:

```python
from typing import Optional
from dataclasses import dataclass
from enum import Enum

class DeviceHealth(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"  # 偶爾失敗
    UNHEALTHY = "unhealthy"  # 連續失敗
    OFFLINE = "offline"  # 完全無法通訊

@dataclass
class DeviceStatus:
    health: DeviceHealth
    error_count: int = 0
    last_success_time: Optional[float] = None
    last_error_time: Optional[float] = None

class ModbusDevice:
    def __init__(self, ...):
        # ... 初始化
        self.status = DeviceStatus(health=DeviceHealth.HEALTHY)
        self.max_retries = 3
        self.retry_delay = 0.1
        self.error_threshold = 5  # 連續 5 次失敗視為不健康

    async def read_holding_registers(
        self,
        address: int,
        count: int,
        retry: bool = True
    ) -> Optional[List[int]]:
        """帶重試機制的讀取"""
        for attempt in range(self.max_retries if retry else 1):
            try:
                result = await self._read_holding_registers_internal(address, count)
                
                # 成功：重置錯誤計數
                if self.status.error_count > 0:
                    self.status.error_count = 0
                    if self.status.health != DeviceHealth.HEALTHY:
                        self.status.health = DeviceHealth.HEALTHY
                        logger.info(f"✅ 設備恢復正常: {self.port}")
                
                self.status.last_success_time = time.time()
                return result
                
            except Exception as e:
                self.status.error_count += 1
                self.status.last_error_time = time.time()
                
                if attempt < self.max_retries - 1:
                    logger.warning(
                        f"⚠️ MODBUS 讀取失敗 (嘗試 {attempt+1}/{self.max_retries}): {e}"
                    )
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(f"❌ MODBUS 讀取最終失敗: {e}")
                    self._update_health_status()
                    return None
        
        return None

    def _update_health_status(self):
        """更新設備健康狀態"""
        if self.status.error_count >= self.error_threshold:
            if self.status.health != DeviceHealth.UNHEALTHY:
                self.status.health = DeviceHealth.UNHEALTHY
                logger.error(f"❌ 設備不健康: {self.port} (錯誤次數: {self.status.error_count})")
                # 發送 MQTT 警報
                asyncio.create_task(self._publish_health_alert())
```

---

### 2.5 🟡 **中優先級: 資源管理與清理**

**問題描述**:
- 串口資源可能未正確釋放
- 異常退出時可能導致資源洩漏
- 缺少優雅關閉機制

**建議改進**:

```python
import atexit
from contextlib import asynccontextmanager

class ModbusDevice:
    def __init__(self, ...):
        # ... 初始化
        self._cleanup_registered = False
        self._register_cleanup()

    def _register_cleanup(self):
        """註冊清理函數"""
        if not self._cleanup_registered:
            atexit.register(self.disconnect)
            self._cleanup_registered = True

    @asynccontextmanager
    async def connection(self):
        """上下文管理器，確保資源正確釋放"""
        try:
            if not self.connected:
                await self.connect()
            yield self
        finally:
            # 不自動斷線，由外部管理生命週期
            pass

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
```

---

### 2.6 🟢 **低優先級: 數據持久化策略**

**問題描述**:
- CSV 和 SQLite 的寫入策略未明確
- 缺少數據完整性保護（如斷電保護）
- 未考慮大量數據的效能問題

**建議改進**:

```python
class DataLogger:
    def __init__(self):
        self._buffer = []  # 記憶體緩衝
        self._buffer_size = 100  # 每 100 筆寫入一次
        self._write_lock = asyncio.Lock()

    async def log_data(self, data: dict):
        """緩衝寫入，提升效能"""
        async with self._write_lock:
            self._buffer.append(data)
            
            if len(self._buffer) >= self._buffer_size:
                await self._flush_buffer()

    async def _flush_buffer(self):
        """批量寫入數據"""
        if not self._buffer:
            return
        
        try:
            # 批量寫入 CSV
            await self._write_csv_batch(self._buffer)
            # 批量寫入 SQLite
            await self._write_db_batch(self._buffer)
            
            self._buffer.clear()
        except Exception as e:
            logger.error(f"❌ 數據寫入失敗: {e}")
            # 保留緩衝區，稍後重試

    async def shutdown(self):
        """優雅關閉：寫入剩餘數據"""
        await self._flush_buffer()
```

---

## 3. 架構設計改進建議 💡

### 3.1 增加配置驗證層

**建議**: 在啟動時驗證所有配置，避免運行時錯誤

```python
# config/validator.py
from pydantic import BaseModel, validator
from pathlib import Path

class ModbusConfig(BaseModel):
    port: str
    baudrate: int
    slave_id: int
    
    @validator('port')
    def port_exists(cls, v):
        if not Path(v).exists():
            raise ValueError(f"串口不存在: {v}")
        return v

class Settings(BaseModel):
    mqtt_broker: str
    mqtt_port: int
    modbus_devices: List[ModbusConfig]
    
    def validate_all(self):
        """驗證所有配置"""
        # 檢查 MQTT 連線
        # 檢查串口可用性
        # 檢查設備地址衝突
        pass
```

### 3.2 增加監控與可觀測性

**建議**: 添加 Prometheus metrics 或自定義監控指標

```python
# core/metrics.py
from dataclasses import dataclass
from typing import Dict

@dataclass
class SystemMetrics:
    modbus_read_success_rate: float
    modbus_read_latency_ms: float
    mqtt_publish_rate: float
    safety_monitor_loop_time_ms: float
    active_test_count: int
    device_health_status: Dict[str, str]

class MetricsCollector:
    def __init__(self):
        self.metrics = SystemMetrics(...)
    
    async def publish_metrics(self):
        """定期發布系統指標至 MQTT"""
        await self.mqtt.publish('pump/system/metrics', {
            'modbus_success_rate': self.metrics.modbus_read_success_rate,
            # ...
        })
```

### 3.3 增加測試覆蓋率要求

**建議**: 明確測試覆蓋率目標

- **單元測試**: ≥ 80%
- **整合測試**: 所有關鍵流程
- **硬體在環測試**: 所有 MODBUS 設備

---

## 4. 安全性改進建議 🔒

### 4.1 MQTT 身份驗證

**當前**: `allow_anonymous true` (測試環境)

**建議**: 生產環境必須啟用身份驗證

```conf
# mosquitto.conf (生產環境)
allow_anonymous false
password_file /etc/mosquitto/passwd
acl_file /etc/mosquitto/acl
```

### 4.2 輸入驗證

**建議**: 所有 MQTT 指令都應驗證

```python
from pydantic import BaseModel, validator

class StartTestCommand(BaseModel):
    mode: str
    type: str
    config: dict
    
    @validator('mode')
    def valid_mode(cls, v):
        if v not in ['vacuum', 'positive', 'manual']:
            raise ValueError(f"無效的測試模式: {v}")
        return v
```

---

## 5. 效能優化建議 ⚡

### 5.1 MODBUS 讀取優化

**建議**: 批量讀取多個寄存器，減少通訊次數

```python
# ❌ 低效：多次讀取
voltage = await read_register(0x1000, 2)
current = await read_register(0x1002, 2)
power = await read_register(0x1004, 2)

# ✅ 高效：一次讀取
data = await read_register(0x1000, 6)  # 一次讀取 6 個寄存器
voltage = parse_int32(data[0:2])
current = parse_int32(data[2:4])
power = parse_int32(data[4:6])
```

### 5.2 MQTT 訊息頻率優化

**建議**: 只在數據變化時發布，或使用節流（throttle）

```python
from collections import deque

class ThrottledPublisher:
    def __init__(self, mqtt_client, min_interval: float = 0.1):
        self.mqtt = mqtt_client
        self.min_interval = min_interval
        self.last_publish_time = {}
    
    async def publish_if_needed(self, topic: str, payload: dict):
        """只在間隔時間足夠時發布"""
        now = time.time()
        last_time = self.last_publish_time.get(topic, 0)
        
        if now - last_time >= self.min_interval:
            await self.mqtt.publish(topic, payload)
            self.last_publish_time[topic] = now
```

---

## 6. 文檔改進建議 📚

### 6.1 增加 API 文檔

**建議**: 使用 Sphinx 或 MkDocs 生成 API 文檔

### 6.2 增加故障排除指南

**建議**: 添加常見問題和解決方案

---

## 7. 優先級行動計劃 📋

### 立即處理 (本週)
1. ✅ **修正 MQTT 客戶端非同步問題** (使用 `aiomqtt`)
2. ✅ **優化安全監控器 100Hz 輪詢** (使用專用執行緒)
3. ✅ **添加 MODBUS 錯誤重試機制**

### 短期改進 (2 週內)
4. ✅ **添加設備健康監控**
5. ✅ **優化資源管理與清理**
6. ✅ **添加配置驗證**

### 中期改進 (1 個月內)
7. ✅ **增加監控指標**
8. ✅ **優化數據持久化**
9. ✅ **完善測試覆蓋率**

---

## 8. 總結

### 優點
- ✅ 架構設計清晰，符合工業標準
- ✅ 安全優先設計，符合 PRD 要求
- ✅ 文檔完整，易於理解和實作

### 需要改進
- ⚠️ **MQTT 非同步實作** (關鍵問題)
- ⚠️ **100Hz 輪詢效能** (關鍵問題)
- ⚠️ **錯誤處理機制** (重要問題)

### 總體評估
架構設計**良好**，但需要修正幾個**關鍵技術問題**。建議優先處理高優先級問題，確保系統穩定性和即時性。修正後，系統應能滿足 PRD 要求。

**建議評分**: 修正後可達 **9/10**

---

**文件結束**

