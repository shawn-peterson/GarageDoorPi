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
import datetime
import logging
import hashlib
import config as c
import garagelib as p
from flask import Flask, flash, redirect, request, render_template, url_for, session, escape, jsonify
import paho.mqtt.client as mqtt

app = Flask(__name__)
app.secret_key = c.FLASKSECRET

#Clear log
p.silentRemove(c.BASEPATH + '/logs/web.log')

logFormat = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=logFormat, filename=c.BASEPATH + '/logs/web.log', level=logging.DEBUG)
logging.info('Web start')

p.setupGPIO()

#setup MQTT broker details
broker_address = p.getIp()
client = mqtt.Client("GarageWeb")
client.username_pw_set("mqtt", c.MQTTPWORD)
client.connect(broker_address, 1883, 60)
client.loop_start()

@app.route('/')
def index():
    if 'username' in session:
        sensors = p.readSensors()

        for i in range(len(sensors)):
            sensors[i] = p.sensorValueToText(sensors[i])

        timeStamp = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        data = {'s': sensors, 'ts': timeStamp, 'user': escape(session['username'])}
        return render_template('index.html', data=data)
    else:
        return redirect(url_for('login'))


@app.route('/trigger')
def trigger():
    if 'username' in session:
        door = request.args.get('door', default = 1, type = int)
        logging.info("Triggering door: " + str(door))
        client.publish("garage/door/trigger", door)
        return jsonify(True)
    else:
        return redirect(url_for('login'))


@app.route('/logs/main')
def mainlogs():
    if 'username' in session:
        f = open(c.BASEPATH + '/logs/main.log', 'r')
        logs = p.tail(f, 100)
        data = {'logs': logs}
        return render_template('logs.html', data=data)
    else:
        return redirect(url_for('login'))


@app.route('/logs/web')
def weblogs():
    if 'username' in session:
        f = open(c.BASEPATH + '/logs/web.log', 'r')
        logs = p.tail(f, 100)
        data = {'logs': logs}
        return render_template('logs.html', data=data)
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get username and password from submitted form
        userName = escape(request.form['username'])
        passWord = escape(request.form['password'])
        # Convert password to hash and compare to stored hash
        passWordHash = hashlib.sha256(passWord.encode('utf-8')).hexdigest()
        if userName == c.USERNAME and passWordHash == c.USERHASH:
            session['username'] = 'admin'
            return redirect(url_for('index'))
        else:
            time.sleep(2)
            session.pop('username', None)
            flash('Sorry. Better luck next time.', 'danger')
    else:
        flash('Please enter your details.', 'info')
    return render_template('login.html')


@app.route('/logout')
def logout():
    # Remove username from the session
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
