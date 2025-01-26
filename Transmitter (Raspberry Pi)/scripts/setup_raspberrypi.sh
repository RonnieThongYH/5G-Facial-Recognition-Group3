#!/bin/bash
sudo apt purge modemmanager -y
sudo apt purge network-manager -y
sudo apt update && sudo apt upgrade
sudo apt install libglib2.0-dev libmbim-utils libmbim-glib-dev
sudo reboot