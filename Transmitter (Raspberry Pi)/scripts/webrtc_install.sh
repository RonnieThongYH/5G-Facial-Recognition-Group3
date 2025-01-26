#!/bin/bash

curl https://www.linux-projects.org/listing/uv4l_repo/lpkey.asc |  apt-key add -
echo "deb https://www.linux-projects.org/listing/uv4l_repo/raspbian/stretch stretch main" | tee /etc/apt/sources.list.d/uv4l.list
apt-get update && apt-get upgrade
apt-get install uv4l-webrtc
uv4l --external-driver --device-name=video0
