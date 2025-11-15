"""感測器輪詢服務"""
import asyncio
import time
from typing import Dict, Optional
from loguru import logger
from core.mqtt_client import MQTTClient
from utils.throttled_publisher import ThrottledPublisher
from drivers.flow_meter import FlowMeterDriver
from drivers.pressure_sensor import PressureSensorDriver
from drivers.power_meter import (
    SinglePhasePowerMeterDriver,
    ThreePhasePowerMeterDriver
)
from config.mqtt_topics import (
    SENSOR_FLOW,
    SENSOR_PRESSURE_POSITIVE,
    SENSOR_PRESSURE_VACUUM,
    SENSOR_POWER_DC,
    SENSOR_POWER_AC110,
    SENSOR_POWER_AC220,
    SENSOR_POWER_AC220_3P
)


class SensorService:
    """
    感測器輪詢服務
    
    負責定期讀取所有感測器數據並發布到 MQTT
    """

    def __init__(self, mqtt_client: MQTTClient):
        self.mqtt = mqtt_client
        self.throttled_publisher = ThrottledPublisher(mqtt_client, min_interval=0.1)
        
        # 初始化所有感測器驅動
        self.flow_meter = FlowMeterDriver()
        self.pressure_positive = PressureSensorDriver("positive")
        self.pressure_vacuum = PressureSensorDriver("vacuum")
        self.dc_meter = SinglePhasePowerMeterDriver("dc")
        self.ac110v_meter = SinglePhasePowerMeterDriver("ac110")
        self.ac220v_meter = SinglePhasePowerMeterDriver("ac220")
        self.ac220v_3p_meter = ThreePhasePowerMeterDriver()
        
        self._running = False

    async def start(self):
        """啟動感測器服務"""
        # 連接所有感測器
        devices = [
            ("流量計", self.flow_meter),
            ("正壓計", self.pressure_positive),
            ("真空計", self.pressure_vacuum),
            ("DC 電表", self.dc_meter),
            ("AC110V 電表", self.ac110v_meter),
            ("AC220V 電表", self.ac220v_meter),
            ("AC220V 3P 電表", self.ac220v_3p_meter),
        ]
        
        connected = []
        for name, device in devices:
            # 使用異步連接（支援 TCP）
            result = await device.connect()
            
            if result:
                connected.append(name)
                logger.info(f"✅ {name} 已連線")
            else:
                logger.warning(f"⚠️ {name} 連線失敗")
        
        if not connected:
            logger.error("❌ 沒有感測器連線成功")
            return False
        
        logger.info(f"✅ 感測器服務已啟動 ({len(connected)}/{len(devices)} 個設備連線)")
        self._running = True
        return True

    async def polling_loop(self):
        """
        感測器輪詢迴圈
        
        根據不同感測器的輪詢頻率進行讀取
        """
        logger.info("🔄 感測器輪詢迴圈已啟動")
        
        # 輪詢計數器（用於控制不同頻率）
        counter = 0
        
        while self._running:
            loop_start = time.time()
            
            try:
                # 流量計：1Hz (每秒)
                if counter % 1 == 0:
                    await self._poll_flow_meter()
                
                # 壓力計：1Hz (每秒)
                if counter % 1 == 0:
                    await self._poll_pressure_sensors()
                
                # 電表：2Hz (每 0.5 秒)
                if counter % 1 == 0:  # 每秒讀取一次（簡化）
                    await self._poll_power_meters()
                
                # 定期刷新待發布的訊息
                if counter % 10 == 0:
                    await self.throttled_publisher.flush_pending()
                
                counter += 1
                
            except Exception as e:
                logger.exception(f"❌ 感測器輪詢異常: {e}")
            
            # 控制輪詢頻率（約 1Hz 基礎頻率）
            elapsed = time.time() - loop_start
            sleep_time = max(0, 1.0 - elapsed)
            await asyncio.sleep(sleep_time)

    async def _poll_flow_meter(self):
        """輪詢流量計"""
        try:
            data = await self.flow_meter.read_all()
            if data:
                await self.throttled_publisher.publish_if_needed(
                    SENSOR_FLOW,
                    {
                        **data,
                        "timestamp": time.time()
                    }
                )
        except Exception as e:
            logger.error(f"❌ 流量計讀取失敗: {e}")

    async def _poll_pressure_sensors(self):
        """輪詢壓力計"""
        try:
            # 正壓計
            pressure_pos = await self.pressure_positive.read_pressure()
            if pressure_pos is not None:
                await self.throttled_publisher.publish_if_needed(
                    SENSOR_PRESSURE_POSITIVE,
                    {
                        "pressure_mpa": pressure_pos,
                        "pressure_kgcm2": pressure_pos * 10.1972,
                        "timestamp": time.time()
                    }
                )
            
            # 真空計
            pressure_vac = await self.pressure_vacuum.read_pressure()
            if pressure_vac is not None:
                await self.throttled_publisher.publish_if_needed(
                    SENSOR_PRESSURE_VACUUM,
                    {
                        "pressure_mpa": pressure_vac,
                        "pressure_kpa": pressure_vac * 1000,
                        "timestamp": time.time()
                    }
                )
        except Exception as e:
            logger.error(f"❌ 壓力計讀取失敗: {e}")

    async def _poll_power_meters(self):
        """輪詢電表"""
        try:
            # DC 電表
            dc_data = await self.dc_meter.read_all()
            if dc_data:
                await self.throttled_publisher.publish_if_needed(
                    SENSOR_POWER_DC,
                    {
                        **dc_data,
                        "timestamp": time.time()
                    }
                )
            
            # AC110V 電表
            ac110_data = await self.ac110v_meter.read_all()
            if ac110_data:
                await self.throttled_publisher.publish_if_needed(
                    SENSOR_POWER_AC110,
                    {
                        **ac110_data,
                        "timestamp": time.time()
                    }
                )
            
            # AC220V 電表
            ac220_data = await self.ac220v_meter.read_all()
            if ac220_data:
                await self.throttled_publisher.publish_if_needed(
                    SENSOR_POWER_AC220,
                    {
                        **ac220_data,
                        "timestamp": time.time()
                    }
                )
            
            # AC220V 3P 電表
            ac220_3p_data = await self.ac220v_3p_meter.read_all()
            if ac220_3p_data:
                await self.throttled_publisher.publish_if_needed(
                    SENSOR_POWER_AC220_3P,
                    {
                        **ac220_3p_data,
                        "timestamp": time.time()
                    }
                )
        except Exception as e:
            logger.error(f"❌ 電表讀取失敗: {e}")

    def stop(self):
        """停止感測器服務"""
        self._running = False
        # 斷開所有感測器
        self.flow_meter.disconnect()
        self.pressure_positive.disconnect()
        self.pressure_vacuum.disconnect()
        self.dc_meter.disconnect()
        self.ac110v_meter.disconnect()
        self.ac220v_meter.disconnect()
        self.ac220v_3p_meter.disconnect()
        logger.info("🛑 感測器服務已停止")

