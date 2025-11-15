"""繼電器 IO 驅動測試"""
import pytest
import os
from pump_backend.drivers.relay_io import RelayIODriver


@pytest.mark.asyncio
@pytest.mark.modbus
@pytest.mark.control
@pytest.mark.requires_simulator
class TestRelayIO:
    """繼電器 IO 驅動測試類"""
    
    @pytest.fixture
    async def relay_io(self):
        """創建繼電器 IO 驅動實例"""
        os.environ["USE_SIMULATOR"] = "true"
        os.environ["MODBUS_SIMULATOR_HOST"] = "localhost"
        os.environ["RELAY_IO_TCP_PORT"] = "5027"
        
        driver = RelayIODriver()
        yield driver
        # 清理：關閉所有繼電器
        await driver.all_relays_off()
        await driver.disconnect_async()
    
    async def test_connect(self, relay_io):
        """測試連接"""
        result = await relay_io.connect()
        assert result is True, "繼電器 IO 應該能夠連接"
    
    async def test_set_relay(self, relay_io):
        """測試設定單個繼電器"""
        await relay_io.connect()
        
        # 測試開啟 CH1
        result = await relay_io.set_relay(1, True)
        assert result is True, "應該能夠設定繼電器"
        
        # 測試關閉 CH1
        result = await relay_io.set_relay(1, False)
        assert result is True, "應該能夠關閉繼電器"
    
    async def test_set_relays(self, relay_io):
        """測試設定多個繼電器"""
        await relay_io.connect()
        
        # 設定多個繼電器
        states = {1: True, 2: False, 3: True, 4: False}
        result = await relay_io.set_relays(states)
        assert result is True, "應該能夠設定多個繼電器"
    
    async def test_all_relays_off(self, relay_io):
        """測試關閉所有繼電器"""
        await relay_io.connect()
        
        result = await relay_io.all_relays_off()
        assert result is True, "應該能夠關閉所有繼電器"
    
    async def test_read_digital_inputs(self, relay_io):
        """測試讀取數位輸入"""
        await relay_io.connect()
        
        inputs = await relay_io.read_digital_inputs()
        
        assert inputs is not None, "應該能夠讀取數位輸入"
        assert isinstance(inputs, int), "輸入值應該是整數"
        assert 0 <= inputs <= 255, "輸入值應該在 0-255 範圍內"

