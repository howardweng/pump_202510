import serial
import struct
import json
import time
import threading
import paho.mqtt.client as mqtt

# MQTT Configuration
BROKER = "localhost"                   # Update with your broker address
MQTT_PORT = 8883                       # Using port 8883
TOPIC_CMD = "heater/cmd"               # Topic to receive heater commands
TOPIC_TEMP = "heater/temperature"      # Topic to publish temperature readings
TOPIC_STAT = "heater/stat"             # Topic to publish stage info
TOPIC_RELAY = "usbrelay/cmd"            # Topic to control USB relay

def send_relay_command(client, relay, state):
    """
    Send relay command to turn on/off a relay.
    """
    payload = json.dumps({str(relay): state})
    client.publish(TOPIC_RELAY, payload)
    print("Published:", payload)

# --- Modbus Functions ---

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

def get_single_temp(ser):
    """
    Read a single temperature value.
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
    Read three temperature values.
    """
    payload = bytes.fromhex('010300280003')
    response = send_custom_modbus_request(ser, payload)
    if response and len(response) >= 9:
        data_bytes = response[3:9]
        temps = [int.from_bytes(data_bytes[i:i+2], byteorder='big') / 10.0 for i in range(0, len(data_bytes), 2)]
        return temps
    return [None, None, None]

def send_hex_command_open(ser, hex_command):
    """
    Send a full hex command (with CRC already embedded) using an already open serial port.
    """
    try:
        hex_command = hex_command.replace(" ", "")
        data = bytes.fromhex(hex_command)
        ser.write(data)
        ser.read(256)  # Optionally, read and discard any response.
    except Exception as e:
        print(f"Error sending hex command: {e}")


def run_heater_cycle():
    """
    Runs one heater cycle:
    """
    PORT = '/dev/ttyUSB0'
    BAUDRATE = 115200

    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
    except Exception as e:
        print(f"Error opening serial port: {e}")
        return

    mqtt_client.publish(TOPIC_STAT, json.dumps({"stage": "啟動"}))
    send_relay_command(mqtt_client, 1, "off")
    time.sleep(1)
    send_relay_command(mqtt_client, 3, "off")

    init_cmd = "02 10 00 64 00 02 04 00 00 00 01 3A F0"
    send_hex_command_open(ser, init_cmd)
    
    temp1 = get_single_temp(ser)
    temps = get_three_temps(ser)
    if temp1 is not None and None not in temps:
        output = {
            "temp1": temp1,
            "temp2": temps[0],
            "temp3": temps[1],
            "temp4": temps[2]
        }
        mqtt_client.publish(TOPIC_TEMP, json.dumps(output))
    else:
        print("Initial temperature reading failed.")

    heater_on_cmd = "02 10 00 6C 00 02 04 00 00 00 00 FA 96"
    send_hex_command_open(ser, heater_on_cmd)
    print("啟動")
    mqtt_client.publish(TOPIC_STAT, json.dumps({"stage": "開始加熱"}))

    cycle_duration = 20  # seconds
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
            mqtt_client.publish(TOPIC_TEMP, json.dumps(output))
        time.sleep(0.1)

    heater_off_cmd = "02 10 00 6C 00 02 04 00 00 00 01 3B 56"
    send_hex_command_open(ser, heater_off_cmd)
    print("結束")
    mqtt_client.publish(TOPIC_STAT, json.dumps({"stage": "停止加熱"}))
    send_relay_command(mqtt_client, 1, "on")
    time.sleep(1)
    send_relay_command(mqtt_client, 3, "on")

    extra_duration = 20  # seconds
    extra_start = time.time()
    while time.time() - extra_start < extra_duration:
        temp1 = get_single_temp(ser)
        temps = get_three_temps(ser)
        if temp1 is not None and None not in temps:
            output = {
                "temp1": temp1,
                "temp2": temps[0],
                "temp3": temps[1],
                "temp4": temps[2]
            }
            mqtt_client.publish(TOPIC_TEMP, json.dumps(output))
        time.sleep(0.1)

    mqtt_client.publish(TOPIC_STAT, json.dumps({"stage": "結束"}))
    send_relay_command(mqtt_client, 1, "off")
    time.sleep(1)
    send_relay_command(mqtt_client, 3, "off")
    time.sleep(1)
    ser.close()

def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Connected to MQTT Broker")
    client.subscribe(TOPIC_CMD)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8").strip())
        if payload.get("action", "").lower() == "heat":
            threading.Thread(target=run_heater_cycle).start()
    except Exception as e:
        print("Error processing MQTT message:", e)

mqtt_client = mqtt.Client(protocol=mqtt.MQTTv5)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def main():
    try:
        mqtt_client.connect(BROKER, MQTT_PORT)
    except Exception as e:
        print("Connection to MQTT Broker failed:", e)
        return

    mqtt_client.loop_forever()

if __name__ == "__main__":
    main()
