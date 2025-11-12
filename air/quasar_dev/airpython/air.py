from pymodbus.client.sync import ModbusSerialClient

def test_device():
    """Test reading the instantaneous flow register (0x0000)."""
    # Configure the Modbus client
    client = ModbusSerialClient(
        method='rtu',
        port='/dev/ttyUSB0',  # Replace with your port
        baudrate=9600,
        stopbits=1,
        bytesize=8,
        parity='N',
        timeout=1
    )

    if not client.connect():
        print("Failed to connect to the device.")
        return

    try:
        # Read instantaneous flow (register 0x0000)
        response = client.read_holding_registers(0x0000, 1, unit=1)  # Default slave ID is 1
        if response.isError():
            print(f"Error reading data: {response}")
        else:
            # Convert and display the flow value
            instantaneous_flow = response.registers[0] / 10.0  # Scale factor is 10
            print(f"Instantaneous Flow: {instantaneous_flow} L/min")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    test_device()
