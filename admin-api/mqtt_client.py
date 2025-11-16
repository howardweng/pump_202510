"""MQTT 客戶端管理"""
import asyncio
from aiomqtt import Client
from loguru import logger
import os
import json

# MQTT 主題映射
DEVICE_TOPIC_MAP = {
    "flow_meter": "pump/sensors/flow",
    "pressure_positive": "pump/sensors/pressure/positive",
    "pressure_vacuum": "pump/sensors/pressure/vacuum",
    "dc_meter": "pump/sensors/power/dc",
    "ac110v_meter": "pump/sensors/power/ac110",
    "ac220v_meter": "pump/sensors/power/ac220",
    "ac220v_3p_meter": "pump/sensors/power/ac220_3p",
}

class MQTTManager:
    """MQTT 客戶端管理器"""
    
    def __init__(self):
        self.client: Client | None = None
        self._connected = False
        self._lock = asyncio.Lock()
    
    async def connect(self):
        """連接到 MQTT Broker"""
        if self._connected and self.client:
            return
        
        async with self._lock:
            if self._connected and self.client:
                return
            
            broker = os.getenv("MQTT_BROKER", "localhost")
            port = int(os.getenv("MQTT_PORT", "1883"))
            
            try:
                self.client = Client(hostname=broker, port=port)
                await self.client.__aenter__()
                self._connected = True
                logger.info(f"✅ MQTT 已連接到 {broker}:{port}")
            except Exception as e:
                logger.error(f"❌ MQTT 連接失敗: {e}")
                self._connected = False
                self.client = None
                raise
    
    async def disconnect(self):
        """斷開 MQTT 連接"""
        if self.client and self._connected:
            try:
                await self.client.__aexit__(None, None, None)
                self._connected = False
                logger.info("🔌 MQTT 已斷開連接")
            except Exception as e:
                logger.error(f"❌ MQTT 斷開連接失敗: {e}")
            finally:
                self.client = None
    
    async def publish_device_data(self, device_id: str, device_type: str, config: dict, enabled: bool, raw_registers: dict = None):
        """發布設備數據到 MQTT"""
        if not enabled:
            # 設備關閉時不發布數據
            return
        
        topic = DEVICE_TOPIC_MAP.get(device_id)
        if not topic:
            # 如果沒有對應的主題，不發布
            return
        
        try:
            # 確保已連接
            if not self._connected or not self.client:
                await self.connect()
            
            # 準備發布的數據
            payload = config.copy()
            payload["enabled"] = enabled
            payload["device_id"] = device_id
            
            # 添加原始寄存器數據
            if raw_registers:
                payload["raw_registers"] = raw_registers
            
            # 發布到 MQTT
            await self.client.publish(topic, payload=json.dumps(payload))
            logger.debug(f"📤 已發布到 {topic}: {payload}")
        except Exception as e:
            logger.error(f"❌ 發布 MQTT 數據失敗 ({device_id}): {e}")
            # 如果連接失敗，嘗試重新連接
            if not self._connected:
                try:
                    await self.connect()
                    # 重試發布
                    if self._connected and self.client:
                        await self.client.publish(topic, payload=json.dumps(payload))
                except Exception as retry_error:
                    logger.error(f"❌ 重試發布失敗: {retry_error}")
    
    async def publish_all_devices(self, devices_dict: dict):
        """發布所有啟用設備的數據"""
        from modbus_reader import modbus_reader
        
        logger.info(f"🔄 開始發布所有設備數據，共 {len(devices_dict)} 個設備")
        logger.debug(f"🔄 開始發布所有設備數據，共 {len(devices_dict)} 個設備")  # 同時輸出 DEBUG 級別
        
        for device_id, device_data in devices_dict.items():
            if device_data.get("enabled", False):
                # 讀取 Modbus 寄存器原始數據
                try:
                    logger.info(f"📖 嘗試讀取 {device_id} 的寄存器...")
                    logger.debug(f"📖 嘗試讀取 {device_id} 的寄存器...")  # 同時輸出 DEBUG 級別
                    raw_registers = await modbus_reader.read_registers(device_id, device_data)
                    if raw_registers:
                        logger.info(f"✅ 讀取到 {device_id} 的寄存器數據: {len(raw_registers.get('registers', []))} 個寄存器")
                        logger.debug(f"✅ 讀取到 {device_id} 的寄存器數據: {len(raw_registers.get('registers', []))} 個寄存器")  # 同時輸出 DEBUG 級別
                    else:
                        logger.info(f"⚠️ {device_id} 的寄存器讀取返回 None")
                        logger.debug(f"⚠️ {device_id} 的寄存器讀取返回 None")  # 同時輸出 DEBUG 級別
                except Exception as e:
                    logger.error(f"❌ 讀取 {device_id} 寄存器時發生異常: {e}", exc_info=True)
                    raw_registers = None
                
                await self.publish_device_data(
                    device_id=device_id,
                    device_type=device_data.get("type", ""),
                    config=device_data.get("config", {}),
                    enabled=True,
                    raw_registers=raw_registers
                )

# 全域 MQTT 管理器實例
mqtt_manager = MQTTManager()

