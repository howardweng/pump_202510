import subprocess
import time

def get_relay_status():
    """Fetch the current status of all relays."""
    try:
        output = subprocess.check_output(["usbrelay"], universal_newlines=True)
        relays = {}
        for line in output.strip().split("\n"):
            name, status = line.split("=")
            relays[name] = int(status)
        return relays
    except subprocess.CalledProcessError as e:
        print(f"Error fetching relay status: {e}")
        return {}

def toggle_relay(relay, state):
    """Toggle a specific relay ON (1) or OFF (0)."""
    try:
        command = f"usbrelay {relay}={state}"
        subprocess.run(command.split(), check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error toggling relay {relay}: {e}")

def main():
    """Toggle all relays ON and OFF with a 1-second delay."""
    relays = get_relay_status()
    if not relays:
        print("No relays detected.")
        return

    # Turn all relays ON one by one
    print("Turning all relays ON...")
    for relay in relays:
        toggle_relay(relay, 1)
        time.sleep(1)

    # Turn all relays OFF one by one
    print("Turning all relays OFF...")
    for relay in relays:
        toggle_relay(relay, 0)
        time.sleep(1)

if __name__ == "__main__":
    main()
