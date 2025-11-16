"""列舉定義"""
from enum import Enum


class TestState(Enum):
    """測試狀態"""
    IDLE = "idle"                    # 閒置
    INITIALIZING = "initializing"    # 初始化中
    READY = "ready"                  # 準備就緒
    RUNNING = "running"              # 測試運行中
    PAUSED = "paused"                # 暫停
    COMPLETED = "completed"          # 完成
    FAILED = "failed"                # 失敗
    STOPPED = "stopped"              # 已停止


class TestMode(Enum):
    """測試模式"""
    MANUAL = "manual"                # 手動測試
    AUTOMATIC = "automatic"          # 自動測試
    CALIBRATION = "calibration"      # 校準模式


class PowerType(Enum):
    """電源類型"""
    DC = "dc"
    AC110 = "ac110"
    AC220 = "ac220"
    AC220_3P = "ac220_3p"


class ValveState(Enum):
    """閥門狀態"""
    VACUUM = "vacuum"                # 真空模式
    POSITIVE = "positive"            # 正壓模式
    MANUAL = "manual"                # 手動模式
    CLOSED = "closed"                # 關閉



