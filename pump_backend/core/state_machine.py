"""測試狀態機"""
from enum import Enum
from typing import Optional, Callable, Dict, Any
from loguru import logger
from pump_backend.models.enums import TestState


class StateMachine:
    """
    測試狀態機
    
    管理測試流程的狀態轉換
    """

    def __init__(self):
        self.current_state = TestState.IDLE
        self.previous_state: Optional[TestState] = None
        self.state_handlers: Dict[TestState, Callable] = {}
        self.transition_history = []

    def register_handler(self, state: TestState, handler: Callable):
        """
        註冊狀態處理器
        
        Args:
            state: 狀態
            handler: 處理函數（async）
        """
        self.state_handlers[state] = handler
        logger.debug(f"📝 註冊狀態處理器: {state.value}")

    async def transition_to(self, new_state: TestState, context: Optional[Dict[str, Any]] = None):
        """
        轉換到新狀態
        
        Args:
            new_state: 新狀態
            context: 狀態轉換上下文
        """
        if new_state == self.current_state:
            logger.debug(f"⏭️ 狀態未變更: {new_state.value}")
            return
        
        # 檢查狀態轉換是否合法
        if not self._can_transition(self.current_state, new_state):
            logger.warning(
                f"⚠️ 非法狀態轉換: {self.current_state.value} -> {new_state.value}"
            )
            return
        
        self.previous_state = self.current_state
        self.current_state = new_state
        
        # 記錄轉換歷史
        self.transition_history.append({
            "from": self.previous_state.value,
            "to": new_state.value,
            "context": context or {}
        })
        
        logger.info(
            f"🔄 狀態轉換: {self.previous_state.value} -> {new_state.value}"
        )
        
        # 執行狀態處理器
        if new_state in self.state_handlers:
            try:
                handler = self.state_handlers[new_state]
                if callable(handler):
                    if hasattr(handler, '__call__'):
                        if hasattr(handler, '__code__') and 'await' in str(handler.__code__.co_code):
                            await handler(context)
                        else:
                            handler(context)
            except Exception as e:
                logger.exception(f"❌ 狀態處理器執行失敗 [{new_state.value}]: {e}")

    def _can_transition(self, from_state: TestState, to_state: TestState) -> bool:
        """
        檢查狀態轉換是否合法
        
        Args:
            from_state: 當前狀態
            to_state: 目標狀態
            
        Returns:
            是否允許轉換
        """
        # 定義合法的狀態轉換
        valid_transitions = {
            TestState.IDLE: [TestState.INITIALIZING, TestState.READY],
            TestState.INITIALIZING: [TestState.READY, TestState.IDLE, TestState.FAILED],
            TestState.READY: [TestState.RUNNING, TestState.IDLE],
            TestState.RUNNING: [
                TestState.PAUSED,
                TestState.COMPLETED,
                TestState.FAILED,
                TestState.STOPPED
            ],
            TestState.PAUSED: [TestState.RUNNING, TestState.STOPPED, TestState.IDLE],
            TestState.COMPLETED: [TestState.IDLE, TestState.READY],
            TestState.FAILED: [TestState.IDLE, TestState.READY],
            TestState.STOPPED: [TestState.IDLE, TestState.READY]
        }
        
        allowed = valid_transitions.get(from_state, [])
        return to_state in allowed

    def get_state(self) -> TestState:
        """獲取當前狀態"""
        return self.current_state

    def reset(self):
        """重置狀態機"""
        self.previous_state = None
        self.current_state = TestState.IDLE
        logger.info("🔄 狀態機已重置")

