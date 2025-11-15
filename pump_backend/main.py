"""應用程式入口點"""
import asyncio
import signal
import sys
from loguru import logger
from config.settings import settings

# 配置日誌
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
    colorize=True
)
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    level=settings.LOG_LEVEL
)

# 全域停止旗標
shutdown_event = asyncio.Event()


def signal_handler(sig, frame):
    """處理 Ctrl+C 信號"""
    logger.info("⏸️ 收到中斷信號，準備關閉...")
    shutdown_event.set()


async def main():
    """主程序"""
    logger.info("🚀 幫浦測試平台後端啟動中...")
    logger.info(f"📋 配置: MQTT={settings.MQTT_BROKER}:{settings.MQTT_PORT}, 模擬器={settings.USE_SIMULATOR}")

    # 註冊信號處理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 初始化元件
    from core.mqtt_client import MQTTClient
    from core.safety_monitor import SafetyMonitor
    from core.watchdog import Watchdog
    from services.sensor_service import SensorService
    from services.control_service import ControlService
    from services.data_logger import DataLogger
    from services.test_automation import TestAutomation

    mqtt = MQTTClient()
    safety = SafetyMonitor(mqtt)
    watchdog = Watchdog(mqtt_client=mqtt)
    sensors = SensorService(mqtt)
    control = ControlService(mqtt, safety)
    data_logger = DataLogger()
    automation = TestAutomation(mqtt, control, sensors, data_logger)

    try:
        # 啟動所有服務
        # 先啟動基礎服務
        await mqtt.start()
        safety_started = await safety.start()
        if not safety_started:
            logger.error("❌ 安全監控器啟動失敗，系統無法繼續")
            return
        
        sensors_started = await sensors.start()
        control_started = await control.start()
        
        if not sensors_started:
            logger.warning("⚠️ 感測器服務啟動失敗，將繼續運行但無法讀取數據")
        if not control_started:
            logger.warning("⚠️ 控制服務啟動失敗，將繼續運行但無法控制設備")
        
        automation.start()
        
        tasks = [
            watchdog.monitor(safety),
            sensors.polling_loop() if sensors_started else asyncio.sleep(3600),
            control.command_handler() if control_started else asyncio.sleep(3600),
            data_logger.logging_loop(),
            automation.state_machine_loop()
        ]

        await asyncio.gather(
            *tasks,
            shutdown_event.wait()
        )

    except KeyboardInterrupt:
        logger.info("⏸️ 收到中斷信號，正在關閉服務...")
    except Exception as e:
        logger.exception(f"❌ 系統異常: {e}")
    finally:
        # 優雅關閉所有服務
        logger.info("🛑 執行安全關閉程序...")
        automation.stop()
        sensors.stop()
        control.stop()
        data_logger.stop()
        safety.stop()
        await mqtt.disconnect()
        logger.info("✅ 系統已安全關閉")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 應用程式已關閉")

