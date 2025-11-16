"""壓力計驅動測試"""
import pytest
import os
from pump_backend.drivers.pressure_sensor import PressureSensorDriver


@pytest.mark.asyncio
@pytest.mark.modbus
@pytest.mark.sensor
@pytest.mark.requires_simulator
class TestPressureSensor:
    """壓力計驅動測試類"""
    
    @pytest.fixture
    async def pressure_positive(self):
        """創建正壓計驅動實例"""
        os.environ["USE_SIMULATOR"] = "true"
        os.environ["MODBUS_SIMULATOR_HOST"] = "localhost"
        os.environ["PRESSURE_POSITIVE_TCP_PORT"] = "5025"
        
        driver = PressureSensorDriver("positive")
        yield driver
        await driver.disconnect_async()
    
    @pytest.fixture
    async def pressure_vacuum(self):
        """創建真空計驅動實例"""
        os.environ["USE_SIMULATOR"] = "true"
        os.environ["MODBUS_SIMULATOR_HOST"] = "localhost"
        os.environ["PRESSURE_VACUUM_TCP_PORT"] = "5026"
        
        driver = PressureSensorDriver("vacuum")
        yield driver
        await driver.disconnect_async()
    
    async def test_positive_pressure_read(self, pressure_positive):
        """測試正壓計讀取"""
        await pressure_positive.connect()
        
        pressure = await pressure_positive.read_pressure()
        
        assert pressure is not None, "應該能夠讀取壓力"
        assert isinstance(pressure, float), "壓力值應該是浮點數"
    
    async def test_vacuum_pressure_read(self, pressure_vacuum):
        """測試真空計讀取"""
        await pressure_vacuum.connect()
        
        pressure = await pressure_vacuum.read_pressure()
        
        assert pressure is not None, "應該能夠讀取壓力"
        assert isinstance(pressure, float), "壓力值應該是浮點數"
    
    async def test_pressure_kgcm2_conversion(self, pressure_positive):
        """測試壓力單位轉換"""
        await pressure_positive.connect()
        
        pressure_kgcm2 = await pressure_positive.read_pressure_kgcm2()
        
        assert pressure_kgcm2 is not None, "應該能夠讀取壓力（kg/cm²）"
        assert isinstance(pressure_kgcm2, float), "壓力值應該是浮點數"



