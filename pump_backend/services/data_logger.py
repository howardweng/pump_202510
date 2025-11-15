"""數據記錄服務"""
import asyncio
import csv
import os
import time
from pathlib import Path
from typing import Dict, Optional, Any
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

    def __init__(self, mqtt_client: MQTTClient, data_dir: str = "./data/test_records"):
        self.mqtt = mqtt_client
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_test_id: Optional[str] = None
        self.csv_file: Optional[csv.writer] = None
        self.csv_handle: Optional[file] = None
        self._running = False
        
        # 用於聚合感測器數據
        self._sensor_data_cache: Dict[str, Any] = {}

    async def logging_loop(self):
        """
        數據記錄迴圈
        
        訂閱感測器數據並記錄到 CSV
        """
        logger.info("🔄 數據記錄迴圈已啟動")
        
        # 訂閱所有感測器主題
        self.mqtt.subscribe(SENSOR_FLOW, self._handle_flow_data)
        self.mqtt.subscribe(SENSOR_PRESSURE_POSITIVE, self._handle_pressure_positive_data)
        self.mqtt.subscribe(SENSOR_PRESSURE_VACUUM, self._handle_pressure_vacuum_data)
        self.mqtt.subscribe(SENSOR_POWER_DC, self._handle_power_dc_data)
        self.mqtt.subscribe(SENSOR_POWER_AC110, self._handle_power_ac110_data)
        self.mqtt.subscribe(SENSOR_POWER_AC220, self._handle_power_ac220_data)
        self.mqtt.subscribe(SENSOR_POWER_AC220_3P, self._handle_power_ac220_3p_data)
        
        logger.info("📥 已訂閱所有感測器數據主題")
        
        # 保持運行，等待測試開始
        self._running = True
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
            
            # 清空數據緩存
            self._sensor_data_cache.clear()
            
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
        
        # 清空數據緩存
        self._sensor_data_cache.clear()
        
        if self.current_test_id:
            logger.info(f"✅ 測試記錄已停止: {self.current_test_id}")
            self.current_test_id = None

    def _handle_flow_data(self, payload: Dict):
        """處理流量計數據"""
        self._sensor_data_cache.update({
            "flow_instantaneous": payload.get("instantaneous"),
            "flow_cumulative": payload.get("cumulative"),
            "timestamp": payload.get("timestamp", time.time())
        })
        self._flush_data()

    def _handle_pressure_positive_data(self, payload: Dict):
        """處理正壓感測器數據"""
        self._sensor_data_cache.update({
            "pressure_positive": payload.get("pressure"),
            "timestamp": payload.get("timestamp", time.time())
        })
        self._flush_data()

    def _handle_pressure_vacuum_data(self, payload: Dict):
        """處理負壓感測器數據"""
        self._sensor_data_cache.update({
            "pressure_vacuum": payload.get("pressure"),
            "timestamp": payload.get("timestamp", time.time())
        })
        self._flush_data()

    def _handle_power_dc_data(self, payload: Dict):
        """處理 DC 電表數據"""
        self._sensor_data_cache.update({
            "dc_voltage": payload.get("voltage"),
            "dc_current": payload.get("current"),
            "dc_power": payload.get("power"),
            "timestamp": payload.get("timestamp", time.time())
        })
        self._flush_data()

    def _handle_power_ac110_data(self, payload: Dict):
        """處理 AC110V 電表數據"""
        self._sensor_data_cache.update({
            "ac110_voltage": payload.get("voltage"),
            "ac110_current": payload.get("current"),
            "ac110_power": payload.get("power"),
            "timestamp": payload.get("timestamp", time.time())
        })
        self._flush_data()

    def _handle_power_ac220_data(self, payload: Dict):
        """處理 AC220V 電表數據"""
        self._sensor_data_cache.update({
            "ac220_voltage": payload.get("voltage"),
            "ac220_current": payload.get("current"),
            "ac220_power": payload.get("power"),
            "timestamp": payload.get("timestamp", time.time())
        })
        self._flush_data()

    def _handle_power_ac220_3p_data(self, payload: Dict):
        """處理 AC220V 3P 電表數據"""
        self._sensor_data_cache.update({
            "ac220_3p_voltage_a": payload.get("voltage_a"),
            "ac220_3p_voltage_b": payload.get("voltage_b"),
            "ac220_3p_voltage_c": payload.get("voltage_c"),
            "ac220_3p_current_a": payload.get("current_a"),
            "ac220_3p_current_b": payload.get("current_b"),
            "ac220_3p_current_c": payload.get("current_c"),
            "ac220_3p_total_power": payload.get("total_power"),
            "timestamp": payload.get("timestamp", time.time())
        })
        self._flush_data()

    def _flush_data(self):
        """
        將緩存的感測器數據寫入 CSV
        
        當有新的感測器數據到達時，將所有緩存的數據寫入一行
        """
        if not self.csv_file or not self.current_test_id:
            return
        
        try:
            # 提取數據
            row = [
                self._sensor_data_cache.get("timestamp", time.time()),
                self._sensor_data_cache.get("flow_instantaneous"),
                self._sensor_data_cache.get("flow_cumulative"),
                self._sensor_data_cache.get("pressure_positive"),
                self._sensor_data_cache.get("pressure_vacuum"),
                self._sensor_data_cache.get("dc_voltage"),
                self._sensor_data_cache.get("dc_current"),
                self._sensor_data_cache.get("dc_power"),
                self._sensor_data_cache.get("ac110_voltage"),
                self._sensor_data_cache.get("ac110_current"),
                self._sensor_data_cache.get("ac110_power"),
                self._sensor_data_cache.get("ac220_voltage"),
                self._sensor_data_cache.get("ac220_current"),
                self._sensor_data_cache.get("ac220_power"),
                self._sensor_data_cache.get("ac220_3p_voltage_a"),
                self._sensor_data_cache.get("ac220_3p_voltage_b"),
                self._sensor_data_cache.get("ac220_3p_voltage_c"),
                self._sensor_data_cache.get("ac220_3p_current_a"),
                self._sensor_data_cache.get("ac220_3p_current_b"),
                self._sensor_data_cache.get("ac220_3p_current_c"),
                self._sensor_data_cache.get("ac220_3p_total_power")
            ]
            
            self.csv_file.writerow(row)
            self.csv_handle.flush()  # 立即寫入
            
        except Exception as e:
            logger.error(f"❌ 記錄數據失敗: {e}")

    def log_sensor_data(self, data: Dict):
        """
        記錄感測器數據（保留此方法以向後兼容）
        
        Args:
            data: 感測器數據字典
        """
        self._sensor_data_cache.update(data)
        self._flush_data()

    def stop(self):
        """停止數據記錄服務"""
        self._running = False
        self.stop_test_logging()
        logger.info("🛑 數據記錄服務已停止")

