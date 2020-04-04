## https://gist.github.com/shiyazt/ea9942d9705948df19d7d13aafab4f04

#Possible values for client.state()
#define MQTT_CONNECTION_TIMEOUT     -4
#define MQTT_CONNECTION_LOST        -3
#define MQTT_CONNECT_FAILED         -2
#define MQTT_DISCONNECTED           -1
#define MQTT_CONNECTED               0
#define MQTT_CONNECT_BAD_PROTOCOL    1
#define MQTT_CONNECT_BAD_CLIENT_ID   2
#define MQTT_CONNECT_UNAVAILABLE     3
#define MQTT_CONNECT_BAD_CREDENTIALS 4
#define MQTT_CONNECT_UNAUTHORIZED    5


# This Program illustrates the Client Side RPC on ThingsBoard IoT Platform
# Paste your ThingsBoard IoT Platform IP and Device access token
# Client_Side_RPC.py : This program will illustrates the Client side
import os
import time
import sys
import json
import random
import paho.mqtt.client as mqtt

# Thingsboard platform credentials
THINGSBOARD_HOST = 'demo.thingsboard.io'
ACCESS_TOKEN = "xP3IxdGAgQR7yUZuZT24"
DEVICE_ID = "0e6ade00-818c-11e9-a0d4-777cc84329e8"

# MQTT on_connect callback function
def on_connect(client, userdata, flags, rc):
    print("rc code:", rc)
    client.subscribe('v1/devices/me/rpc/response/+')
    request = {"humidity": "11", "temperature": "22"}
    client.publish('v1/devices/me/request/1', json.dumps(request))
    print('-')

# MQTT on_message caallback functionACCESS_TOKEN
def on_message(client, userdata, msg):
    print('Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload))

# start the client instance
client = mqtt.Client(client_id=DEVICE_ID)
# registering the callbacks
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(ACCESS_TOKEN, password=None)
client.connect(THINGSBOARD_HOST, 1883, 60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()

# import requests
# r = requests.post("http://demo.thingsboard.io/api/v1/{}/telemetry".format(devices["dht11_21"]), data=json.dumps(
#     {"temperature": 10, "humidity": 10}),
#               headers={'Content-type': 'application/json'})
#
# print(r.status_code, r.reason)