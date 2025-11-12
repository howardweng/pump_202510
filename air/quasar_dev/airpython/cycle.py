import serial
import time

def send_hex_command(port, baudrate, hex_command):
    """
    Open the serial port, send the hex command (as a string with or without spaces),
    read and print any response, and then close the port.
    """
    try:
        # Open the serial port
        ser = serial.Serial(port, baudrate, timeout=1)
        # Remove any spaces and convert the hex string to bytes
        hex_command = hex_command.replace(" ", "")
        data = bytes.fromhex(hex_command)
        print("Sending:", hex_command)
        ser.write(data)
        # Optionally read any response (if expected)
        response = ser.read(256)
        ser.close()
        print("Response:", response.hex())
        return response
    except Exception as e:
        print("Error sending hex command:", e)
        return None

def main():
    PORT = '/dev/ttyUSB0'
    BAUDRATE = 115200

    # 1. Initiate system with:
    #    02 10 00 64 00 02 04 00 00 00 01 3A F0
    init_cmd = "02 10 00 64 00 02 04 00 00 00 01 3A F0"
    send_hex_command(PORT, BAUDRATE, init_cmd)

    # 2. Turn on heater with:
    #    02 10 00 6C 00 02 04 00 00 00 00 FA 96
    heater_on_cmd = "02 10 00 6C 00 02 04 00 00 00 00 FA 96"
    send_hex_command(PORT, BAUDRATE, heater_on_cmd)

    # 3. Delay for 20 seconds
    print("Delaying for 20 seconds...")
    time.sleep(3)

    # 4. Stop heater with:
    #    02 10 00 6C 00 02 04 00 00 00 01 3B 56
    heater_stop_cmd = "02 10 00 6C 00 02 04 00 00 00 01 3B 56"
    send_hex_command(PORT, BAUDRATE, heater_stop_cmd)

    print("Config End")

if __name__ == "__main__":
    main()
