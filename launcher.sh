#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script
cd /home/pi/garage
python3 /home/pi/garage/garagemain.py &
python3 /home/pi/garage/garageweb.py &