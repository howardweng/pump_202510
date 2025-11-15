"""電表驅動 (JX3101 單相 / JX8304M 三相)"""
from typing import Optional, Dict
from loguru import logger
from .modbus_base import ModbusDevice
from config.modbus_devices import get_device_config


def parse_int32(registers: list) -> int:
    """
    解析 Signed Int32 (2 個寄存器，Big-Endian)
    
    Args:
        registers: 2 個寄存器的列表
        
    Returns:
        Signed Int32 值
    """
    if len(registers) < 2:
        return 0
    
    # Big-Endian: 高位在前
    value = (registers[0] << 16) | registers[1]
    
    # 轉換為有符號整數
    if value & 0x80000000:
        value = value - 0x100000000
    
    return value


class SinglePhasePowerMeterDriver(ModbusDevice):
    """
    單相電表驅動 - JX3101 系列
    
    規格：
    - 所有參數都是 Signed Int32 (2 個寄存器)
    - 電壓: 係數 0.01 (除法)
    - 電流: 係數 0.001 (除法)
    - 功率: 係數 0.01 (除法)
    """

    def __init__(self, meter_type: str = "dc"):
        """
        Args:
            meter_type: "dc", "ac110", "ac220"
        """
        config_map = {
            "dc": "dc_meter",
            "ac110": "ac110v_meter",
            "ac220": "ac220v_meter"
        }
        config_key = config_map.get(meter_type, "dc_meter")
        config = get_device_config()[config_key]
        
        super().__init__(
            port=config["port"],
            baudrate=config["baudrate"],
            parity=config["parity"],
            stopbits=config["stopbits"],
            bytesize=config["bytesize"],
            slave_id=config["slave_id"],
            timeout=config["timeout"]
        )
        self.meter_type = meter_type

    async def read_voltage(self) -> Optional[float]:
        """
        讀取電壓
        
        Returns:
            電壓 (V)，失敗返回 None
        """
        registers = await self.read_holding_registers(0x0000, 2)
        if registers is None or len(registers) < 2:
            return None
        
        raw_value = parse_int32(registers)
        voltage = raw_value / 100.0  # 係數 0.01
        
        logger.debug(f"📊 {self.meter_type} 電壓: {voltage:.2f} V (原始值: {raw_value})")
        return voltage

    async def read_current(self) -> Optional[float]:
        """
        讀取電流
        
        Returns:
            電流 (A)，失敗返回 None
        """
        registers = await self.read_holding_registers(0x0002, 2)
        if registers is None or len(registers) < 2:
            return None
        
        raw_value = parse_int32(registers)
        current = raw_value / 1000.0  # 係數 0.001
        
        logger.debug(f"📊 {self.meter_type} 電流: {current:.3f} A (原始值: {raw_value})")
        return current

    async def read_active_power(self) -> Optional[float]:
        """
        讀取有功功率
        
        Returns:
            功率 (W)，失敗返回 None
        """
        registers = await self.read_holding_registers(0x0004, 2)
        if registers is None or len(registers) < 2:
            return None
        
        raw_value = parse_int32(registers)
        power = raw_value / 100.0  # 係數 0.01
        
        logger.debug(f"📊 {self.meter_type} 有功功率: {power:.2f} W (原始值: {raw_value})")
        return power

    async def read_reactive_power(self) -> Optional[float]:
        """
        讀取無功功率
        
        Returns:
            無功功率 (VAR)，失敗返回 None
        """
        registers = await self.read_holding_registers(0x0006, 2)
        if registers is None or len(registers) < 2:
            return None
        
        raw_value = parse_int32(registers)
        reactive = raw_value / 100.0  # 係數 0.01
        
        logger.debug(f"📊 {self.meter_type} 無功功率: {reactive:.2f} VAR (原始值: {raw_value})")
        return reactive

    async def read_all(self) -> Optional[Dict[str, float]]:
        """
        讀取所有數據
        
        Returns:
            包含所有電氣參數的字典，失敗返回 None
        """
        voltage = await self.read_voltage()
        current = await self.read_current()
        active_power = await self.read_active_power()
        reactive_power = await self.read_reactive_power()
        
        if all(v is None for v in [voltage, current, active_power, reactive_power]):
            return None
        
        return {
            "voltage": voltage,
            "current": current,
            "active_power": active_power,
            "reactive_power": reactive_power
        }


