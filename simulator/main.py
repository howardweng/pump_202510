"""MODBUS 模擬器主程序"""
import asyncio
import signal
import os
import sys
from loguru import logger
from devices import (
    FlowMeterSimulator,
    PressureSensorSimulator,
    SinglePhasePowerMeterSimulator,
    ThreePhasePowerMeterSimulator,
    RelayIOSimulator
)

# 配置日誌
log_level = os.getenv("LOG_LEVEL", "INFO")
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=log_level,
    colorize=True
)

# 全域停止旗標
shutdown_event = asyncio.Event()

def signal_handler(sig, frame):
    """處理 Ctrl+C 信號"""
    logger.info("⏸️ 收到中斷信號，準備關閉...")
    shutdown_event.set()


async def main():
    """主程序"""
    logger.info("🚀 MODBUS 設備模擬器啟動中...")
    
    # 註冊信號處理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 創建所有設備模擬器
    # 根據 MODBUS_all_devices.md 和 SIMULATOR_ARCHITECTURE.md
    simulators = [
        # 流量計 (Slave ID 1, Port 5020)
        FlowMeterSimulator(slave_id=1, port=5020),
        
        # 電表 (4台)
        SinglePhasePowerMeterSimulator(slave_id=1, port=5021, meter_type="DC"),
        SinglePhasePowerMeterSimulator(slave_id=2, port=5022, meter_type="AC110V"),
        SinglePhasePowerMeterSimulator(slave_id=3, port=5023, meter_type="AC220V"),
        ThreePhasePowerMeterSimulator(slave_id=4, port=5024),
        
        # 壓力計 (2台)
        PressureSensorSimulator(slave_id=2, port=5025, is_vacuum=False),  # 正壓
        PressureSensorSimulator(slave_id=3, port=5026, is_vacuum=True),   # 真空
        
        # 繼電器 IO 模組 (Slave ID 1, Port 5027)
        RelayIOSimulator(slave_id=1, port=5027),
    ]
    
    # 啟動所有模擬器
    tasks = []
    for sim in simulators:
        task = asyncio.create_task(sim.start())
        tasks.append(task)
    
    logger.info(f"✅ 已啟動 {len(simulators)} 台設備模擬器")
    
    try:
        # 等待停止信號
        await shutdown_event.wait()
    except KeyboardInterrupt:
        logger.info("⏸️ 收到中斷信號，正在關閉模擬器...")
    except Exception as e:
        logger.exception(f"❌ 系統異常: {e}")
    finally:
        # 停止所有模擬器
        logger.info("🛑 正在停止所有模擬器...")
        stop_tasks = [sim.stop() for sim in simulators]
        await asyncio.gather(*stop_tasks, return_exceptions=True)
        logger.info("✅ 所有模擬器已停止")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 模擬器已關閉")

