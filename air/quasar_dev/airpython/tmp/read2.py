import serial
import struct
import time

def send_hex_command(port, baudrate, hex_command):
    """
    Open the serial port, send the hex command (as a string),
    read and print any response, and then close the port.
    """
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        # Remove spaces and convert hex string to bytes
        hex_command = hex_command.replace(" ", "")
        data = bytes.fromhex(hex_command)
        print("Sending:", hex_command)
        ser.write(data)
        # Read any available response (if applicable)
        response = ser.read(256)
        ser.close()
        print("Response:", response.hex())
        return response
    except Exception as e:
        print("Error sending hex command:", e)
        return None

def get_temperature(port, baudrate):
    """
    Send the read temperature command (02 03 00 00 00 02) and process the response.
    Expected response: 02 03 04 [00 00 00 A8] CRC (total 9 bytes)
    The four data bytes are converted from big-endian integer and divided by 10.
    """
    # Temperature read command (without CRC; the slave should add CRC to its response)
    payload = "02 03 00 00 00 02"
    response = send_hex_command(port, baudrate, payload)
    if response and len(response) >= 9:
        # Extract the four data bytes (indexes 3 to 6)
        temp_bytes = response[3:7]
        raw_temp = int.from_bytes(temp_bytes, byteorder='big')
        temperature = raw_temp / 10.0
        return temperature
    else:
        print("Temperature read failed or response too short.")
        return None

def main():
    PORT = '/dev/ttyUSB0'
    BAUDRATE = 115200

    # 1. Initiate system
    init_cmd = "02 10 00 64 00 02 04 00 00 00 01 3A F0"
    print("\n-- Initiating System --")
    send_hex_command(PORT, BAUDRATE, init_cmd)

    # 2. Turn on heater
    heater_on_cmd = "02 10 00 6C 00 02 04 00 00 00 00 FA 96"
    print("\n-- Turning ON Heater --")
    send_hex_command(PORT, BAUDRATE, heater_on_cmd)

    # 3. Wait for 20 seconds while reading temperature every 1 second
    print("\n-- Reading Temperature Every 1 Second for 20 Seconds --")
    for i in range(20):
        temp = get_temperature(PORT, BAUDRATE)
        if temp is not None:
            print(f"Time {i+1:2d}s - Temperature: {temp:.1f}")
        else:
            print(f"Time {i+1:2d}s - Temperature reading failed.")
        time.sleep(1)

    # 4. Stop heater
    heater_stop_cmd = "02 10 00 6C 00 02 04 00 00 00 01 3B 56"
    print("\n-- Stopping Heater --")
    send_hex_command(PORT, BAUDRATE, heater_stop_cmd)

    print("\nConfig End")

if __name__ == "__main__":
    main()
