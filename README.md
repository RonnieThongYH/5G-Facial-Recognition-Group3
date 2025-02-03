# 5G Facial Recognition Door Access System

## Overview
This project implements a **5G Facial Recognition Door Access System** leveraging Raspberry Pi, Multi-Edge Computing (MEC), and MQTT for real-time communication and control. The system captures live video from a Raspberry Pi camera, processes it via an AI-powered facial recognition API, and unlocks the door when a recognized face is detected. An LED on the Raspberry Pi indicates the success or failure of the recognition process.

---

## Features
- **5G Connectivity:** Enables high-speed, low-latency communication between devices.
- **Facial Recognition:** Utilizes a local API running on `http://localhost:32168` for face detection and recognition.
- **MQTT Integration:** Transfers video frames and control signals efficiently.
- **Data Visualization:** Provides graphical insights via the dashboard and logs.
- **Device-to-Device Communication:** Raspberry Pi (transmitter) communicates with the MEC (receiver) for video processing and LED control.

---

## Folder Structure
```
5G-Facial-Recognition-Group3/
├── Transmitter (Raspberry Pi)/
│   ├── scripts/
│   │   ├── send_frames_mqtt.py       # Publishes video frames to MQTT
│   │   ├── configure_5g_module.py    # Sets up 5G module configuration
│   │   ├── setup_camera_mqtt.sh      # Installs MQTT and camera dependencies
│   │   ├── setup_raspberrypi.sh      # Initial setup for Raspberry Pi
│   │   ├── start_5g_network.sh       # Starts the 5G network connection
│   │   ├── start_camera_stream.sh    # Streams video via RTSP
│   │   ├── start_webrtc.sh           # Starts UV4L WebRTC service
│   │   ├── webrtc_install.sh         # Installs UV4L WebRTC dependencies
├── Receiver (MEC)/
│   ├── scripts/
│   │   ├── recognition.py            # Receives frames and performs face recognition
│   │   ├── registration.py           # Registers new faces to the recognition system
│   │   ├── options.py                # Configuration for the API and directories
│   │   ├── LED_SSH.py                # Controls the Raspberry Pi's LED via SSH
│   │   ├── AT_command.py             # Sends AT commands to the 5G module
│   │   ├── dashboard.py              # Displays data visualization for performance tracking
│   │   ├── matplot.py                # Generates graphs using Matplotlib
│   │   ├── send_cmd.py               # Sends additional command controls to devices
├── Data/
│   ├── recognition_logs.csv          # Logs of recognition events
│   ├── latest_bar_chart.png          # Visualization of latest recognition stats
│   ├── latest_frame.jpg              # Most recent captured frame
```

---

## Setup and Installation

### Prerequisites
- **Hardware:**
  - Raspberry Pi with 5G hat
  - Pi camera module
  - LED and resistors
  - MEC (e.g., laptop with local API server)
- **Software:**
  - Python 3.8+
  - MQTT Broker (e.g., Mosquitto)
  - Thonny Python IDE
  - Required dependencies in `requirements.txt`

### Raspberry Pi Setup
#### 1. Hardware Setup
1. Connect the Raspberry Pi and 5G Hat with the USB connector, attach the antennas.
2. Connect the Raspberry Pi to a monitor, keyboard, and mouse. Power on the Raspberry Pi.
3. Connect to the "SPStudent" Wi-Fi network (refer to Lab 3 for details).

#### 2. Clone the Repository
```bash
git clone https://github.com/RonnieThongYH/5G-Facial-Recognition-Group3.git
cd 5G-Facial-Recognition-Group3/Transmitter\ \(Raspberry\ Pi\)/scripts
```

#### 3. Run the Setup Script
```bash
./setup_raspberrypi.sh
```

#### 4. Start the 5G Network
```bash
python3 configure_5g_module.py
./start_5g_network.sh
```

#### 5. Camera and MQTT Setup
For MQTT:
```bash
./setup_camera_mqtt.sh
```

#### 6. Restart MQTT Service (If Necessary)
After setting up the Raspberry Pi, the MQTT service may need to be restarted to ensure it listens on the correct network interface.

1. Kill any existing processes on port 1883:
   ```bash
   sudo fuser -k 1883/tcp
   ```
2. Restart the Mosquitto service:
   ```bash
   sudo systemctl restart mosquitto
   ```
3. Verify that Mosquitto is listening on `0.0.0.0:1883` instead of `127.0.0.1`:
   ```bash
   sudo netstat -tulnp | grep mosquitto
   ```
4. If the service is not listening on `0.0.0.0:1883`, check the Mosquitto configuration:
   ```bash
   sudo nano /etc/mosquitto/mosquitto.conf
   ```
   Ensure the following line is present or updated:
   ```
   listener 1883 0.0.0.0
   ```
   Then restart Mosquitto again:
   ```bash
   sudo systemctl restart mosquitto
   ```

#### 7. Send Frames to Topic
```bash
python3 send_frames_mqtt.py
```

For RTSP:
```bash
./start_camera_stream.sh
```

### MEC Setup
```bash
cd 5G-Facial-Recognition-Group3/Receiver\ \(MEC\)/scripts
python3 AT_command.py
```
Run the recognition system:
```bash
python3 recognition.py
```
To register new faces:
```bash
python3 registration.py
```
To view the dashboard:
```bash
python3 dashboard.py
```

---

## Workflow
1. **Frame Capture (Raspberry Pi):**
   - The Raspberry Pi captures video frames using the camera.
   - Frames are published to the MQTT broker (`home/server` topic).

2. **Frame Reception and Processing (MEC):**
   - The MEC subscribes to the MQTT topic and receives the frames.
   - Frames are sent to the facial recognition API for processing.

3. **LED Control:**
   - The MEC sends SSH commands to the Raspberry Pi to turn the LED on or off based on recognition results.

4. **Data Visualization:**
   - The system logs recognition events (`recognition_logs.csv`).
   - `dashboard.py` generates real-time graphical reports.

---

## Scripts and Their Roles
### Transmitter (Raspberry Pi)
- **`send_frames_mqtt.py`** – Publishes video frames to MQTT.
- **`configure_5g_module.py`** – Configures the 5G module.
- **`setup_camera_mqtt.sh`** – Installs dependencies for MQTT and OpenCV.
- **`setup_raspberrypi.sh`** – Configures Raspberry Pi.
- **`start_5g_network.sh`** – Establishes 5G network connection.
- **`start_camera_stream.sh`** – Streams video via RTSP.
- **`start_webrtc.sh`** – Starts WebRTC service.
- **`webrtc_install.sh`** – Installs WebRTC dependencies.

### Receiver (MEC)
- **`AT_command.py`** – Configures the 5G connection.
- **`recognition.py`** – Handles facial recognition and LED control.
- **`registration.py`** – Registers new faces.
- **`options.py`** – Configures API endpoints and directories.
- **`LED_SSH.py`** – Sends SSH commands for LED control.
- **`dashboard.py`** – Displays real-time recognition performance.
- **`matplot.py`** – Generates performance graphs.
- **`send_cmd.py`** – Sends additional commands to devices.

---

## Future Improvements
- Improve error handling and logging.
- Enhance dashboard functionality.
- Optimize frame transfer and processing.
- Integrate additional 5G features.

---

## Authors
- **Ronnie Thong**
- **Cheang Kai Yang**
- **May**
- **Chuu**

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.




