"""電表驅動測試"""
import pytest
import os
from pump_backend.drivers.power_meter import (
    SinglePhasePowerMeterDriver,
    ThreePhasePowerMeterDriver
)


@pytest.mark.asyncio
@pytest.mark.modbus
@pytest.mark.sensor
@pytest.mark.requires_simulator
class TestPowerMeter:
    """電表驅動測試類"""
    
    @pytest.fixture
    async def dc_meter(self):
        """創建 DC 電表驅動實例"""
        os.environ["USE_SIMULATOR"] = "true"
        os.environ["MODBUS_SIMULATOR_HOST"] = "localhost"
        os.environ["DC_METER_TCP_PORT"] = "5021"
        
        driver = SinglePhasePowerMeterDriver("dc")
        yield driver
        await driver.disconnect_async()
    
    @pytest.fixture
    async def ac220v_3p_meter(self):
        """創建 AC220V 3P 電表驅動實例"""
        os.environ["USE_SIMULATOR"] = "true"
        os.environ["MODBUS_SIMULATOR_HOST"] = "localhost"
        os.environ["AC220V_3P_METER_TCP_PORT"] = "5024"
        
        driver = ThreePhasePowerMeterDriver()
        yield driver
        await driver.disconnect_async()
    
    async def test_dc_meter_read_voltage(self, dc_meter):
        """測試 DC 電表讀取電壓"""
        await dc_meter.connect()
        
        voltage = await dc_meter.read_voltage()
        
        assert voltage is not None, "應該能夠讀取電壓"
        assert isinstance(voltage, float), "電壓值應該是浮點數"
    
    async def test_dc_meter_read_current(self, dc_meter):
        """測試 DC 電表讀取電流"""
        await dc_meter.connect()
        
        current = await dc_meter.read_current()
        
        assert current is not None, "應該能夠讀取電流"
        assert isinstance(current, float), "電流值應該是浮點數"
    
    async def test_dc_meter_read_all(self, dc_meter):
        """測試 DC 電表讀取所有參數"""
        await dc_meter.connect()
        
        data = await dc_meter.read_all()
        
        assert data is not None, "應該能夠讀取所有數據"
        assert "voltage" in data, "應該包含電壓"
        assert "current" in data, "應該包含電流"
        assert "active_power" in data, "應該包含有功功率"
    
    async def test_3p_meter_read_all(self, ac220v_3p_meter):
        """測試三相電表讀取所有參數"""
        await ac220v_3p_meter.connect()
        
        data = await ac220v_3p_meter.read_all()
        
        assert data is not None, "應該能夠讀取所有數據"
        assert "voltage_a" in data, "應該包含 A 相電壓"
        assert "voltage_b" in data, "應該包含 B 相電壓"
        assert "voltage_c" in data, "應該包含 C 相電壓"
        assert "total_active_power" in data, "應該包含合相功率"



