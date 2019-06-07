#!/usr/bin/python3
#-----------------------------------------------------------
#
#
# Author : Matt Hawkins
# Modified by: fezfox
# Modified more by: Shawn Peterson
#
#
#-----------------------------------------------------------

BASEPATH = '/home/pi/garage'

# Defines the input GPIO pins the Reed Switch is connected to - one for each door.
DOOR1SENSORPIN = 37
DOOR2SENSORPIN = 40

# Defines the output GPIO pins the Relay is connected to - one for each door.
DOOR1RELAYPIN = 32
DOOR2RELAYPIN = 36

# Set the number of seconds between each loop.
# This determines how often the system checks the status of the garage door.
LOOPDELAY = 30

# Default username and password hash "updown"
# Use hashgenerator.py in utils to create hash for your password
USERNAME = 'admin'
USERHASH = 'c2878e56972df9029ce46271ce10f7b2de194900864d9b0b79f8323cf636e251'

# Flask needs a secret key or phrase to handle login cookie
FLASKSECRET = '7e8031df78fd55cba971df8d9f5740be'

# MQTT settings
# enter the MQTT password
MQTTPWORD = 'updown'
