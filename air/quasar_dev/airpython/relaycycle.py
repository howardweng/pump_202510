import time
import json
import threading
import paho.mqtt.client as mqtt

# Configuration
BROKER = "localhost"      # Update with your broker address if needed
MQTT_PORT = 8883          # Using port 8883 (TLS) as required
TOPIC_CMD = "usbrelay/cmd"  # Topic to publish relay commands

# Create an event to signal when we are connected
connected_event = threading.Event()

def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Connected to MQTT Broker")
    connected_event.set()  # Signal that we're connected

def main():
    client = mqtt.Client(protocol=mqtt.MQTTv5)
    client.on_connect = on_connect

    try:
        client.connect(BROKER, MQTT_PORT)
    except Exception as e:
        print("Connection failed:", e)
        return

    client.loop_start()  # Start network loop in a background thread

    # Wait until connected (with a timeout if desired)
    if not connected_event.wait(timeout=5):
        print("Failed to connect within timeout period.")
        client.loop_stop()
        return

    try:
        while True:
            # Turn on relay 1
            payload1_on = json.dumps({"1": "on"})
            client.publish(TOPIC_CMD, payload1_on)
            print("Published:", payload1_on)
            time.sleep(1)

            # Turn on relay 3
            payload3_on = json.dumps({"3": "on"})
            client.publish(TOPIC_CMD, payload3_on)
            print("Published:", payload3_on)

            # Wait for 5 seconds
            time.sleep(5)

            # Turn off relay 1
            payload1_off = json.dumps({"1": "off"})
            client.publish(TOPIC_CMD, payload1_off)
            print("Published:", payload1_off)
            time.sleep(1)

            # Turn off relay 3
            payload3_off = json.dumps({"3": "off"})
            client.publish(TOPIC_CMD, payload3_off)
            print("Published:", payload3_off)

            # Wait 2 seconds before next cycle
            time.sleep(5)
    except KeyboardInterrupt:
        print("Exiting cycle...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
