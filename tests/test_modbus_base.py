"""MODBUS 基礎驅動測試"""
import pytest
import asyncio
from pymodbus.client import AsyncModbusTcpClient
from pump_backend.drivers.modbus_base import ModbusDevice
from pump_backend.models.device_health import DeviceHealth


@pytest.mark.asyncio
@pytest.mark.modbus
@pytest.mark.requires_simulator
class TestModbusBase:
    """MODBUS 基礎驅動測試類"""
    
    @pytest.fixture
    async def modbus_tcp_device(self, test_config):
        """創建 MODBUS TCP 設備實例"""
        device = ModbusDevice(
            port=test_config["modbus_simulator_host"],
            tcp_port=test_config["modbus_ports"]["flow_meter"],
            slave_id=1,
            use_tcp=True,
            timeout=1.0
        )
        yield device
        await device.disconnect_async()
    
    async def test_tcp_connection(self, modbus_tcp_device):
        """測試 TCP 連接"""
        result = await modbus_tcp_device.connect()
        assert result is True, "TCP 連接應該成功"
        assert modbus_tcp_device.connected is True, "設備應該標記為已連接"
        assert modbus_tcp_device.status.health == DeviceHealth.HEALTHY, "設備健康狀態應該是 HEALTHY"
    
    async def test_read_holding_registers(self, modbus_tcp_device):
        """測試讀取保持寄存器"""
        await modbus_tcp_device.connect()
        
        # 讀取流量計的瞬时流量寄存器（地址 0x0000）
        registers = await modbus_tcp_device.read_holding_registers(0x0000, 1)
        
        assert registers is not None, "讀取應該成功"
        assert len(registers) == 1, "應該讀取到 1 個寄存器"
        assert isinstance(registers[0], int), "寄存器值應該是整數"
    
    async def test_device_health_tracking(self, modbus_tcp_device):
        """測試設備健康狀態追蹤"""
        await modbus_tcp_device.connect()
        
        # 執行多次讀取
        for _ in range(5):
            await modbus_tcp_device.read_holding_registers(0x0000, 1)
        
        # 檢查健康狀態
        assert modbus_tcp_device.status.total_requests > 0, "應該有請求記錄"
        assert modbus_tcp_device.status.successful_requests > 0, "應該有成功記錄"
        assert modbus_tcp_device.status.get_success_rate() > 0, "成功率應該大於 0"
    
    async def test_connection_context_manager(self, test_config):
        """測試上下文管理器"""
        async with ModbusDevice(
            port=test_config["modbus_simulator_host"],
            tcp_port=test_config["modbus_ports"]["flow_meter"],
            slave_id=1,
            use_tcp=True
        ) as device:
            assert device.connected is True, "設備應該在上下文管理器中連接"
            registers = await device.read_holding_registers(0x0000, 1)
            assert registers is not None, "應該能夠讀取數據"



