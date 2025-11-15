# Modbus RTU 到 TCP 串口橋接器

將 Modbus RTU 請求從虛擬串口轉發到 Modbus TCP 模擬器服務。

## 功能

- 創建虛擬串口（使用 pty）
- 在虛擬串口上運行 Modbus RTU 服務器
- 將 RTU 請求轉發到 Modbus TCP 模擬器
- 支援多個虛擬串口和不同的 UART 設定

## 虛擬串口映射

| 虛擬串口 | TCP 端口 | UART 設定 | 設備 |
|---------|---------|----------|------|
| /dev/ttySIM0 | 5021 | 57600/8/NONE/1 | DC 電表 |
| /dev/ttySIM0_1 | 5022 | 57600/8/NONE/1 | AC110V 電表 |
| /dev/ttySIM0_2 | 5023 | 57600/8/NONE/1 | AC220V 電表 |
| /dev/ttySIM0_3 | 5024 | 57600/8/NONE/1 | AC220V 3P 電表 |
| /dev/ttySIM1 | 5020 | 19200/8/NONE/1 | 流量計 |
| /dev/ttySIM2 | 5027 | 115200/8/NONE/1 | 繼電器 IO |
| /dev/ttySIM3 | 5025 | 19200/8/EVEN/1 | 壓力計 (正壓) |
| /dev/ttySIM3_1 | 5026 | 19200/8/EVEN/1 | 壓力計 (真空) |

## 使用方式

### Docker Compose

```bash
docker compose up -d serial-bridge
```

## 注意事項

- 需要 `privileged: true` 權限來創建虛擬串口
- 虛擬串口會在容器停止時自動清理

