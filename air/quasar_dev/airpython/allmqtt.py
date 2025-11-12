import serial
import struct
import json
import time
import subprocess
import paho.mqtt.client as mqtt
from threading import Thread
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configuration
POLLING_INTERVAL = 2  # Set polling interval (in seconds)
PORT = '/dev/ttyUSB1'
BAUDRATE = 115200
BROKER = "localhost"
MQTT_PORT = 8883
TOPIC_FLOW = "air/flow"  # Single topic for the entire flow object
TOPIC_STAT = "usbrelay/stat"  # Single topic for relay statuses
TOPIC_CMD = "usbrelay/cmd"  # Single topic for relay commands

# MQTT Setup
mqtt_client = mqtt.Client(protocol=mqtt.MQTTv5)  # Use MQTT v5


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
        request = struct.pack('>B B H H', 0x01, 0x03, start_register, count)
        crc = calculate_crc(request)
        request += struct.pack('<H', crc)
        ser.write(request)
        response = ser.read(5 + 2 * count)
        ser.close()
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
        calculated_crc = calculate_crc(response[:-2])
        received_crc = int.from_bytes(crc, byteorder='little')
        if calculated_crc != received_crc:
            raise ValueError(f"CRC Error: Expected {calculated_crc:04X}, Got {received_crc:04X}")
        registers = [int.from_bytes(data[i:i + 2], byteorder='big') for i in range(0, len(data), 2)]
        return registers
    except Exception as e:
        print(f"Error decoding response: {e}")
        return None


import subprocess

def get_relay_status():
    """Fetch the current status of all relays and return as a JSON-like dictionary."""
    try:
        output = subprocess.run(["usbrelay"], capture_output=True, text=True, timeout=2)
        
        if output.returncode != 0:
            print("usbrelay command failed or device not detected")
            return {}  # Return empty if usbrelay fails

        relays = {}
        for line in output.stdout.strip().split("\n"):
            if "=" not in line:  # Ignore errors/malformed lines
                print(f"Skipping malformed line: {line}")
                continue
            
            parts = line.split("=")
            if len(parts) != 2:
                print(f"Skipping invalid relay entry: {line}")
                continue
            
            name, status = parts
            simple_name = name.split("_", 1)[-1]  # Extract simplified name
            relays[simple_name] = "ON" if status.strip() == "1" else "OFF"

        return relays

    except subprocess.TimeoutExpired:
        print("usbrelay command timeout. Device may be unresponsive.")
        return {}
    except FileNotFoundError:
        print("usbrelay command not found. Please install it.")
        return {}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {}



def toggle_relay(simple_name, state):
    """Toggle a specific relay ON (1) or OFF (0) using its simplified name."""
    try:
        full_relay_name = get_full_relay_name(simple_name)
        command = f"usbrelay {full_relay_name}={state}"
        subprocess.run(command.split(), check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error toggling relay {simple_name}: {e}")


def get_full_relay_name(simple_name):
    """Retrieve the full relay name by adding the initial prefix."""
    all_relays = subprocess.check_output(["usbrelay"], universal_newlines=True)
    for line in all_relays.strip().split("\n"):
        full_name, _ = line.split("=")
        if full_name.endswith(f"_{simple_name}"):
            return full_name
    return simple_name


import time

def process_command(client, cmd_payload):
    """Process the JSON command payload to control relays."""
    try:
        commands = json.loads(cmd_payload)
        all_command = commands.get("all", None)

        if all_command:
            state = 1 if all_command.upper() == "ON" else 0

            for relay in range(1, 5):  # Loop from relay 1 to 4
                toggle_relay(str(relay), state)  # Convert to string
                time.sleep(0.5)  # 0.2-second delay

            # Update status after all relays are toggled
            updated_status = get_relay_status()
            client.publish(TOPIC_STAT, json.dumps(updated_status), retain=False)
        else:
            for relay, action in commands.items():
                state = 1 if action.upper() == "ON" else 0
                toggle_relay(relay, state)

            # Update status after individual relays are toggled
            updated_status = get_relay_status()
            client.publish(TOPIC_STAT, json.dumps(updated_status), retain=False)

    except json.JSONDecodeError as e:
        print(f"Invalid JSON command received: {cmd_payload}. Error: {e}")
    except Exception as e:
        print(f"Error processing command: {e}")



def on_connect(client, userdata, flags, reason_code, properties):
    """Callback when the MQTT client connects to the broker."""
    print("Connected to MQTT Broker!")
    client.subscribe(TOPIC_CMD)  # Subscribe to the command topic


def on_message(client, userdata, msg):
    """Callback when an MQTT message is received."""
    topic = msg.topic
    if topic == TOPIC_CMD:
        cmd_payload = msg.payload.decode("utf-8").strip()
        process_command(client, cmd_payload)


def modbus_flow_main():
    try:
        mqtt_client.connect(BROKER, MQTT_PORT)
        mqtt_client.loop_start()
        mqtt_client.on_connect = on_connect  # Updated
        mqtt_client.on_message = on_message  # Updated
        while True:
            start_time = time.time()
            response = send_modbus_request(PORT, BAUDRATE, 0x0000, 3)
            if response:
                registers = decode_registers(response)
                if registers and len(registers) >= 3:
                    instantaneous_flow = registers[0] / 10.0
                    cumulative_flow = ((registers[1] << 16) | registers[2]) / 10.0
                    flow_data = {"instant": instantaneous_flow, "total": cumulative_flow}

                    mqtt_client.publish(TOPIC_FLOW, json.dumps(flow_data))
                    print(json.dumps(flow_data, ensure_ascii=False, indent=2))

            elapsed_time = time.time() - start_time
            time_to_wait = POLLING_INTERVAL - elapsed_time
            if time_to_wait > 0:
                time.sleep(time_to_wait)
    except KeyboardInterrupt:
        print("\nTerminating Modbus Flow...")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()


def relay_control_main():
    client = mqtt.Client(protocol=mqtt.MQTTv5)
    client.on_connect = on_connect  # Updated
    client.on_message = on_message  # Updated
    try:
        client.connect(BROKER, MQTT_PORT)
        client.loop_start()
        while True:
            relays = get_relay_status()
            client.publish(TOPIC_STAT, json.dumps(relays), retain=False)
            time.sleep(0.5)  # Update every second
    except KeyboardInterrupt:
        print("Exiting Relay Control...")
    finally:
        client.loop_stop()
        client.disconnect()



if __name__ == "__main__":
    mqtt_client.on_connect = on_connect  # Updated
    mqtt_client.on_message = on_message  # Updated

    modbus_thread = Thread(target=modbus_flow_main)
    relay_thread = Thread(target=relay_control_main)
    modbus_thread.start()
    relay_thread.start()
    modbus_thread.join()
    relay_thread.join()
