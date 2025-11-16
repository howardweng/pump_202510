"""設備健康狀態模型"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
import time


class DeviceHealth(Enum):
    """設備健康狀態"""
    HEALTHY = "healthy"        # 正常運作
    DEGRADED = "degraded"      # 偶爾失敗，但可恢復
    UNHEALTHY = "unhealthy"    # 連續失敗，需要關注
    OFFLINE = "offline"        # 完全無法通訊


@dataclass
class DeviceStatus:
    """設備狀態資訊"""
    health: DeviceHealth = DeviceHealth.OFFLINE
    error_count: int = 0
    consecutive_errors: int = 0
    last_success_time: Optional[float] = None
    last_error_time: Optional[float] = None
    total_requests: int = 0
    successful_requests: int = 0
    
    def update_success(self):
        """更新成功狀態"""
        self.last_success_time = time.time()
        self.consecutive_errors = 0
        self.total_requests += 1
        self.successful_requests += 1
        
        # 根據錯誤率更新健康狀態
        if self.consecutive_errors == 0:
            if self.health != DeviceHealth.HEALTHY:
                self.health = DeviceHealth.HEALTHY
        elif self.health == DeviceHealth.UNHEALTHY:
            self.health = DeviceHealth.DEGRADED
    
    def update_error(self):
        """更新錯誤狀態"""
        self.error_count += 1
        self.consecutive_errors += 1
        self.last_error_time = time.time()
        self.total_requests += 1
        
        # 根據連續錯誤數更新健康狀態
        if self.consecutive_errors >= 5:
            self.health = DeviceHealth.UNHEALTHY
        elif self.consecutive_errors >= 2:
            self.health = DeviceHealth.DEGRADED
    
    def get_success_rate(self) -> float:
        """計算成功率"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests



