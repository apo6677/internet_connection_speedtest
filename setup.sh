#!/bin/bash
# setup.sh


# Kill processes that might interfere with monitor mode
sudo airmon-ng check kill

# Start monitor mode on interface wlo1
sudo airmon-ng start wlo1

# Run the wifi_doctor.py script with specified parameters
python3 wifi_doctor.py --interface wlo1mon --channels 1,9,11 --duration 10


#After successfully running it, reset everything to default settings

# Stop monitor mode on interface wlo1min
sudo airmon-ng stop wlo1mon

# Restart network-related services
sudo systemctl restart systemd-networkd
sudo systemctl restart NetworkManager
