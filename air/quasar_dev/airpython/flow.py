import serial
import struct
import json
import time

POLLING_INTERVAL = 0.1  # Set polling interval (in seconds)

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

def send_modbus_request(port, baudrate, start_register, count):
    """Send a Modbus request to read multiple registers."""
    try:
        ser = serial.Serial(port, baudrate, timeout=1)

        # Build the Modbus request (Slave ID=1, Function=3, Start Register, Count)
        request = struct.pack('>B B H H', 0x01, 0x03, start_register, count)
        crc = calculate_crc(request)
        request += struct.pack('<H', crc)  # Append CRC

        ser.write(request)
        # Read the response
        response = ser.read(5 + 2 * count)  # 5 bytes header + 2 bytes per register
        ser.close()

        # Print raw data
        print(f"Raw data received: {response.hex()}")

        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def decode_registers(response):
    """Decode multiple register values from Modbus response."""
    try:
        if len(response) < 7:
            raise ValueError("Incomplete response.")

        byte_count = response[2]
        data = response[3:3 + byte_count]
        crc = response[-2:]

        # Validate CRC
        calculated_crc = calculate_crc(response[:-2])
        received_crc = int.from_bytes(crc, byteorder='little')
        if calculated_crc != received_crc:
            raise ValueError(f"CRC Error: Expected {calculated_crc:04X}, Got {received_crc:04X}")

        # Decode data into a list of register values
        registers = [int.from_bytes(data[i:i+2], byteorder='big') for i in range(0, len(data), 2)]
        return registers
    except Exception as e:
        print(f"Error decoding response: {e}")
        return None

def main():
    PORT = '/dev/ttyUSB1'
    BAUDRATE = 115200

    print("Press Ctrl+C to stop.")
    try:
        while True:
            start_time = time.time()

            # Read 3 registers starting from 0x0000
            response = send_modbus_request(PORT, BAUDRATE, 0x0000, 3)
            if response:
                registers = decode_registers(response)
                if registers and len(registers) >= 3:
                    instantaneous_flow = registers[0] / 10.0  # Scale factor for flow
                    cumulative_flow = ((registers[1] << 16) | registers[2]) / 10.0  # Combine high and low

                    # Format as JSON
                    data = {
                        "instantaneous_flow": instantaneous_flow,
                        "cumulative_flow": cumulative_flow
                    }
                    print(json.dumps(data, ensure_ascii=False, indent=2))
                else:
                    print("Invalid response.")
            else:
                print("No response received.")

            # Wait for next polling interval
            elapsed_time = time.time() - start_time
            time_to_wait = POLLING_INTERVAL - elapsed_time
            if time_to_wait > 0:
                time.sleep(time_to_wait)
    except KeyboardInterrupt:
        print("\nTerminating...")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
