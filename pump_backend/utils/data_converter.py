"""數據轉換工具"""
from typing import List


def parse_int32(registers: List[int]) -> int:
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


def parse_uint32(registers: List[int]) -> int:
    """
    解析 Unsigned Int32 (2 個寄存器，Big-Endian)
    
    Args:
        registers: 2 個寄存器的列表
        
    Returns:
        Unsigned Int32 值
    """
    if len(registers) < 2:
        return 0
    
    # Big-Endian: 高位在前
    value = (registers[0] << 16) | registers[1]
    return value


def parse_int16(register: int, signed: bool = True) -> int:
    """
    解析 Int16
    
    Args:
        register: 寄存器值
        signed: 是否為有符號整數
        
    Returns:
        Int16 值
    """
    if signed:
        # 轉換為有符號整數
        if register & 0x8000:
            return register - 0x10000
    return register


def parse_uint16(register: int) -> int:
    """
    解析 Unsigned Int16
    
    Args:
        register: 寄存器值
        
    Returns:
        Unsigned Int16 值
    """
    return register & 0xFFFF