class ThreePhasePowerMeterDriver(ModbusDevice):
    """
    三相電表驅動 - JX8304M
    
    規格：
    - 所有參數都是 Signed Int32 (2 個寄存器)
    - 電壓: 係數 0.01 (除法)
    - 電流: 係數 0.001 (除法)
    - 功率: 係數 0.01 (除法)
    """

    def __init__(self):
        config = get_device_config()["ac220v_3p_meter"]
        super().__init__(
            port=config["port"],
            baudrate=config["baudrate"],
            parity=config["parity"],
            stopbits=config["stopbits"],
            bytesize=config["bytesize"],
            slave_id=config["slave_id"],
            timeout=config["timeout"]
        )

    async def read_voltage_phase(self, phase: str) -> Optional[float]:
        """
        讀取相電壓
        
        Args:
            phase: "A", "B", "C"
            
        Returns:
            相電壓 (V)，失敗返回 None
        """
        phase_map = {"A": 0x0000, "B": 0x0002, "C": 0x0004}
        address = phase_map.get(phase.upper(), 0x0000)
        
        registers = await self.read_holding_registers(address, 2)
        if registers is None or len(registers) < 2:
            return None
        
        raw_value = parse_int32(registers)
        voltage = raw_value / 100.0  # 係數 0.01
        
        logger.debug(f"📊 相{phase} 電壓: {voltage:.2f} V (原始值: {raw_value})")
        return voltage

    async def read_current_phase(self, phase: str) -> Optional[float]:
        """
        讀取相電流
        
        Args:
            phase: "A", "B", "C"
            
        Returns:
            相電流 (A)，失敗返回 None
        """
        phase_map = {"A": 0x0006, "B": 0x0008, "C": 0x000A}
        address = phase_map.get(phase.upper(), 0x0006)
        
        registers = await self.read_holding_registers(address, 2)
        if registers is None or len(registers) < 2:
            return None
        
        raw_value = parse_int32(registers)
        current = raw_value / 1000.0  # 係數 0.001
        
        logger.debug(f"📊 相{phase} 電流: {current:.3f} A (原始值: {raw_value})")
        return current

    async def read_total_active_power(self) -> Optional[float]:
        """
        讀取合相有功功率
        
        Returns:
            合相有功功率 (W)，失敗返回 None
        """
        registers = await self.read_holding_registers(0x000C, 2)
        if registers is None or len(registers) < 2:
            return None
        
        raw_value = parse_int32(registers)
        power = raw_value / 100.0  # 係數 0.01
        
        logger.debug(f"📊 合相有功功率: {power:.2f} W (原始值: {raw_value})")
        return power

    async def read_all(self) -> Optional[Dict[str, float]]:
        """
        讀取所有數據
        
        Returns:
            包含所有三相電氣參數的字典，失敗返回 None
        """
        va = await self.read_voltage_phase("A")
        vb = await self.read_voltage_phase("B")
        vc = await self.read_voltage_phase("C")
        ia = await self.read_current_phase("A")
        ib = await self.read_current_phase("B")
        ic = await self.read_current_phase("C")
        total_power = await self.read_total_active_power()
        
        if all(v is None for v in [va, vb, vc, ia, ib, ic, total_power]):
            return None
        
        return {
            "voltage_a": va,
            "voltage_b": vb,
            "voltage_c": vc,
            "current_a": ia,
            "current_b": ib,
            "current_c": ic,
            "total_active_power": total_power
        }

