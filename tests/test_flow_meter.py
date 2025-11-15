"""流量計驅動測試"""
import pytest
import os
from pump_backend.drivers.flow_meter import FlowMeterDriver


@pytest.mark.asyncio
@pytest.mark.modbus
@pytest.mark.sensor
@pytest.mark.requires_simulator
class TestFlowMeter:
    """流量計驅動測試類"""
    
    @pytest.fixture
    async def flow_meter(self):
        """創建流量計驅動實例"""
        # 設置環境變數以使用 TCP
        os.environ["USE_SIMULATOR"] = "true"
        os.environ["MODBUS_SIMULATOR_HOST"] = "localhost"
        os.environ["FLOW_METER_TCP_PORT"] = "5020"
        
        driver = FlowMeterDriver()
        yield driver
        await driver.disconnect_async()
    
    async def test_connect(self, flow_meter):
        """測試連接"""
        result = await flow_meter.connect()
        assert result is True, "流量計應該能夠連接"
    
    async def test_read_instantaneous_flow(self, flow_meter):
        """測試讀取瞬时流量"""
        await flow_meter.connect()
        
        flow = await flow_meter.read_instantaneous_flow()
        
        assert flow is not None, "應該能夠讀取瞬时流量"
        assert isinstance(flow, float), "流量值應該是浮點數"
        assert flow >= 0, "流量值應該 >= 0"
    
    async def test_read_cumulative_flow(self, flow_meter):
        """測試讀取累積流量"""
        await flow_meter.connect()
        
        cumulative = await flow_meter.read_cumulative_flow()
        
        assert cumulative is not None, "應該能夠讀取累積流量"
        assert isinstance(cumulative, float), "累積流量值應該是浮點數"
        assert cumulative >= 0, "累積流量值應該 >= 0"
    
    async def test_read_all(self, flow_meter):
        """測試讀取所有數據"""
        await flow_meter.connect()
        
        data = await flow_meter.read_all()
        
        assert data is not None, "應該能夠讀取所有數據"
        assert "instantaneous_flow" in data, "應該包含瞬时流量"
        assert "cumulative_flow" in data, "應該包含累積流量"

