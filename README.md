# 5G Facial Recognition Door Access System

## Overview
This project implements a **5G Facial Recognition Door Access System** leveraging Raspberry Pi, Multi-Edge Computing (MEC), and MQTT for real-time communication and control. The system captures live video from a Raspberry Pi camera, processes it via an AI-powered facial recognition API, and unlocks the door when a recognized face is detected. An LED on the Raspberry Pi indicates the success or failure of the recognition process.

---

## Features
- **5G Connectivity:** Enables high-speed, low-latency communication between devices.
- **Facial Recognition:** Utilizes a local API running on `http://localhost:32168` for face detection and recognition.
- **MQTT Integration:** Transfers video frames and control signals efficiently.
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
├── Receiver (MEC)/
│   ├── scripts/
│   │   ├── recognition.py            # Receives frames and performs face recognition
│   │   ├── registration.py           # Registers new faces to the recognition system
│   │   ├── options.py                # Configuration for the API and directories
│   │   ├── LED_SSH.py                # Controls the Raspberry Pi's LED via SSH
│   │   ├── AT_command.py             # Sends AT commands to the 5G module
├── logs/                             # Logs for debugging and monitoring
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

### Raspberry Pi Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/RonnieThongYH/5G-Facial-Recognition-Group3.git
   cd 5G-Facial-Recognition-Group3/Transmitter\ (Raspberry\ Pi)/scripts
   ```
2. Run the setup script:
   ```bash
   ./setup_raspberrypi.sh
   ```
3. Start the MQTT publisher:
   ```bash
   python3 send_frames_mqtt.py
   ```

### MEC Setup
1. Navigate to the MEC scripts directory:
   ```bash
   cd 5G-Facial-Recognition-Group3/Receiver\ (MEC)/scripts
   ```
2. Ensure the API is running on `http://localhost:32168`.
3. Run the face recognition script:
   ```bash
   python3 recognition.py
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

4. **Output:**
   - The MEC displays the processed video feed with bounding boxes and labels for recognized faces.

---

## Scripts and Their Roles
### Transmitter (Raspberry Pi)
- **`send_frames_mqtt.py`:** Captures video frames and publishes them to the MQTT broker.
- **`configure_5g_module.py`:** Configures the 5G module for connectivity.
- **`setup_camera_mqtt.sh`:** Installs dependencies for MQTT and OpenCV.

### Receiver (MEC)
- **`recognition.py`:** Handles frame reception, facial recognition, and LED control.
- **`options.py`:** Configures API endpoints and directories.
- **`LED_SSH.py`:** Sends SSH commands to the Raspberry Pi for LED control.

---

## Future Improvements
- Enhance error handling and logging.
- Optimize frame transfer and processing.
- Integrate additional 5G features for scalability.
- Extend functionality to support multiple devices and cameras.

---

## Authors
- **Ronnie Thong**
- **Group 3 Members**

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
