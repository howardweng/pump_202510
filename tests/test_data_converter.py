"""數據轉換器測試"""
import pytest
from pump_backend.utils.data_converter import (
    parse_int32,
    parse_uint32,
    parse_int16,
    parse_uint16
)


@pytest.mark.unit
class TestDataConverter:
    """數據轉換器測試類"""
    
    def test_parse_int32_positive(self):
        """測試解析正數 Int32"""
        registers = [0x0000, 0x0064]  # 100
        value = parse_int32(registers)
        assert value == 100, "應該正確解析正數"
    
    def test_parse_int32_negative(self):
        """測試解析負數 Int32"""
        registers = [0xFFFF, 0xFF9C]  # -100
        value = parse_int32(registers)
        assert value == -100, "應該正確解析負數"
    
    def test_parse_uint32(self):
        """測試解析 Unsigned Int32"""
        registers = [0x0001, 0x86A0]  # 100000
        value = parse_uint32(registers)
        assert value == 100000, "應該正確解析無符號整數"
    
    def test_parse_int16_positive(self):
        """測試解析正數 Int16"""
        value = parse_int16(100, signed=True)
        assert value == 100, "應該正確解析正數"
    
    def test_parse_int16_negative(self):
        """測試解析負數 Int16"""
        value = parse_int16(0xFF9C, signed=True)  # -100
        assert value == -100, "應該正確解析負數"
    
    def test_parse_uint16(self):
        """測試解析 Unsigned Int16"""
        value = parse_uint16(0x0064)
        assert value == 100, "應該正確解析無符號整數"

