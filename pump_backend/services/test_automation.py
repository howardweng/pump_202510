"""自動測試引擎"""
import asyncio
import time
from typing import Dict, Optional, Any
from loguru import logger
from core.mqtt_client import MQTTClient
from core.state_machine import StateMachine
from core.safety_monitor import SafetyMonitor
from services.control_service import ControlService
from services.sensor_service import SensorService
from services.data_logger import DataLogger
from models.enums import TestState, TestMode, PowerType, ValveState
from config.mqtt_topics import TEST_STATUS, TEST_RECORD, CONTROL_TEST


class TestAutomation:
    """
    自動測試引擎
    
    負責執行自動化測試流程
    使用狀態機管理測試狀態
    """

    def __init__(
        self,
        mqtt_client: MQTTClient,
        control_service: ControlService,
        sensor_service: SensorService,
        data_logger: Optional[DataLogger] = None
    ):
        self.mqtt = mqtt_client
        self.control = control_service
        self.sensors = sensor_service
        self.data_logger = data_logger
        
        self.state_machine = StateMachine()
        self._setup_state_handlers()
        
        self.current_test_config: Optional[Dict[str, Any]] = None
        self.test_start_time: Optional[float] = None
        self._running = False

    def _setup_state_handlers(self):
        """設置狀態處理器"""
        self.state_machine.register_handler(
            TestState.INITIALIZING,
            self._handle_initializing
        )
        self.state_machine.register_handler(
            TestState.READY,
            self._handle_ready
        )
        self.state_machine.register_handler(
            TestState.RUNNING,
            self._handle_running
        )
        self.state_machine.register_handler(
            TestState.PAUSED,
            self._handle_paused
        )
        self.state_machine.register_handler(
            TestState.COMPLETED,
            self._handle_completed
        )
        self.state_machine.register_handler(
            TestState.FAILED,
            self._handle_failed
        )
        self.state_machine.register_handler(
            TestState.STOPPED,
            self._handle_stopped
        )

    async def state_machine_loop(self):
        """
        狀態機迴圈
        
        監控狀態變化並執行相應操作
        """
        logger.info("🔄 自動測試引擎狀態機迴圈已啟動")
        
        # 訂閱測試控制命令
        self.mqtt.subscribe(CONTROL_TEST, self._handle_test_command)
        
        # 保持運行
        while self._running:
            await asyncio.sleep(0.1)

    async def _handle_test_command(self, payload: Dict):
        """
        處理測試命令
        
        命令格式:
        {
            "action": "start" | "stop" | "pause" | "resume" | "reset",
            "config": {...}  # 測試配置（start 時需要）
        }
        """
        try:
            action = payload.get("action", "").lower()
            
            if action == "start":
                config = payload.get("config", {})
                await self.start_test(config)
            elif action == "stop":
                await self.stop_test()
            elif action == "pause":
                await self.pause_test()
            elif action == "resume":
                await self.resume_test()
            elif action == "reset":
                self.reset_test()
            else:
                logger.warning(f"⚠️ 未知的測試命令: {action}")
                
        except Exception as e:
            logger.exception(f"❌ 處理測試命令異常: {e}")

    async def start_test(self, config: Dict[str, Any]):
        """
        開始測試
        
        Args:
            config: 測試配置
        """
        current_state = self.state_machine.get_state()
        
        if current_state not in [TestState.IDLE, TestState.READY]:
            logger.warning(
                f"⚠️ 無法開始測試，當前狀態: {current_state.value}"
            )
            return
        
        # 安全檢查
        from core.safety_monitor import SafetyMonitor
        if hasattr(self.control, 'safety'):
            safety: SafetyMonitor = self.control.safety
            can_proceed, error_msg = safety.check_start_conditions()
            if not can_proceed:
                logger.error(f"❌ 安全檢查失敗: {error_msg}")
                await self.mqtt.publish(TEST_STATUS, {
                    "status": "error",
                    "message": error_msg,
                    "state": current_state.value
                })
                return
        
        self.current_test_config = config
        await self.state_machine.transition_to(TestState.INITIALIZING, config)

    async def stop_test(self):
        """停止測試"""
        current_state = self.state_machine.get_state()
        
        if current_state in [TestState.RUNNING, TestState.PAUSED]:
            await self.state_machine.transition_to(TestState.STOPPED)
        else:
            logger.warning(f"⚠️ 無法停止測試，當前狀態: {current_state.value}")

    async def pause_test(self):
        """暫停測試"""
        current_state = self.state_machine.get_state()
        
        if current_state == TestState.RUNNING:
            await self.state_machine.transition_to(TestState.PAUSED)
        else:
            logger.warning(f"⚠️ 無法暫停測試，當前狀態: {current_state.value}")

    async def resume_test(self):
        """恢復測試"""
        current_state = self.state_machine.get_state()
        
        if current_state == TestState.PAUSED:
            await self.state_machine.transition_to(TestState.RUNNING)
        else:
            logger.warning(f"⚠️ 無法恢復測試，當前狀態: {current_state.value}")

    def reset_test(self):
        """重置測試"""
        self.state_machine.reset()
        self.current_test_config = None
        self.test_start_time = None
        logger.info("🔄 測試已重置")

    async def _handle_initializing(self, context: Optional[Dict] = None):
        """處理初始化狀態"""
        logger.info("🔧 測試初始化中...")
        
        try:
            # 1. 檢查所有感測器連線狀態
            sensor_status = {
                "flow_meter": self.sensors.flow_meter.connected if hasattr(self.sensors.flow_meter, 'connected') else False,
                "pressure_positive": self.sensors.pressure_positive.connected if hasattr(self.sensors.pressure_positive, 'connected') else False,
                "pressure_vacuum": self.sensors.pressure_vacuum.connected if hasattr(self.sensors.pressure_vacuum, 'connected') else False,
            }
            
            connected_sensors = [name for name, status in sensor_status.items() if status]
            if not connected_sensors:
                logger.warning("⚠️ 沒有感測器連線，但繼續初始化")
            else:
                logger.info(f"✅ 感測器連線狀態: {', '.join(connected_sensors)}")
            
            # 2. 檢查控制服務連線狀態
            control_ready = self.control.io_driver.connected if hasattr(self.control.io_driver, 'connected') else False
            if not control_ready:
                logger.warning("⚠️ 控制服務未就緒，但繼續初始化")
            else:
                logger.info("✅ 控制服務已就緒")
            
            # 3. 設定測試參數（從 context 中讀取）
            if context:
                self.current_test_config = context
                logger.info(f"📋 測試配置已載入: {context.get('test_id', 'N/A')}")
            
            # 4. 準備數據記錄
            if self.data_logger:
                test_id = context.get("test_id", f"test_{int(time.time())}") if context else f"test_{int(time.time())}"
                self.data_logger.start_test_logging(test_id)
                logger.info(f"📝 數據記錄已準備: {test_id}")
            
            await asyncio.sleep(0.5)  # 初始化完成延遲
            
            await self.state_machine.transition_to(TestState.READY)
            
        except Exception as e:
            logger.exception(f"❌ 初始化失敗: {e}")
            await self.state_machine.transition_to(TestState.FAILED, {"error": str(e)})

    async def _handle_ready(self, context: Optional[Dict] = None):
        """處理準備就緒狀態"""
        logger.info("✅ 測試準備就緒")
        
        await self.mqtt.publish(TEST_STATUS, {
            "state": TestState.READY.value,
            "message": "測試準備就緒，等待開始"
        })
        
        # 自動開始測試（如果配置了自動模式）
        if context and context.get("auto_start", False):
            await asyncio.sleep(1.0)
            await self.state_machine.transition_to(TestState.RUNNING)

    async def _handle_running(self, context: Optional[Dict] = None):
        """處理運行狀態"""
        logger.info("▶️ 測試運行中...")
        
        self.test_start_time = time.time()
        
        await self.mqtt.publish(TEST_STATUS, {
            "state": TestState.RUNNING.value,
            "message": "測試運行中",
            "start_time": self.test_start_time
        })
        
        # 執行測試流程
        try:
            config = context or self.current_test_config or {}
            
            # 1. 根據配置啟動電源（如果需要）
            if config.get("power_on"):
                power_type = config.get("power_type", "dc")
                logger.info(f"🔌 啟動電源: {power_type}")
                # 電源控制通過控制服務的 MQTT 命令處理，這裡只記錄日誌
            
            # 2. 根據配置控制閥門（如果需要）
            if config.get("valve_state"):
                valve_state = config.get("valve_state")
                logger.info(f"🚰 設定閥門狀態: {valve_state}")
                # 閥門控制通過控制服務的 MQTT 命令處理，這裡只記錄日誌
            
            # 3. 監控數據並記錄結果
            # 數據記錄由數據記錄器自動從 MQTT 接收並記錄
            logger.info("📊 開始監控感測器數據...")
            
            # 4. 運行指定時長或直到手動停止
            duration = config.get("duration", 60)  # 預設 60 秒
            
            if duration > 0:
                logger.info(f"⏱️ 測試將運行 {duration} 秒")
                elapsed = 0
                check_interval = 1.0  # 每秒檢查一次
                
                while elapsed < duration and self._running:
                    await asyncio.sleep(check_interval)
                    elapsed += check_interval
                    
                    # 定期發布狀態更新
                    if int(elapsed) % 10 == 0:  # 每 10 秒更新一次
                        await self.mqtt.publish(TEST_STATUS, {
                            "state": TestState.RUNNING.value,
                            "message": f"測試運行中 ({int(elapsed)}/{duration} 秒)",
                            "elapsed": elapsed,
                            "duration": duration
                        })
                
                if elapsed >= duration:
                    logger.info("✅ 測試時長已達到，完成測試")
                    await self.state_machine.transition_to(TestState.COMPLETED)
            else:
                # 無時長限制，等待手動停止
                logger.info("⏸️ 測試運行中（無時長限制，等待手動停止）")
                while self._running:
                    await asyncio.sleep(1.0)
                    
        except Exception as e:
            logger.exception(f"❌ 測試運行異常: {e}")
            await self.state_machine.transition_to(TestState.FAILED, {"error": str(e)})

    async def _handle_paused(self, context: Optional[Dict] = None):
        """處理暫停狀態"""
        logger.info("⏸️ 測試已暫停")
        
        await self.mqtt.publish(TEST_STATUS, {
            "state": TestState.PAUSED.value,
            "message": "測試已暫停"
        })

    async def _handle_completed(self, context: Optional[Dict] = None):
        """處理完成狀態"""
        logger.info("✅ 測試完成")
        
        test_duration = None
        if self.test_start_time:
            test_duration = time.time() - self.test_start_time
        
        # 停止數據記錄
        if self.data_logger:
            self.data_logger.stop_test_logging()
        
        await self.mqtt.publish(TEST_STATUS, {
            "state": TestState.COMPLETED.value,
            "message": "測試完成",
            "duration": test_duration
        })
        
        # 自動重置（可選）
        await asyncio.sleep(2.0)
        await self.state_machine.transition_to(TestState.IDLE)

    async def _handle_failed(self, context: Optional[Dict] = None):
        """處理失敗狀態"""
        logger.error("❌ 測試失敗")
        
        # 停止數據記錄
        if self.data_logger:
            self.data_logger.stop_test_logging()
        
        await self.mqtt.publish(TEST_STATUS, {
            "state": TestState.FAILED.value,
            "message": "測試失敗",
            "error": context.get("error") if context else None
        })

    async def _handle_stopped(self, context: Optional[Dict] = None):
        """處理停止狀態"""
        logger.info("🛑 測試已停止")
        
        # 執行緊急停止
        await self.control.emergency_shutdown()
        
        # 停止數據記錄
        if self.data_logger:
            self.data_logger.stop_test_logging()
        
        await self.mqtt.publish(TEST_STATUS, {
            "state": TestState.STOPPED.value,
            "message": "測試已停止"
        })
        
        # 自動重置
        await asyncio.sleep(1.0)
        await self.state_machine.transition_to(TestState.IDLE)

    def start(self):
        """啟動自動測試引擎"""
        self._running = True
        logger.info("✅ 自動測試引擎已啟動")

    def stop(self):
        """停止自動測試引擎"""
        self._running = False
        self.reset_test()
        logger.info("🛑 自動測試引擎已停止")

