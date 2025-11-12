import paho.mqtt.client as mqtt
import subprocess
import json
import time

BROKER = "localhost"
PORT = 8883
TOPIC_STAT = "usbrelay/stat"
TOPIC_CMD = "usbrelay/cmd"

def get_relay_status():
    """Fetch the current status of all relays and return as a JSON-like dictionary."""
    try:
        output = subprocess.check_output(["usbrelay"], universal_newlines=True)
        relays = {}
        for line in output.strip().split("\n"):
            name, status = line.split("=")
            simple_name = name.split("_", 1)[-1]
            relays[simple_name] = "ON" if int(status) == 1 else "OFF"
        return relays
    except subprocess.CalledProcessError as e:
        print(f"Error fetching relay status: {e}")
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

def process_command(client, cmd_payload):
    """Process the JSON command payload to control relays."""
    try:
        commands = json.loads(cmd_payload)
        all_command = commands.get("all", None)

        if all_command:
            # Override all relays
            state = 1 if all_command.upper() == "ON" else 0
            relays = get_relay_status()
            for relay in relays:
                toggle_relay(relay, state)
            # Publish updated state
            updated_status = {relay: all_command.upper() for relay in relays}
            client.publish(TOPIC_STAT, json.dumps(updated_status), retain=False)
        else:
            # Handle individual relay commands
            for relay, action in commands.items():
                state = 1 if action.upper() == "ON" else 0
                toggle_relay(relay, state)
            # Publish updated state
            updated_status = get_relay_status()
            client.publish(TOPIC_STAT, json.dumps(updated_status), retain=False)

    except json.JSONDecodeError as e:
        print(f"Invalid JSON command received: {cmd_payload}. Error: {e}")
    except Exception as e:
        print(f"Error processing command: {e}")

def on_connect(client, userdata, flags, rc):
    """Callback when the MQTT client connects to the broker."""
    print("Connected to MQTT Broker!")
    client.subscribe(TOPIC_CMD)  # Subscribe to the command topic

def on_message(client, userdata, msg):
    """Callback when an MQTT message is received."""
    topic = msg.topic
    if topic == TOPIC_CMD:
        cmd_payload = msg.payload.decode("utf-8").strip()
        process_command(client, cmd_payload)

def main():
    """Main function to set up MQTT communication and relay control."""
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT)
        client.loop_start()

        while True:
            # Periodically publish the state of all relays
            relays = get_relay_status()
            client.publish(TOPIC_STAT, json.dumps(relays), retain=False)
            time.sleep(10)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
