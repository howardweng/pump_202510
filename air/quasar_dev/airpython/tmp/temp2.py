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

        print("Sending:", payload_with_crc.hex())
        ser.write(payload_with_crc)
        # Read the response (adjust size if necessary)
        response = ser.read(256)
        ser.close()

        print(f"Raw data received: {response.hex()}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_three_temp_read():
    PORT = '/dev/ttyUSB0'
    BAUDRATE = 115200

    # Custom payload to request 3 registers starting at address 0x28 for slave 01
    # Without CRC, the payload is: 01 03 00 28 00 03
    payload = bytes.fromhex('010300280003')

    # Send the custom request
    response = send_custom_modbus_request(PORT, BAUDRATE, payload)
    if response:
        # Expected response format:
        # Slave Addr (1 byte) | Function (1 byte) | Byte count (1 byte) | 
        # Data (6 bytes: 3 registers, each 2 bytes) | CRC (2 bytes)
        if len(response) >= 9:
            # Extract the 6 data bytes (index 3 to 8)
            data_bytes = response[3:3+6]
            temperatures = []
            # Process each 2-byte register
            for i in range(0, len(data_bytes), 2):
                # Extract 2 bytes for each channel
                temp_bytes = data_bytes[i:i+2]
                # Convert from big-endian to integer
                raw_temp = int.from_bytes(temp_bytes, byteorder='big')
                # Convert to a temperature value with one decimal place
                temperature = raw_temp / 10.0
                temperatures.append(temperature)
                print(f"Channel {i//2 + 1} raw bytes: {temp_bytes.hex()} -> Temperature: {temperature:.1f}")

            print("All channel temperatures:", temperatures)
        else:
            print("Response too short to contain three temperature channels data")
    else:
        print("No response received.")

if __name__ == "__main__":
    test_three_temp_read()
