import os
import cv2
import numpy as np
import requests
import datetime
import time
import pandas as pd
from options import Options
from threading import Thread, Lock, Event
from concurrent.futures import ThreadPoolExecutor
import paho.mqtt.client as mqtt
import base64
import paramiko
import send_cmd as send  # Import for LED control

# SSH Configuration for LED control
raspberry_pi_ip = "172.30.212.124"
username = "pi"
password = "raspberry"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(raspberry_pi_ip, username=username, password=password)

# Ensure LED is off at the start
send.turn_led_off(ssh)

# Paths to files for logging and storing the latest frame
LOG_FILE_PATH = r"C:\Users\chean\Downloads\5G-Facial-Recognition-Group3\5G-Facial-Recognition-Group3\recognition_logs.csv"
FRAME_FILE_PATH = r"C:\Users\chean\Downloads\5G-Facial-Recognition-Group3\5G-Facial-Recognition-Group3\latest_frame.jpg"

# Create an instance of the Options class
opts = Options()

# MQTT Configuration
MQTT_BROKER = "172.30.212.124"
MQTT_RECEIVE = "home/server"

# Global variables
frame = None
processed_frame = None
frame_lock = Lock()
processed_frame_lock = Lock()
stop_event = Event()

# ThreadPoolExecutor for face recognition requests
recognition_executor = ThreadPoolExecutor(max_workers=5)

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_RECEIVE)

def on_message(client, userdata, msg):
    global frame
    try:
        img = base64.b64decode(msg.payload)
        npimg = np.frombuffer(img, dtype=np.uint8)
        decoded_frame = cv2.imdecode(npimg, 1)

        # Resize the frame for faster processing
        resized_frame = cv2.resize(decoded_frame, (640, 480))
        with frame_lock:
            frame = resized_frame
    except Exception as e:
        print(f"Error decoding frame: {e}")

# MQTT Client Setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER)
client.loop_start()

# Asynchronous Face Recognition Request (using ThreadPoolExecutor)
def recognize_face_async(face_data, callback):
    try:
        response = requests.post(opts.endpoint("vision/face/recognize"),
                                 files={"image": face_data},
                                 data={"min_confidence": 0.6}).json()
        callback(response)
    except requests.exceptions.RequestException as e:
        print(f"Error during recognition: {e}")
        callback({})  # Handle failure with an empty response

# Callback function to handle face recognition results
def handle_recognition_result(result, current_frame, x_min, y_min):
    recognized_ID = "Not Recognized"
    status = "Not Recognized"

    if "predictions" in result:
        for user in result["predictions"]:
            recognized_ID = user.get("userid", "Not Recognized")

            if recognized_ID != "unknown" and recognized_ID != "Not Recognized":
                print(f"Recognized as: {recognized_ID}")  # Print to console
                status = "Recognized"
                send.turn_led_on(ssh)  # Turn LED on when face is recognized
            else:
                print("No recognized face detected.")  # Print if not recognized
                recognized_ID = "Not Recognized"
                status = "Not Recognized"
                send.turn_led_off(ssh)  # Turn LED off when face is not recognized

    # Add the recognized name near the bounding box
    cv2.putText(current_frame, recognized_ID, (x_min, y_min - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Log the recognition result and update CSV
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {"Timestamp": timestamp, "Name": recognized_ID, "Status": status}
    log_to_csv(log_entry)

    # Save the latest frame with face recognition (without console message)
    try:
        cv2.imwrite(FRAME_FILE_PATH, current_frame)
    except Exception as e:
        pass  # No print statement, just silently pass if an error occurs


# Log the recognition results to CSV (without console message)
def log_to_csv(log_entry):
    try:
        if os.path.exists(LOG_FILE_PATH):
            # Check if the file is empty
            if os.stat(LOG_FILE_PATH).st_size == 0:
                logs_df = pd.DataFrame(columns=["Timestamp", "Name", "Status"])
            else:
                logs_df = pd.read_csv(LOG_FILE_PATH)
        else:
            logs_df = pd.DataFrame(columns=["Timestamp", "Name", "Status"])

        # Append the new log entry
        log_df = pd.DataFrame([log_entry])
        logs_df = pd.concat([logs_df, log_df], ignore_index=True)

        # Write the updated DataFrame back to the CSV file
        logs_df.to_csv(LOG_FILE_PATH, index=False)

    except Exception as e:
        print(f"Error logging to CSV: {e}")


def process_frames():
    global frame, processed_frame

    while not stop_event.is_set():
        with frame_lock:
            if frame is None:
                time.sleep(0.01)
                continue
            current_frame = frame.copy()

        # Encode the frame for face detection
        _, encoded_frame = cv2.imencode('.jpg', current_frame)

        try:
            # Send the frame to the server for face detection
            response = requests.post(opts.endpoint("vision/face"),
                                     files={"image": encoded_frame.tobytes()}).json()

            predictions = response.get("predictions", [])
            if not predictions:
                send.turn_led_off(ssh)  # Turn LED off when no face is detected
                with processed_frame_lock:
                    processed_frame = current_frame.copy()
                    cv2.putText(processed_frame, "Not Recognized", (10, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                continue

            # Process detected faces
            for pred in predictions:
                x_min, y_min, x_max, y_max = pred["x_min"], pred["y_min"], pred["x_max"], pred["y_max"]
                cv2.rectangle(current_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

                # Extract and encode the face region for recognition
                face_region = current_frame[y_min:y_max, x_min:x_max]
                _, face_encoded = cv2.imencode('.jpg', face_region)

                # Recognize face asynchronously using ThreadPoolExecutor
                recognition_executor.submit(recognize_face_async, face_encoded.tobytes(),
                                            lambda result: handle_recognition_result(result, current_frame, x_min, y_min))

            # Update the processed frame with bounding boxes drawn
            with processed_frame_lock:
                processed_frame = current_frame.copy()

        except Exception as e:
            pass  # No print statement, just silently pass if an error occurs

        time.sleep(0.01)

# Display Live Stream
def display_frames():
    global frame, processed_frame

    while not stop_event.is_set():
        with frame_lock:
            if frame is None:
                time.sleep(0.01)
                continue
            current_frame = frame.copy()

        # Add timestamp to the frame
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(current_frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Display processed frame if available
        with processed_frame_lock:
            if processed_frame is not None:
                current_frame = processed_frame.copy()

        # Display the frame
        cv2.imshow("Live Stream", current_frame)

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            break

    cv2.destroyAllWindows()

# Main Function
if __name__ == "__main__":
    # Start the face detection and recognition thread
    detection_thread = Thread(target=process_frames, daemon=True)
    detection_thread.start()

    # Start the live stream thread
    display_frames()

    try:
        detection_thread.join()
    except KeyboardInterrupt:
        pass  # No print statement, just pass if interrupted
    finally:
        client.loop_stop()
        stop_event.set()
        send.turn_led_off(ssh)  # Turn LED off when the program ends
        cv2.destroyAllWindows()