import serial
import struct

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
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def continuous_temp_read():
    PORT = '/dev/ttyUSB0'
    BAUDRATE = 115200
    # Payload to read 2 registers (4 bytes) starting at address 0
    payload = bytes.fromhex('020300000002')

    while True:
        response = send_custom_modbus_request(PORT, BAUDRATE, payload)
        if response and len(response) >= 9:
            # Extract the temperature data (bytes index 3 to 6)
            temp_bytes = response[3:7]
            raw_temp = int.from_bytes(temp_bytes, byteorder='big')
            temperature = raw_temp / 10.0  # Convert to a temperature value with one decimal place
            print(f"Temperature: {temperature:.1f}")
        else:
            print("No or incomplete response received.")

if __name__ == "__main__":
    try:
        continuous_temp_read()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")
