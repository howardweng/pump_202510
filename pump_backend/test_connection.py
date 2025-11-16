#!/usr/bin/env python3
"""快速連接測試腳本"""
import asyncio
import sys
from loguru import logger

# 配置日誌
logger.remove()
logger.add(sys.stdout, level="INFO", colorize=True)


async def test_mqtt():
    """測試 MQTT 連接"""
    logger.info("🔍 測試 MQTT 連接...")
    try:
        from aiomqtt import Client
        
        async with Client("localhost", 1883) as client:
            await client.publish("test/connection", "Hello from backend test")
            logger.info("✅ MQTT 連接成功")
            return True
    except Exception as e:
        logger.error(f"❌ MQTT 連接失敗: {e}")
        return False


async def test_modbus_tcp():
    """測試 Modbus TCP 連接（模擬器）"""
    logger.info("🔍 測試 Modbus TCP 連接（模擬器）...")
    try:
        from pymodbus.client import AsyncModbusTcpClient
        
        # 測試流量計（端口 5020）
        client = AsyncModbusTcpClient('localhost', port=5020)
        await client.connect()
        
        if not client.connected:
            logger.error("❌ Modbus TCP 連接失敗：未連接")
            return False
        
        # 讀取一個寄存器
        result = await client.read_holding_registers(0, 1, slave=1)
        
        if result.isError():
            logger.error(f"❌ Modbus TCP 讀取失敗: {result}")
            client.close()
            return False
        
        logger.info(f"✅ Modbus TCP 連接成功，讀取值: {result.registers}")
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Modbus TCP 連接失敗: {e}")
        return False


async def test_postgres():
    """測試 PostgreSQL 連接"""
    logger.info("🔍 測試 PostgreSQL 連接...")
    try:
        import asyncpg
        
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='pump_user',
            password='pump_password_change_me',
            database='pump_testing'
        )
        
        version = await conn.fetchval('SELECT version()')
        logger.info(f"✅ PostgreSQL 連接成功: {version[:50]}...")
        await conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL 連接失敗: {e}")
        logger.info("💡 提示: 請檢查 .env 文件中的資料庫配置")
        return False


async def main():
    """主測試函數"""
    logger.info("🚀 開始後端連接測試...\n")
    
    results = {
        "MQTT": await test_mqtt(),
        "Modbus TCP": await test_modbus_tcp(),
        "PostgreSQL": await test_postgres()
    }
    
    logger.info("\n" + "="*50)
    logger.info("📊 測試結果總結:")
    logger.info("="*50)
    
    for service, success in results.items():
        status = "✅ 通過" if success else "❌ 失敗"
        logger.info(f"  {service:15} {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        logger.info("\n✅ 所有連接測試通過！可以啟動後端服務。")
        return 0
    else:
        logger.warning("\n⚠️ 部分連接測試失敗，請檢查配置和服務狀態。")
        logger.info("\n💡 提示:")
        logger.info("  1. 確保 Docker 服務運行: docker compose ps")
        logger.info("  2. 檢查 .env 文件配置")
        logger.info("  3. 查看詳細錯誤訊息")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n⏸️ 測試中斷")
        sys.exit(1)



