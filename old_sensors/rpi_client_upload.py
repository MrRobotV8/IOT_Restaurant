from thingspeak.ThingSpeakRequests import ThingSpeakRequests
from thingsboard.ThingsBoardRequests import ThingsBoardRequests
import json
from mqtt.MyMQTT import MyMQTT
import time
from RPi_core_temperature import RPi_core_temperature
from RPi_speedtest import RPi_speedtest
import paho.mqtt.publish as publish
import threading
import math as m
import datetime
import psutil

from config import local_broker_address
from config import local_broker_port
from config import access_tokens
from config import thingsboard_broker_address
from config import thingsboard_broker_port

############################################################
MULTIPLES = ["B", "k{}B", "M{}B", "G{}B", "T{}B", "P{}B", "E{}B", "Z{}B", "Y{}B"]
def humanbytes(i, binary=False, precision=2):
    base = 1024 if binary else 1000
    multiple = m.trunc(m.log2(i) / m.log2(base))
    value = i / m.pow(base, multiple)
    suffix = MULTIPLES[multiple].format("i" if binary else "")
    return f"{value:.{precision}f} {suffix}"

def send_MQTT_with_RPi_attributes_to_thingsboard():
    try:
        print("send_MQTT_with_RPi_attributes_to_thingsboard running")
        internet_data = RPi_speedtest()
        rpi_data = {"cpu_usage": psutil.cpu_percent(), "memory_usage": psutil.virtual_memory()[2] ,"core_temperature": RPi_core_temperature(), "download_speed": "{:0.2f}".format(internet_data[0]/1e6),
                    "upload_speed": "{:0.2f}".format(internet_data[1]/1e6), "ISP":internet_data[2], "last_update": str(datetime.datetime.now())}
        print("publish.single thingsboard_mqtt->RPi_device_attributes")
        print(json.dumps(rpi_data))
        publish.single("v1/devices/me/telemetry", payload=json.dumps(rpi_data),
                       qos=1, retain=False, hostname=thingsboard_broker_address,
                       port=thingsboard_broker_port, auth={'username': access_tokens["rpi_togliatti"], 'password': ""})
        print("thingsboard_mqtt send finished->RPi_device_attributes" + " " + str(datetime.datetime.now()))
        threading.Timer(15*60, send_MQTT_with_RPi_attributes_to_thingsboard).start()
    except:
        pass

## initialize thingsboard http api
inst_http_thingsboard = ThingsBoardRequests(devices=access_tokens)

inst_mqtt_local_broker = MyMQTT(userNickname="rpi_upstream", userName="rpi_upstream", devices=access_tokens,
                                broker=local_broker_address, port=local_broker_port,
                                thingsboard_mqtt_broker_address=thingsboard_broker_address,
                                subscription=["#"], subscription_qos=2, linktype="upload")

inst_mqtt_local_broker.create_client()
time.sleep(0.5)
inst_mqtt_local_broker.connect()

send_MQTT_with_RPi_attributes_to_thingsboard()

run = True
while run:
    inst_mqtt_local_broker.loop()