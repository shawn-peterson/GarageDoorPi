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
import time
import logging
import config as c
import garagelib as p
import paho.mqtt.client as mqtt

#Clear log
p.silentRemove(c.BASEPATH + '/logs/main.log')

logFormat = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=logFormat, filename=c.BASEPATH + '/logs/main.log', level=logging.DEBUG)
logging.info('Main start')

#Setup the GPIO pins
p.setupGPIO()

#Set number of seconds to wait between loops before sending data
loopDelay = c.LOOPDELAY

#Trigger the relay when a message is received.
def on_message(client, userdata, message):
    door = int(message.payload.decode("utf-8"))
    logging.info(message.topic + " - " + str(door))
    p.triggerRelay(c.DOOR1RELAYPIN if door == 1 else c.DOOR2RELAYPIN)


#Setup MQTT broker details
broker_address = p.getIp()
client = mqtt.Client("GarageMain")
client.username_pw_set("mqtt", c.MQTTPWORD)
client.on_message=on_message   
client.connect(broker_address, 1883, 60)
client.loop_start()

#Subscribe to door triggers
client.subscribe("garage/door/trigger")

if __name__ == '__main__':

    while True:
        try:
            sensors = p.readSensors()
            
            for i in range(len(sensors)):
                client.publish("garage/door/" + str(i+1) + "/status", p.sensorValueToText(sensors[i]))
            
            # Wait before doing it all again
            time.sleep(loopDelay)
        except:
            p.cleanupGPIO()
            quit()

    logging.info('Main end')
