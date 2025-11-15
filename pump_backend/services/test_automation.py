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
            # TODO: 執行初始化操作
            # 1. 檢查所有感測器連線
            # 2. 設定測試參數
            # 3. 準備數據記錄
            
            # 開始數據記錄
            if self.data_logger:
                test_id = context.get("test_id", f"test_{int(time.time())}")
                self.data_logger.start_test_logging(test_id)
            
            await asyncio.sleep(0.5)  # 模擬初始化時間
            
            await self.state_machine.transition_to(TestState.READY)
            
        except Exception as e:
            logger.exception(f"❌ 初始化失敗: {e}")
            await self.state_machine.transition_to(TestState.FAILED)

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
        
        # TODO: 執行測試流程
        # 這裡應該根據測試配置執行具體的測試步驟
        # 例如：啟動電源、監控數據、記錄結果等
        
        # 暫時：運行一段時間後自動完成
        if context and context.get("duration"):
            duration = context.get("duration", 60)
            await asyncio.sleep(duration)
            await self.state_machine.transition_to(TestState.COMPLETED)

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

