"""全域配置管理"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# 載入環境變數
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """應用程式設定"""
    
    def __init__(self):
        # MQTT 配置
        self.MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
        self.MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
        self.MQTT_USERNAME = os.getenv("MQTT_USERNAME")
        self.MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
        
        # 模擬器開關
        use_simulator = os.getenv("USE_SIMULATOR", "true").lower()
        self.USE_SIMULATOR = use_simulator in ("true", "1", "yes")
        
        # 日誌配置
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        # 資料庫配置
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "sqlite:///./data/database.db"
        )


# 全域設定實例
settings = Settings()

