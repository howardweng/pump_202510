# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **Air and Water Pump Testing Platform** (岡泰Air and Water Pump testing platform) built with React for the frontend and Python for hardware control. The system monitors and controls pumps, heaters, flow meters, and relay switches through MQTT messaging and Modbus serial communication.

## Development Commands

### Frontend (React Application)

```bash
# Install dependencies
cd air/quasar_dev
npm install

# Start development server (runs on port 3000)
npm start

# Build for production
npm build

# Launch in fullscreen Chrome (for kiosk/testing mode)
./start_chrome.sh

# Launch in fullscreen Firefox
./start_firefox.sh
```

### Python Backend Services

The Python scripts in `air/quasar_dev/airpython/` control hardware devices:

```bash
# Navigate to Python directory
cd air/quasar_dev/airpython

# Run main air/flow control
python3 air.py

# Run heater temperature control
python3 heater.py

# Run relay control
python3 relay.py

# Run temperature cycle tests
python3 heatcycle.py
python3 cycle2.py
python3 cycle3.py
python3 cycle4.py

# Run flow monitoring with MQTT
python3 flowmqtt.py

# Run relay control with MQTT
python3 relaymqtt.py

# Monitor all temperatures
python3 alltemp.py
```

## Architecture

### Frontend Architecture

**Technology Stack:**
- React 19.0.0
- React Router for navigation
- MQTT.js for real-time device communication
- Recharts for temperature/flow visualization
- Tailwind CSS for styling

**Key Pages:**
- `/` (root) - **Control.js**: Heater temperature control dashboard (加熱器溫度控制)
- `/flow` - **Flow.js**: Gas flow monitoring dashboard (氣體流量)

Both pages use MQTT to subscribe to device telemetry and send control commands.

**MQTT Configuration:**
- Located in `src/pages/config.js`
- Default: `ws://localhost:9500` (WebSocket MQTT broker)
- Credentials: `datavan_howard` / `datavanhoward123`

### Backend Architecture

**Python Hardware Control:**

The backend consists of independent Python scripts that:
1. Communicate with hardware via USB/Serial (Modbus RTU protocol)
2. Publish sensor data to MQTT broker
3. Subscribe to control commands from frontend

**Key Components:**
- **air.py** - Flow meter reading via Modbus (port `/dev/ttyUSB0`)
- **heater.py** - Temperature sensor monitoring
- **relay.py** - USB relay control (8-channel relay board)
- **flowmqtt.py** - Flow data publisher to MQTT topic `air/flow`
- **relaymqtt.py** - Relay state publisher to `usbrelay/state`
- **allmqtt.py** - Aggregated sensor data publisher
- **heatcycle.py / cycle*.py** - Automated test cycle scripts

**Hardware Interfaces:**
- **Flow Meter**: Modbus RTU over `/dev/ttyUSB0` (9600 baud, register 0x0000)
- **USB Relay**: Controlled via `usbrelay` binary in `air/quasar_dev/usbrelay/`
- **Temperature Sensors**: Read via custom Python modules

### MQTT Topics

The system uses MQTT for real-time bidirectional communication:

**Published by Python Backend:**
- `air/flow` - Instantaneous flow rate (L/min)
- `usbrelay/state` - Relay on/off states (8 channels)
- `heater/temp` - Temperature readings (4 sensors)
- `heater/stage` - Heater cycle stage info

**Subscribed by Frontend:**
- React pages subscribe to above topics for real-time display
- Charts update automatically when new data arrives

**Command Topics (Frontend → Backend):**
- Control commands sent from React UI to Python services
- Commands stored in `cmdRawList` state for logging

### Data Flow

1. **Sensor Reading**: Python scripts read Modbus/USB devices every second
2. **MQTT Publish**: Sensor data published to MQTT broker
3. **Frontend Subscribe**: React components receive updates via MQTT.js
4. **UI Update**: Charts and displays re-render with new data
5. **User Control**: User clicks buttons → MQTT commands sent → Python scripts execute hardware actions

### Docker Support

The project includes Docker image `howardweng/air:v0310h` with:
- Node.js environment
- Pre-configured development dependencies
- Project files at `/home/node/app/quasar_source/`

To pull and run:
```bash
docker pull howardweng/air:v0310h
docker run -d --name air_container howardweng/air:v0310h
docker exec -it air_container /bin/sh
```

## Important Files

- `src/pages/config.js` - MQTT broker connection settings
- `package.json` - Frontend dependencies and scripts
- `airpython/*.py` - Hardware control modules
- `NODE_RED_flow/` - Node-RED automation flows (alternative control interface)
- `start_chrome.sh` / `start_firefox.sh` - Fullscreen kiosk launcher scripts

## Notes

- **Port 3000**: React dev server
- **Port 9500**: MQTT WebSocket broker (must be running separately)
- **Serial Devices**: Ensure `/dev/ttyUSB*` permissions for Python scripts
- The system is designed for Chinese language UI (繁體中文)
- Temperature data staleness detection: Frontend shows "溫度偵測異常" if no updates for >2 seconds
- Relay data staleness detection: Frontend shows "繼電器偵測異常" if no updates for >2 seconds
