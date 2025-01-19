# Import necessary modules and packages
import os
import cv2
import numpy as np
import requests
import datetime
from options import Options
from imutils.video import VideoStream
import paho.mqtt.client as mqtt
import base64

# Create an instance of the Options class
opts = Options()
    
#Put your name
name = "j"

MQTT_BROKER = "100.70.118.250"
MQTT_RECEIVE = "home/server"


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_RECEIVE)

frame = np.zeros((240, 320, 3), np.uint8)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global frame
    # Decoding the message
    img = base64.b64decode(msg.payload)
    # converting into numpy array from buffer
    npimg = np.frombuffer(img, dtype=np.uint8)
    # Decode to Original Frame
    frame = cv2.imdecode(npimg, 1)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER)

# Starting thread which will receive the frames
client.loop_start()


# Define function to register a face !!!
def register_face(img_path, user_id):
    # This function sends the face image and the user id to the server to register !!!

    # Build the file path to the image
    filepath = os.path.join(opts.imageDir, img_path)

    # Read the image data as bytes
    image_data = open(filepath, "rb").read()

    try:
        # Send the image & user_id to the server to register !!!
        response = requests.post(opts.endpoint("vision/face/register"),
                                files={"image": image_data},
                                data={"userid": user_id}).json()
        # Print the response received from the server !!!
        print(f"Registration response: {response}")
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


# Define the main function
def main():

    global frame
    # Captures the video frames from the camera,
    # detects the faces in the frames,
    # and sends them to the server with user ids for registration. !!!

    # Create an instance of the Options class
    opts = Options()

    # Initialise capturing video from the default camera
    # 0 for default camera, 1 if you have installed third-party webcam apps
    #cap = VideoStream(0).start()
    #cap = VideoStream('rtsp://100.107.9.202:8080/').start()

    # Initialize variables to keep track of frame count, predictions, and frame skipping
    frame_index = 0
    predictions = {}
    skip_frame = 5

    # Begin the main loop to process frames from the camera
    while True:
        # Check for the 'q' key to exit the program
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Stop capturing...")
            break

         # Capture a frame from the camera
        if frame is None:
            print("Camera closed")
            break
        
        # Increment the frame count
        frame_index += 1

        # Skip some frames to reduce the processing load
        if skip_frame > 1:
            if frame_index % skip_frame != 0:
                continue
        
         # Get the current timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add the timestamp to the frame
        cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)
        
        # Encode the frame as a JPEG image
        retval, new_frame = cv2.imencode('.jpg', frame)

        try:
            # Send the frame to the server to detect the face(s) in the frame
            response = requests.post(opts.endpoint("vision/face"),
                                    files={"image": new_frame}).json()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        
        # Extract the detections from the response
        predictions = response['predictions']

        # Get the number of predictions (i.e. faces detected)
        num_prediction_json = len(predictions)

        # Loop over the predictions and draw a rectangle around each face in the frame
        if num_prediction_json == 1:
            for i in range(num_prediction_json):
                blue, green, red = 0, 0, 255
                frame = cv2.rectangle(frame,
                                      (predictions[i]['x_min'], predictions[i]['y_min']),
                                      (predictions[i]['x_max'], predictions[i]['y_max']),
                                      (blue, green, red), 2)
                # Save the frame as an image file named "image.jpg"
                cv2.imwrite('image.jpg', frame)

                # Register the face with the user ID 
                register_face("image.jpg", name)

                # Add result right next to the rectangle
                cv2.putText(frame, name, (predictions[i]['x_min'], predictions[i]['y_min']-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        else:
            print('Make sure you are showing your face ONLY and CLEARLY...')

        cv2.imshow('Image Viewer', frame)

    # Release the camera and close all windows
    cv2.destroyAllWindows()
    client.loop_stop()

    
# Call the main function if this script is being run directly
if __name__ == "__main__":
    main()
