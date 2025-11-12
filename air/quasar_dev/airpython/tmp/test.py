import serial
import struct
import json
import time

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

def send_custom_modbus_request(port, baudrate, payload):
    """Send a custom Modbus request with a given payload."""
    try:
        ser = serial.Serial(port, baudrate, timeout=1)

        # Append CRC to the payload
        crc = calculate_crc(payload)
        payload_with_crc = payload + struct.pack('<H', crc)

        ser.write(payload_with_crc)
        # Read the response
        response = ser.read(256)  # Adjust the size as needed
        ser.close()

        # Print raw data
        print(f"Raw data received: {response.hex()}")

        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_custom_modbus_communication():
    PORT = '/dev/ttyUSB0'
    BAUDRATE = 115200

    # Custom payload: 02 10 00 64 00 02 04 00 00 00 01
    payload = bytes.fromhex('0210006400020400000001')

    # Send the custom request
    response = send_custom_modbus_request(PORT, BAUDRATE, payload)
    if response:
        print("Response received.")
    else:
        print("No response received.")

if __name__ == "__main__":
    test_custom_modbus_communication()