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

def send_modbus_request(port, baudrate, request):
    """Send Modbus request and receive response."""
    try:
        # Open the serial port
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"Connected to {port} at {baudrate} baud.")

        # Send the request
        print(f"Sending: {' '.join(format(x, '02X') for x in request)}")
        ser.write(request)

        # Wait for the response
        print("Waiting for response...")
        response = ser.read(8)  # Adjust length based on expected response
        ser.close()

        # Check response length
        if len(response) < 7:
            print("Incomplete or no response received.")
            return None

        print(f"Received (Hex): {' '.join(format(x, '02X') for x in response)}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def decode_response(response):
    """Decode Modbus response from AFM07."""
    try:
        if len(response) < 7:
            raise ValueError("Incomplete response.")

        slave_id = response[0]
        function_code = response[1]
        byte_count = response[2]
        data = response[3:3 + byte_count]
        crc = response[-2:]

        # Validate CRC
        calculated_crc = calculate_crc(response[:-2])
        received_crc = int.from_bytes(crc, byteorder='little')
        if calculated_crc != received_crc:
            print(f"CRC Error: Expected {calculated_crc:04X}, Got {received_crc:04X}")
            return

        # Decode instantaneous flow (register 0x0000)
        if function_code == 3 and byte_count == 2:
            raw_flow = int.from_bytes(data, byteorder='big')
            scaled_flow = raw_flow / 10.0  # Scale factor is 10
            print(f"Instantaneous Flow: {scaled_flow} L/min")
        else:
            print("Unexpected response format.")

        # Print parsed details
        print(f"Slave ID: {slave_id}")
        print(f"Function Code: {function_code}")
        print(f"Data (Hex): {' '.join(format(x, '02X') for x in data)}")
        print(f"CRC: {' '.join(format(x, '02X') for x in crc)}")

    except Exception as e:
        print(f"Error decoding response: {e}")

if __name__ == "__main__":
    # Modbus RTU settings
    PORT = '/dev/ttyUSB0'
    BAUDRATE = 115200

    # Modbus request to read register 0x0000 (instantaneous flow)
    request = b"\x01\x03\x00\x00\x00\x01"  # Slave ID=1, Function=3, Start=0x0000, Length=1
    crc = calculate_crc(request)
    request += struct.pack('<H', crc)  # Append CRC (little-endian)

    # Send request and get response
    response = send_modbus_request(PORT, BAUDRATE, request)

    # Decode and process response
    if response:
        decode_response(response)
