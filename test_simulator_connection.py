#!/usr/bin/env python3
"""測試模擬器連接"""
import asyncio
from pymodbus.client import AsyncModbusTcpClient

async def test_simulator():
    """測試模擬器連接"""
    print("🔍 測試模擬器連接...")
    
    # 測試流量計（端口 5020, Slave ID 1）
    try:
        client = AsyncModbusTcpClient(host='localhost', port=5020)
        await client.connect()
        
        if client.is_socket_open():
            print("✅ 已連接到模擬器 (端口 5020)")
            
            # 讀取寄存器 0x0000 (瞬时流量)
            result = await client.read_holding_registers(address=0x0000, count=1, slave=1)
            if not result.isError():
                print(f"✅ 讀取成功: 寄存器值 = {result.registers}")
            else:
                print(f"❌ 讀取失敗: {result}")
        else:
            print("❌ 無法連接到模擬器")
        
        client.close()
    except Exception as e:
        print(f"❌ 連接錯誤: {e}")

if __name__ == "__main__":
    asyncio.run(test_simulator())

