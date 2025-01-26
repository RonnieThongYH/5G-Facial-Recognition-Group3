#!/bin/bash

curl https://www.linux-projects.org/listing/uv4l_repo/lpkey.asc |  apt-key add -
echo "deb https://www.linux-projects.org/listing/uv4l_repo/raspbian/stretch stretch main" | tee /etc/apt/sources.list.d/uv4l.list
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install uv4l-webrtc
uv4l --external-driver --device-name=video0
