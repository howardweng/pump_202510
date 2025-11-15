"""狀態機測試"""
import pytest
from pump_backend.core.state_machine import StateMachine
from pump_backend.models.enums import TestState


@pytest.mark.unit
class TestStateMachine:
    """狀態機測試類"""
    
    @pytest.fixture
    def state_machine(self):
        """創建狀態機實例"""
        return StateMachine()
    
    def test_initial_state(self, state_machine):
        """測試初始狀態"""
        assert state_machine.get_state() == TestState.IDLE, "初始狀態應該是 IDLE"
    
    def test_valid_transition(self, state_machine):
        """測試合法狀態轉換"""
        import asyncio
        
        async def test():
            await state_machine.transition_to(TestState.INITIALIZING)
            assert state_machine.get_state() == TestState.INITIALIZING, "應該能夠轉換到 INITIALIZING"
        
        asyncio.run(test())
    
    def test_invalid_transition(self, state_machine):
        """測試非法狀態轉換"""
        import asyncio
        
        async def test():
            # IDLE 不能直接轉換到 RUNNING
            await state_machine.transition_to(TestState.RUNNING)
            # 應該保持在 IDLE
            assert state_machine.get_state() == TestState.IDLE, "非法轉換應該被拒絕"
        
        asyncio.run(test())
    
    def test_state_handler(self, state_machine):
        """測試狀態處理器"""
        import asyncio
        handler_called = []
        
        def handler(context):
            handler_called.append(True)
        
        state_machine.register_handler(TestState.READY, handler)
        
        async def test():
            await state_machine.transition_to(TestState.INITIALIZING)
            await state_machine.transition_to(TestState.READY)
            # 處理器應該被調用
            assert len(handler_called) > 0, "狀態處理器應該被調用"
        
        asyncio.run(test())
    
    def test_reset(self, state_machine):
        """測試重置狀態機"""
        import asyncio
        
        async def test():
            await state_machine.transition_to(TestState.INITIALIZING)
            state_machine.reset()
            assert state_machine.get_state() == TestState.IDLE, "重置後應該回到 IDLE"
        
        asyncio.run(test())

