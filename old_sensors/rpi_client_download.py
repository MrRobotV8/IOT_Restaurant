from thingspeak.ThingSpeakRequests import ThingSpeakRequests
from thingsboard.ThingsBoardRequests import ThingsBoardRequests
import json
from mqtt.MyMQTT import MyMQTT
import time
import paho.mqtt.publish as publish
import datetime
import threading

from config import local_broker_address
from config import local_broker_port
from config import access_tokens
from config import thingsboard_broker_address
from config import thingsboard_broker_port

############################################################
def ping_eq3():
    """
    sends a single mqtt message to synchronize the time with the ble eq3 valve. the valve sends a status message in response.
    :return:
    """
    now = datetime.datetime.now()
    payload = json.dumps({"value": [0x03, (int(now.year % 100)), (now.month), (now.day), (now.hour), (now.minute), (now.second)]})
    publish.single(access_tokens["stanza_23"] + "/eq3/rx", payload=json.dumps(payload),
                   qos=2, retain=False, hostname=local_broker_address, port=local_broker_port, client_id="Ping Valve")  # the MQTT client id to use. If "" or None, the Paho library will generate a client id automatically.
    print("publish single to local broker -> ping eq3: " + payload)
    threading.Timer(30*60, ping_eq3).start() # make it every 8 hours. 8*60*60, 3x a day
    print("send finished -> ping eq3" + " at " + str(datetime.datetime.now()))

# CONNECT TO LOCAL BROKER - don't subscribe.. just publish to local broker -> esp32 -> eq3
inst_mqtt_local_broker = MyMQTT(userNickname="rpi_download_local", userName="rpi_download_local",
                                broker=local_broker_address, port=local_broker_port)
inst_mqtt_local_broker.create_client()
time.sleep(0.5)
inst_mqtt_local_broker.connect()

# CONNECT TO THINGSBOARD BROKER - subscribe to rpc command
thingsboard_mqtt = {}
thingsboard_mqtt["stanza_23"] = MyMQTT(userNickname=access_tokens["stanza_23"], userName=access_tokens["stanza_23"],
                                broker=thingsboard_broker_address, port=thingsboard_broker_port, password="",
                                      localbroker=inst_mqtt_local_broker, linktype="download",
                                      subscription=["v1/devices/me/rpc/request/+"], subscription_qos=1)

thingsboard_mqtt["stanza_23"].create_client()
time.sleep(0.5)
thingsboard_mqtt["stanza_23"].connect()

ping_eq3()
run = True
while run:
    inst_mqtt_local_broker.loop()
    thingsboard_mqtt["stanza_23"].loop()