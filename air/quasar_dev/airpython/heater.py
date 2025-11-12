import serial
import struct
import time
import subprocess
import serial.tools.list_ports

# Configuration for the second Modbus device
PORT = '/dev/ttyUSB1'  # Adjust to your device's port
BAUDRATE = 115200      # Adjust if different
SLAVE_ID = 0x01       # Modbus slave ID

def list_usb_devices():
    """List all USB devices with detailed information."""
    print("\n=== USB Device Details ===")
    
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"\nDevice: {port.device}")
        print(f"  Manufacturer: {port.manufacturer}")
        print(f"  Product: {port.product}")
        print(f"  Description: {port.description}")
        print(f"  Serial Number: {port.serial_number}")
        print(f"  Location: {port.location}")
        print(f"  Interface: {port.interface}")
        print(f"  Hardware ID: {port.hwid}")

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

def send_modbus_request(start_register, count):
    """Send a Modbus request to read multiple registers."""
    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        # Create Modbus RTU read holding registers request
        request = struct.pack('>B B H H', SLAVE_ID, 0x03, start_register, count)
        crc = calculate_crc(request)
        request += struct.pack('<H', crc)
        
        # Send request and get response
        ser.write(request)
        response = ser.read(5 + 2 * count)  # Read response (5 bytes header/CRC + 2 bytes per register)
        ser.close()
        
        if len(response) < 5:
            print("No response received")
            return None
            
        # Process response
        byte_count = response[2]
        data = response[3:3 + byte_count]
        
        # Convert bytes to register values
        registers = []
        for i in range(0, len(data), 2):
            register = int.from_bytes(data[i:i+2], byteorder='big')
            registers.append(register)
            
        return registers
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    # Just list the devices without starting Modbus communication
    list_usb_devices()

if __name__ == "__main__":
    main()
