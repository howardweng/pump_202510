#!/usr/bin/env python3
import serial
import struct
import time

PORT = "/dev/ttyUSB0"
BAUDRATE = 115200
PAYLOAD = bytes.fromhex("020300000002")  # Modbus request payload
DELAY_BETWEEN_REQUESTS = 0.15  # 15ms delay (safe for GZ400)

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

def send_request(ser):
    """Send Modbus request and read the response at max speed."""
    crc = calculate_crc(PAYLOAD)
    request = PAYLOAD + struct.pack('<H', crc)
    ser.write(request)
    time.sleep(DELAY_BETWEEN_REQUESTS)  # Wait for GZ400 to process response
    return ser.read_all()  # Read all available response data

def continuous_temp_read():
    """Continuously send requests at max speed."""
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=0.05) as ser:  # Short timeout for faster response handling
            print(f"Opened {PORT} at {BAUDRATE} bps. Sending continuous requests...")

            while True:
                response = send_request(ser)
                if response and len(response) >= 9:
                    temp_bytes = response[3:7]
                    raw_temp = int.from_bytes(temp_bytes, byteorder="big")
                    temperature = raw_temp / 10.0
                    print(f"Temperature: {temperature:.1f} °C")
                else:
                    print("No or incomplete response received.")
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")
    except Exception as e:
        print(f"Serial error: {e}")

if __name__ == "__main__":
    continuous_temp_read()
