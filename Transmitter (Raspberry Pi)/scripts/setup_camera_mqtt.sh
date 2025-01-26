#!/bin/bash

apt install -y mosquitto mosquitto-clients
systemctl enable mosquitto.service
mosquitto -v
pip install paho-mqtt
pip install opencv-python-headless==4.6.0.66
pip install numpy==1.26.1
sudo apt install -y libatlas-base-dev
sudo apt install -y libopenblas-dev