"""MQTT 主題定義"""

# 感測器數據主題
SENSOR_FLOW = "pump/sensors/flow"
SENSOR_PRESSURE_POSITIVE = "pump/sensors/pressure/positive"
SENSOR_PRESSURE_VACUUM = "pump/sensors/pressure/vacuum"
SENSOR_POWER_DC = "pump/sensors/power/dc"
SENSOR_POWER_AC110 = "pump/sensors/power/ac110"
SENSOR_POWER_AC220 = "pump/sensors/power/ac220"
SENSOR_POWER_AC220_3P = "pump/sensors/power/ac220_3p"

# 控制命令主題
CONTROL_VALVE = "pump/control/valve"
CONTROL_POWER = "pump/control/power"
CONTROL_TEST = "pump/control/test"

# 安全狀態主題
SAFETY_STATUS = "pump/safety/status"
SAFETY_ALERT = "pump/system/alert"

# 系統狀態主題
SYSTEM_STATUS = "pump/system/status"
SYSTEM_HEALTH = "pump/system/health"

# 測試記錄主題
TEST_RECORD = "pump/test/record"
TEST_STATUS = "pump/test/status"



