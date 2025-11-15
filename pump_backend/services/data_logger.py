"""數據記錄服務"""
import asyncio
import csv
import os
import time
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from loguru import logger
from core.mqtt_client import MQTTClient
from config.mqtt_topics import (
    SENSOR_FLOW,
    SENSOR_PRESSURE_POSITIVE,
    SENSOR_PRESSURE_VACUUM,
    SENSOR_POWER_DC,
    SENSOR_POWER_AC110,
    SENSOR_POWER_AC220,
    SENSOR_POWER_AC220_3P,
    TEST_RECORD
)


class DataLogger:
    """
    數據記錄服務
    
    負責將感測器數據記錄到 CSV 文件
    """

    def __init__(self, data_dir: str = "./data/test_records"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_test_id: Optional[str] = None
        self.csv_file: Optional[csv.writer] = None
        self.csv_handle: Optional[file] = None
        self._running = False

    async def logging_loop(self):
        """
        數據記錄迴圈
        
        訂閱感測器數據並記錄到 CSV
        """
        logger.info("🔄 數據記錄迴圈已啟動")
        
        # 保持運行，等待測試開始
        while self._running:
            await asyncio.sleep(1.0)

    def start_test_logging(self, test_id: str):
        """
        開始測試記錄
        
        Args:
            test_id: 測試 ID
        """
        if self.current_test_id:
            logger.warning(f"⚠️ 已有測試記錄進行中: {self.current_test_id}")
            return
        
        self.current_test_id = test_id
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.data_dir / f"test_{test_id}_{timestamp}.csv"
        
        try:
            self.csv_handle = open(filename, 'w', newline='', encoding='utf-8')
            self.csv_file = csv.writer(self.csv_handle)
            
            # 寫入標題行
            self.csv_file.writerow([
                "timestamp",
                "flow_instantaneous",
                "flow_cumulative",
                "pressure_positive",
                "pressure_vacuum",
                "dc_voltage",
                "dc_current",
                "dc_power",
                "ac110_voltage",
                "ac110_current",
                "ac110_power",
                "ac220_voltage",
                "ac220_current",
                "ac220_power",
                "ac220_3p_voltage_a",
                "ac220_3p_voltage_b",
                "ac220_3p_voltage_c",
                "ac220_3p_current_a",
                "ac220_3p_current_b",
                "ac220_3p_current_c",
                "ac220_3p_total_power"
            ])
            
            logger.info(f"✅ 測試記錄已開始: {filename}")
        except Exception as e:
            logger.error(f"❌ 創建測試記錄文件失敗: {e}")
            self.current_test_id = None

    def stop_test_logging(self):
        """停止測試記錄"""
        if self.csv_handle:
            self.csv_handle.close()
            self.csv_handle = None
            self.csv_file = None
        
        if self.current_test_id:
            logger.info(f"✅ 測試記錄已停止: {self.current_test_id}")
            self.current_test_id = None

    def log_sensor_data(self, data: Dict):
        """
        記錄感測器數據
        
        Args:
            data: 感測器數據字典
        """
        if not self.csv_file or not self.current_test_id:
            return
        
        try:
            # 提取數據
            row = [
                data.get("timestamp", time.time()),
                data.get("flow_instantaneous"),
                data.get("flow_cumulative"),
                data.get("pressure_positive"),
                data.get("pressure_vacuum"),
                data.get("dc_voltage"),
                data.get("dc_current"),
                data.get("dc_power"),
                data.get("ac110_voltage"),
                data.get("ac110_current"),
                data.get("ac110_power"),
                data.get("ac220_voltage"),
                data.get("ac220_current"),
                data.get("ac220_power"),
                data.get("ac220_3p_voltage_a"),
                data.get("ac220_3p_voltage_b"),
                data.get("ac220_3p_voltage_c"),
                data.get("ac220_3p_current_a"),
                data.get("ac220_3p_current_b"),
                data.get("ac220_3p_current_c"),
                data.get("ac220_3p_total_power")
            ]
            
            self.csv_file.writerow(row)
            self.csv_handle.flush()  # 立即寫入
            
        except Exception as e:
            logger.error(f"❌ 記錄數據失敗: {e}")

    def stop(self):
        """停止數據記錄服務"""
        self._running = False
        self.stop_test_logging()
        logger.info("🛑 數據記錄服務已停止")

