#!/usr/bin/env python3
import serial
import struct
import json
import time

PORT = "/dev/ttyUSB0"
BAUDRATE = 115200
DELAY_BETWEEN_REQUESTS = 0.015  # 15ms delay (safe for GZ400)

def calculate_crc(data):
    """Calculate Modbus CRC16."""
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def send_custom_modbus_request(ser, payload):
    """Send a Modbus request and read the response."""
    try:
        crc = calculate_crc(payload)
        payload_with_crc = payload + struct.pack('<H', crc)
        ser.write(payload_with_crc)
        time.sleep(DELAY_BETWEEN_REQUESTS)  # Wait for response (max speed)
        return ser.read_all()  # Read all available data
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_single_temp(ser):
    """Read a single temperature value."""
    payload = bytes.fromhex("020300000002")
    response = send_custom_modbus_request(ser, payload)
    if response and len(response) >= 9:
        temp_bytes = response[3:7]
        raw_temp = int.from_bytes(temp_bytes, byteorder="big")
        return raw_temp / 10.0
    return None

def get_three_temps(ser):
    """Read three temperature values."""
    payload = bytes.fromhex("010300280003")
    response = send_custom_modbus_request(ser, payload)
    if response and len(response) >= 9:
        data_bytes = response[3:9]
        return [int.from_bytes(data_bytes[i:i+2], byteorder="big") / 10.0 for i in range(0, len(data_bytes), 2)]
    return [None, None, None]

def continuous_temp_read():
    """Continuously read temperatures at maximum speed."""
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=0.05) as ser:
            print(f"Opened {PORT} at {BAUDRATE} bps. Reading temperatures continuously...")

            while True:
                temp1 = get_single_temp(ser)
                temps = get_three_temps(ser)

                if temp1 is not None and None not in temps:
                    output = {
                        "temp1": temp1,
                        "temp2": temps[0],
                        "temp3": temps[1],
                        "temp4": temps[2]
                    }
                    print(json.dumps(output, indent=4))
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")
    except Exception as e:
        print(f"Serial error: {e}")

if __name__ == "__main__":
    continuous_temp_read()
