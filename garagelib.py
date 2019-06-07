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

import os
import errno
import datetime
import requests
import config as c
import socket
import RPi.GPIO as GPIO
import time

def setupGPIO():
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(c.DOOR1SENSORPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(c.DOOR2SENSORPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(c.DOOR1RELAYPIN, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(c.DOOR2RELAYPIN, GPIO.OUT, initial=GPIO.HIGH)
    except:
        print("Problem setting pins")
        GPIO.cleanup()  
        quit()


def cleanupGPIO():
    GPIO.cleanup()


def readSensors():
    try:
        return [GPIO.input(c.DOOR1SENSORPIN), GPIO.input(c.DOOR2SENSORPIN)]
    except:
        print("Problem reading sensors")
        quit()


def triggerRelay(pin):
    try:
        GPIO.output(pin,False)
        time.sleep(0.5)
        GPIO.output(pin,True)
    except:
        print("Problem triggering relay")
        quit()


def sensorValueToText(val):
    return "Closed" if val == 0 else "Open"


def getIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def silentRemove(filename):
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


# Tail a file and get X lines from the end
def tail(f, lines=20, _buffer=4098):

    # place holder for the lines found
    lines_found = []

    # block counter will be multiplied by buffer
    # to get the block size from the end
    block_counter = -1

    # loop until we find X lines
    while len(lines_found) < lines:
        try:
            f.seek(block_counter * _buffer, os.SEEK_END)
        except IOError:  # either file is too small, or too many lines requested
            f.seek(0)
            lines_found = f.readlines()
            break

        lines_found = f.readlines()

        # decrement the block counter to get the
        # next X bytes
        block_counter -= 1

    return lines_found[-lines:]