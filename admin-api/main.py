"""Admin API 主程序"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers import devices, scenarios
from routers.scenarios import init_db
from loguru import logger
import sys
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用生命週期管理"""
    # 啟動時初始化資料庫
    await init_db()
    logger.info("✅ Admin API 已啟動")
    yield
    # 關閉時清理資源
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

