"""控制服務 - 閥門和電源控制"""
import asyncio
from typing import Dict, Optional
from loguru import logger
from core.mqtt_client import MQTTClient
from core.safety_monitor import SafetyMonitor
from drivers.relay_io import RelayIODriver
from config.mqtt_topics import CONTROL_VALVE, CONTROL_POWER, CONTROL_TEST


class ControlService:
    """
    控制服務
    
    負責處理閥門和電源控制命令
    所有操作都需要通過安全檢查
    """

    def __init__(self, mqtt_client: MQTTClient, safety_monitor: SafetyMonitor):
        self.mqtt = mqtt_client
        self.safety = safety_monitor
        self.io_driver = RelayIODriver()
        self._running = False

    async def start(self):
        """啟動控制服務"""
        if not self.io_driver.connect():
            logger.error("❌ IO 模組連線失敗，控制服務無法啟動")
            return False
        
        logger.info("✅ 控制服務已啟動")
        self._running = True
        return True

    async def command_handler(self):
        """
        MQTT 命令處理迴圈
        
        訂閱控制命令主題並處理
        """
        logger.info("🔄 控制命令處理迴圈已啟動")
        
        # 訂閱控制命令主題
        self.mqtt.subscribe(CONTROL_VALVE, self._handle_valve_command)
        self.mqtt.subscribe(CONTROL_POWER, self._handle_power_command)
        self.mqtt.subscribe(CONTROL_TEST, self._handle_test_command)
        
        # 保持運行
        while self._running:
            await asyncio.sleep(1.0)

    async def _handle_valve_command(self, payload: Dict):
        """
        處理閥門控制命令
        
        命令格式:
        {
            "valve": "A" | "B" | "C" | "D",
            "state": true | false
        }
        """
        try:
            valve = payload.get("valve", "").upper()
            state = payload.get("state", False)
            
            if valve not in ["A", "B", "C", "D"]:
                logger.error(f"❌ 無效的閥門: {valve}")
                return
            
            # 安全檢查
            can_proceed, error_msg = self.safety.check_start_conditions()
            if not can_proceed:
                logger.warning(f"⚠️ 閥門控制被拒絕: {error_msg}")
                await self.mqtt.publish(CONTROL_VALVE, {
                    "status": "error",
                    "message": error_msg
                })
                return
            
            # 控制閥門
            channel_map = {"A": 1, "B": 2, "C": 3, "D": 4}
            channel = channel_map[valve]
            success = await self.io_driver.set_relay(channel, state)
            
            if success:
                logger.info(f"✅ 閥門 {valve} 已{'開啟' if state else '關閉'}")
                await self.mqtt.publish(CONTROL_VALVE, {
                    "status": "success",
                    "valve": valve,
                    "state": state
                })
            else:
                logger.error(f"❌ 閥門 {valve} 控制失敗")
                await self.mqtt.publish(CONTROL_VALVE, {
                    "status": "error",
                    "message": f"閥門 {valve} 控制失敗"
                })
                
        except Exception as e:
            logger.exception(f"❌ 處理閥門命令異常: {e}")

    async def _handle_power_command(self, payload: Dict):
        """
        處理電源控制命令
        
        命令格式:
        {
            "power_type": "dc" | "ac110" | "ac220" | "ac220_3p",
            "state": true | false
        }
        """
        try:
            power_type = payload.get("power_type", "")
            state = payload.get("state", False)
            
            # 安全檢查
            can_proceed, error_msg = self.safety.check_start_conditions()
            if not can_proceed:
                logger.warning(f"⚠️ 電源控制被拒絕: {error_msg}")
                await self.mqtt.publish(CONTROL_POWER, {
                    "status": "error",
                    "message": error_msg
                })
                return
            
            # 控制電源
            channel_map = {
                "dc": 5,
                "ac110": 6,
                "ac220": 7,
                "ac220_3p": 8
            }
            
            channel = channel_map.get(power_type)
            if channel is None:
                logger.error(f"❌ 無效的電源類型: {power_type}")
                return
            
            success = await self.io_driver.set_relay(channel, state)
            
            if success:
                logger.info(f"✅ 電源 {power_type} 已{'開啟' if state else '關閉'}")
                await self.mqtt.publish(CONTROL_POWER, {
                    "status": "success",
                    "power_type": power_type,
                    "state": state
                })
            else:
                logger.error(f"❌ 電源 {power_type} 控制失敗")
                await self.mqtt.publish(CONTROL_POWER, {
                    "status": "error",
                    "message": f"電源 {power_type} 控制失敗"
                })
                
        except Exception as e:
            logger.exception(f"❌ 處理電源命令異常: {e}")

    async def _handle_test_command(self, payload: Dict):
        """
        處理測試命令
        
        命令格式:
        {
            "action": "start" | "stop" | "pause" | "resume",
            ...
        }
        """
        try:
            action = payload.get("action", "")
            logger.info(f"📋 收到測試命令: {action}")
            
            # TODO: 實作測試命令處理邏輯
            # 這將與自動測試引擎整合
            
        except Exception as e:
            logger.exception(f"❌ 處理測試命令異常: {e}")

    async def emergency_shutdown(self):
        """
        緊急關閉
        
        切斷所有電源並開啟洩壓閥
        """
        logger.critical("🛑 執行緊急關閉程序...")
        
        # 切斷所有電源
        await self.io_driver.all_relays_off()
        
        # 開啟洩壓閥
        await self.io_driver.set_relays({
            1: True,  # 閥門 A
            2: True,  # 閥門 B
            3: False,
            4: False
        })
        
        logger.critical("✅ 緊急關閉程序已完成")

    def stop(self):
        """停止控制服務"""
        self._running = False
        self.io_driver.disconnect()
        logger.info("🛑 控制服務已停止")



