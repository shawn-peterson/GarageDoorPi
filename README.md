# Raspberry Pi Garage Door Monitor and Controller

Borrowed heavily from:
* https://github.com/fezfox/pool
* https://fezfox.com/raspberry-pi-pool-temperature-monitor/

Which borrowed heavily from:
* https://bitbucket.org/MattHawkinsUK/rpispy-pool-monitor/overview
* https://www.raspberrypi-spy.co.uk/2017/07/pool-temperature-monitoring-and-pump-control-with-the-pi-zero-w/

I wanted to monitor and control the garage doors in my home using a Raspberry Pi and Home Assistant.

After looking at a varity of code samples, I decided to use the repo above as a starting point.

It included everything that I needed - a simple python framework, great setup guide, MQTT integration, and a local website.

## Hardware

### Raspberry Pi Zero WH

I'm using a [Raspberry Pi Zero WH](https://www.buyapi.ca/product/raspberry-pi-zero-wireless-wh-pre-soldered-header/) which includes headers - making it easier to connect everything together - no soldering required.

You will also need a [power adapter](https://www.buyapi.ca/product/wall-adapter-power-supply-5-25v-dc-2-4a-usb-micro-b/) and MicroSD card.

![Raspberry Pi Zero WH](https://www.dropbox.com/s/lhmufa7vozinh3h/IMG_20190602_201854.jpg?raw=1)

### 2 Channel Relay

I'm using a [2-Channel Relay](https://www.buyapi.ca/product/2-channel-relay-module-for-arduino-raspberry-pi-5v/) to control two garage door openers.

![2 Channel Relay](https://www.dropbox.com/s/ytfjolg0mnji5v5/IMG_20190602_201832.jpg?raw=1)

### Reed Switches

I'm using two [Wired Magnetic Reed Switches](https://www.amazon.ca/gp/product/B01M8JCGSO/ref=ppx_yo_dt_b_asin_title_o00_s01?ie=UTF8&psc=1) to detect when each garage door is opened.

![Reed Switch](https://www.dropbox.com/s/npaluotct1cxgpp/IMG_20190602_201915.jpg?raw=1)

### Wires

I purchased a large set of [Jumper Wires](https://www.amazon.ca/gp/product/B01C84WKN0/ref=ppx_yo_dt_b_asin_title_o01_s00?ie=UTF8&psc=1) for other projects. A small number of Female-to-Female jumper wires would be sufficient.

You will also need wires to run from the Relay to each garage door opener and from the Pi to each Reed Switch. I'm using regular speaker wire.

## GPIO PINs

I recommend [this site](https://pinout.xyz) for good diagrams of the Pi GPIO pins.

### 2 Channel Relay

My jumper is connected between JD-VOC and VOC.

* Pi GPIO Pin 2 (+5.0v) Relay VOC
* Pi GPIO Pin 6 (GND) to Relay GND.
* Pi GPIO Pin 32 (Door 1) to Relay IN1.
* Pi GPIO Pin 36 (Door 2) to Relay IN2.

### Reed Switches

* Pi GPIO Pin 37 (Door 1) to Reed Switch 1 (either connector).
* Pi GPIO Pin 39 (GND) to Reed Switch 1 (either connector).

* Pi GPIO Pin 40 (Door 2) to Reed Switch 2 (either connector).
* Pi GPIO Pin 34 (GND) to Reed Switch 2 (either connector).

![GPIO Jumpers](https://www.dropbox.com/s/9gzdfph8auxrrd9/IMG_20190604_205455.jpg?raw=1)

## Software Setup

### Setup SSH
The easiest way to use the pi is via SSH. Im assuming you've already got an SD card with Raspbian on it. Put that card into your computer however you do it and using a simple text editor create a blank file called `ssh` in the root. Then create another file called `wpa_supplicant.conf` with the following data:

```
country=us
update_config=1
ctrl_interface=/var/run/wpa_supplicant

network={
 scan_ssid=1
 ssid="YOUR_NETWORK_SSID"
 psk="YOUR_NETWORK_PASSWORD"
}
```

This means when you boot up your pi it will connect to your wifi, and you can ssh to it. You just need to know your pis IP address, and then you can call:
`ssh pi@YOUR_PI_IP_ADDRESS` and the default password is `raspberry`. Logging in will take you to the default non-root user "pi". This account's path is  `/home/pi/`.

### Install packages
Once logged into the pi, update:
```
sudo apt-get update
sudo apt-get -y upgrade
```
That will take 10-20 minutes...then install these packages:
```
sudo apt-get -y install git
sudo apt-get install python3-gpiozero
sudo apt-get -y install python3-pip
sudo pip3 install flask
sudo pip3 install requests
sudo pip3 install paho-mqtt
sudo apt-get install mosquitto
sudo apt-get install mosquitto-clients
```

### Clone the repo
My repo contains all the code, described below, to control two garage doors. Clone the git repo:
```
git clone https://github.com/shawn-peterson/GarageDoorPi.git
```

Navigate to it:
```
cd garage
```

Make the launcher executable:
```
chmod +x launcher.sh
```

### Setup cron
This will make the launcher code run everytime the pi reboots:
```
sudo crontab -e
```
Add this line to the bottom:
```
@reboot sh /home/pi/garage/launcher.sh > /home/pi/garage/logs/cronlog 2>&1
```

### Reboot the pi
Rebooting the pi will start the web page and logger:
```
sudo reboot now
```

## Software
Below are the two ways I am using this software:

1. View/control from a local website using flask
1. Publish and subscribe to a mosquitto channel, which can be monitored and triggered using [Home Assistant](https://www.home-assistant.io)

### Post to a webpage on your local network using flask
After reboot, launcher will run `webmain.py` which will use flask to create a web page on your local website. This can be accessed by navigating to you pi's IP address followed by port 5000:
```
YOUR_PI_IP_ADDRESS:5000
```
You will need to login with the username "admin" and the password "updown". You will see something like this:

![Website](https://www.dropbox.com/s/44sznn2p4agjpdu/Web.JPG?raw=1)

If not check your logs. If you have any familiarity with writing webpages, you can edit the files found in "templates".

The index page will display the most current status from the Reed Switches (open or closed). A button is also available to trigger the Relay to open/close the door.

### Publish and Subscribe to a mosquitto channel
The code in `poolmain.py` creates and publishes to a *MQTT broker*. This is the setup here

```
#Setup MQTT broker details
broker_address = p.getIp()
client = mqtt.Client("GarageMain")
client.username_pw_set("mqtt", c.MQTTPWORD)
client.on_message=on_message   
client.connect(broker_address, 1883, 60)
client.loop_start()
```

It also subscribes to triggers (to open/close) the door:
```
client.subscribe("garage/door/trigger")
```

In the main loop, you can see the status (Open/Closed) being published for each door:
```
client.publish("garage/door/" + str(i+1) + "/status", p.sensorValueToText(sensors[i]))
```

You can test this by logging into the pi with another terminal window, and *subscribing* to this channel:
```
mosquitto_sub -v -t "garage/door/#/status"
```

Every 30 seconds you will see this in your terminal window:
```
garage/door/1/status Closed
garage/door/2/status Closed
```

### Configure Home Assistant

Add the following to your `configuration.yaml` file:

```
mqtt:
  broker: YOUR_GARAGE_PI_IP
  port: 1883
  client_id: garage
  username: mqtt
  password: YOUR_GARAGE_PI_PASSWORD
  
cover:
  - platform: mqtt
    name: "Garage Door 1"
    command_topic: "garage/door/trigger"
    state_topic: "garage/door/1/status"
    payload_open: "1"
    payload_close: "1"
    state_open: "Open"
    state_closed: "Closed"
  - platform: mqtt
    name: "Garage Door 2"
    command_topic: "garage/door/trigger"
    state_topic: "garage/door/2/status"
    payload_open: "2"
    payload_close: "2"
    state_open: "Open"
    state_closed: "Closed"
```

The cover can be used to trigger the garage door using "up" and "down" buttons (based on the status). This can be added to the UI in a variety of ways.

#### Glance

In this view, clicking on a door will provide the "up" and "down" buttons to control it.

![Cover - Glance](https://www.dropbox.com/s/ds7l6b6mpx9t4lv/HA1.JPG?raw=1)

#### Entities

![Cover - Entities](https://www.dropbox.com/s/me9p474uh5fhzfs/HA2.JPG?raw=1)

## Installation

### Pi / Relay

Mount the Pi and Relay to something solid. I screwed it into some thick cardboard.

Mine was placed on top of one garage door opener - as it was close to a power plug.

I used a glue gun to attach the cardboard to the opener in a few spots - as the vibrations were moving it around.

![Mount](https://www.dropbox.com/s/yf952y2acehq02u/Mount.JPG?raw=1)

### 2 Channel Relay

Because my relay was placed on top of a garage door opener, I ran wires from each relay to garage door opener.

I'm using the Normally Open and Common Pin on each channel:

![Relay](https://www.dropbox.com/s/prfz9ojlij5vame/Relay.JPG?raw=1)

For my model of garage door opener, these are the two connections needed to trigger the door to open or close (1 and 2):

![Garage Door Opener](https://www.dropbox.com/s/ki9d17r4kaulkul/GarageDoorOpener.JPG?raw=1)

### Reed Switches

Mount the Reed Switches so they are close when the garage door is fully closed. I needed to add some wood to level things out. I used a glue gun to attach everything together.

Connect your wires from each switch to the appropriate jumpers from your Pi.

![Reed Switch](https://www.dropbox.com/s/zmxdil1wp5cwvek/ReedSwitch.JPG?raw=1)

### Dust Cover

Optional; but, you could design and add a dust cover:

![Complete](https://www.dropbox.com/s/oqlrppblpj211hm/Complete.JPG?raw=1)