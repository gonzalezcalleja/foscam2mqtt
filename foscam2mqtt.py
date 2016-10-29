#!/usr/bin/env python

import paho.mqtt.client as paho
import json
import time
import argparse

from foscam import FoscamCamera

lastMotionDetectAlarm = -1
lastSoundAlarm = -1
lastInfraLedState = -1
lastTimePublish = 0

parser = argparse.ArgumentParser()

parser.add_argument("-N", "--name", help="foscam camera name")
parser.add_argument("-H", "--host", help="foscam camera host/ip")
parser.add_argument("-p", "--port", help="foscam camera port", type=int)
parser.add_argument("-u", "--username", help="foscam camera username")
parser.add_argument("-w", "--password", help="foscam camera password")
parser.add_argument("-M", "--mqtthost", help="mqtt host")
parser.add_argument("-P", "--mqttport", help="mqtt port", type=int)
parser.add_argument("-U", "--mqttusername", help="mqtt camera username")
parser.add_argument("-W", "--mqttpassword", help="mqtt camera password")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="increase output verbosity")
args = parser.parse_args()

def print_devinfo(returncode, params):
#    print 'print_devinfo'
    global lastMotionDetectAlarm
    global lastSoundAlarm
    global lastInfraLedState
    global lastTimePublish

    if returncode != 0:
        print 'Failed to get DEVInfo!'
        time.sleep(30)
        return
    
    data = {}
    data['motionDetectAlarm'] = params['motionDetectAlarm']
    data['soundAlarm'] = params['soundAlarm']
    data['infraLedState'] = params['infraLedState']

    json_data = json.dumps(data)
    #print 'json_data %s' % (json_data)
    
    if any( [data['motionDetectAlarm'] != lastMotionDetectAlarm , data['soundAlarm'] != lastSoundAlarm, data['infraLedState'] != lastInfraLedState, (time.time() - lastTimePublish) > 10.0]):
    	client.publish("ipcamera/"+args.name, json_data, qos=0)
    	lastMotionDetectAlarm = data['motionDetectAlarm']
    	lastSoundAlarm = data['soundAlarm']
    	lastInfraLedState = data['infraLedState']
    	lastTimePublish = time.time()

client = paho.Client(client_id="", clean_session=True, userdata=None, protocol="MQTTv31")
client.username_pw_set(args.mqttusername, args.mqttpassword)
client.connect(args.mqtthost, 1883, 5)
client.loop_start()

mycam = FoscamCamera(args.host, args.port, args.username, args.password, daemon=True, verbose=args.verbose)

while True:
   resultado = mycam.get_dev_state(print_devinfo)
   time.sleep(1)