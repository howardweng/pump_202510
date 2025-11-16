"""Admin API 主程序"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# 載入環境變數（優先載入 .env.local，如果不存在則載入 .env）
# 注意：必須在導入 routers 之前載入環境變數
env_local = Path(__file__).parent / ".env.local"
env_file = Path(__file__).parent / ".env"
if env_local.exists():
    load_dotenv(env_local)
    logger.info(f"✅ 已載入環境變數: {env_local}")
elif env_file.exists():
    load_dotenv(env_file)
    logger.info(f"✅ 已載入環境變數: {env_file}")

# 在載入環境變數後才導入 routers
from routers import devices, scenarios
from routers.scenarios import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用生命週期管理"""
    # 啟動時初始化資料庫
    await init_db()
    
    # 連接 MQTT
    from mqtt_client import mqtt_manager
    from routers.devices import DEVICES
    try:
        await mqtt_manager.connect()
        
        # 啟動定期發布任務
        async def periodic_publish():
            """定期發布所有設備數據（每 2 秒）"""
            while True:
                try:
                    await asyncio.sleep(2.0)
                    await mqtt_manager.publish_all_devices(DEVICES)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"❌ 定期發布失敗: {e}")
        
        publish_task = asyncio.create_task(periodic_publish())
    except Exception as e:
        logger.warning(f"⚠️ MQTT 連接失敗，將在需要時重試: {e}")
        publish_task = None
    
    logger.info("✅ Admin API 已啟動")
    yield
    # 關閉時清理資源
    if publish_task:
        publish_task.cancel()
        try:
            await publish_task
        except asyncio.CancelledError:
            pass
    
    # 關閉 Modbus 連接
    from modbus_reader import modbus_reader
    await modbus_reader.close_all()
    
    await mqtt_manager.disconnect()
    logger.info("🛑 Admin API 已關閉")

# 配置日誌
log_level = os.getenv("LOG_LEVEL", "INFO")
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=log_level,
    colorize=True
)

# 創建 FastAPI 應用
app = FastAPI(
    title="MODBUS 模擬器 Admin API",
    description="MODBUS 設備模擬器管理 API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境應該限制來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(devices.router)
app.include_router(scenarios.router)


@app.get("/")
async def root():
    """根路徑"""
    return {
        "message": "MODBUS 模擬器 Admin API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康檢查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level=log_level.lower()
    )

