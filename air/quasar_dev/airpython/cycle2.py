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

def send_custom_modbus_request(ser, payload):
    """
    Send a custom Modbus request with a given payload using an already open serial port.
    The function appends the CRC to the payload.
    """
    try:
        crc = calculate_crc(payload)
        payload_with_crc = payload + struct.pack('<H', crc)
        ser.write(payload_with_crc)
        response = ser.read(256)
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def send_hex_command_open(ser, hex_command):
    """
    Send a full hex command (with CRC already embedded) using an already open serial port.
    """
    try:
        hex_command = hex_command.replace(" ", "")
        data = bytes.fromhex(hex_command)
        ser.write(data)
        # Optionally, read and discard any response.
        ser.read(256)
    except Exception as e:
        print(f"Error sending hex command: {e}")

def get_single_temp(ser):
    """
    Read a single temperature value using payload: 02 03 00 00 00 02.
    Expected response: 02 03 04 [4 data bytes] CRC.
    """
    payload = bytes.fromhex('020300000002')
    response = send_custom_modbus_request(ser, payload)
    if response and len(response) >= 9:
        temp_bytes = response[3:7]
        raw_temp = int.from_bytes(temp_bytes, byteorder='big')
        return raw_temp / 10.0
    return None

def get_three_temps(ser):
    """
    Read three temperature values using payload: 01 03 00 28 00 03.
    Expected response: 01 03 06 [6 data bytes] CRC.
    """
    payload = bytes.fromhex('010300280003')
    response = send_custom_modbus_request(ser, payload)
    if response and len(response) >= 9:
        data_bytes = response[3:9]
        temps = []
        for i in range(0, len(data_bytes), 2):
            raw_temp = int.from_bytes(data_bytes[i:i+2], byteorder='big')
            temps.append(raw_temp / 10.0)
        return temps
    return [None, None, None]

def main():
    PORT = '/dev/ttyUSB0'
    BAUDRATE = 115200

    try:
        # Open the serial port once
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
    except Exception as e:
        print(f"Error opening serial port: {e}")
        return

    # 1. Initiate system
    init_cmd = "02 10 00 64 00 02 04 00 00 00 01 3A F0"
    send_hex_command_open(ser, init_cmd)

    # 2. Turn on heater
    heater_on_cmd = "02 10 00 6C 00 02 04 00 00 00 00 FA 96"
    send_hex_command_open(ser, heater_on_cmd)

    # Print stage "啟動" after initialization and heater on.
    print("啟動")

    # 3. Start temperature reading cycle
    print("開始")
    cycle_duration = 20  # Duration of the reading cycle in seconds
    start_time = time.time()
    while time.time() - start_time < cycle_duration:
        temp1 = get_single_temp(ser)
        temps = get_three_temps(ser)
        if temp1 is not None and None not in temps:
            output = {
                "temp1": temp1,
                "temp2": temps[0],
                "temp3": temps[1],
                "temp4": temps[2]
            }
            print(json.dumps(output))
        time.sleep(0.1)

    # 4. Stop heater
    heater_off_cmd = "02 10 00 6C 00 02 04 00 00 00 01 3B 56"
    send_hex_command_open(ser, heater_off_cmd)

    # Print stage "結束"
    print("結束")

    ser.close()

if __name__ == "__main__":
    main()
