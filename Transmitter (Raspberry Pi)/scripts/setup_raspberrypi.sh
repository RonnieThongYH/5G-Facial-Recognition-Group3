#!/bin/bash
apt purge modemmanager -y
apt purge network-manager -y
apt update && apt upgrade
apt install libglib2.0-dev libmbim-utils libmbim-glib-dev
reboot