import json
import random
import time

import paho.mqtt.client as mqtt
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
                    datefmt='%d/%m/%Y %H:%M ',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class Publisher:
    def __init__(self, clientID, broker="mqtt.eclipse.org", port=1883, topic="", qos=1, token=''):
        self.client = clientID
        self.broker = broker
        self.port = port
        self.topic = topic
        self.qos = qos

        self.mqtt_client = mqtt.Client(self.client, clean_session=False)
        self.mqtt_client.username_pw_set(token)

    def on_connect(self, mqtt_client, userdata, flags, rc):
        errMsg = ""

        if rc == 0:
            logger.info(f"MQTT client {self.client} successfully connected to broker!")
            return str(rc)

        # If we go through this we had a problem with the connection phase
        elif 0 < rc <= 5:
            errMsg = "/!\ " + self.client + " connection to broker was " \
                                            "refused because of: "
            if rc == 1:
                errMsg.append("the use of an incorrect protocol version!")
            elif rc == 2:
                errMsg.append("the use of an invalid client identifier!")
            elif rc == 3:
                errMsg.append("the server is unavailable!")
            elif rc == 4:
                errMsg.append("the use of a bad username or password!")
            else:
                errMsg.append("it was not authorised!")
        else:
            errMsg = "/!\ " + self.client + " connection to broker was " \
                                            "refused for unknown reasons!"
        logger.error(errMsg)

    def OnDisconnect(self, mqtt_client, userdata, rc):
        if rc == 0:
            logger.info(f"MQTT client {self.client} successfully disconnected!")
        else:
            logger.warning(f"Unexpected disconnection of MQTT client {self.client}. " \
                           "Reconnecting right away!")

    def start(self):
        self.mqtt_client.connect(host=self.broker, port=self.port)
        self.mqtt_client.loop_start()
        logger.info(f"Client {self.client} connected to the Broker {self.broker}")

    def stop(self):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        logger.info(f"Client {self.client} disconnected from the Broker")

    def publish(self, msg):
        logger.info(f"Client {self.client} publishing {msg} on {self.topic}")
        self.mqtt_client.publish(self.topic, msg, self.qos)


if __name__ == '__main__':
    import sys
    import requests

    sys.path.insert(0, "C:/Users/Riccardo/Desktop/IOT_Restaurant/OrderEatWebApp/thingsboard")
    from main import ThingsDash
    THINGSBOARD_HOST = '139.59.148.149'
    ACCESS_TOKEN = '1ff2b990-5f52-11eb-bcf2-5f53f5d253b9_business:1'
    # ACCESS_TOKEN = "de066470-5e69-11eb-bcf2-5f53f5d253b9_business:1"
    td = ThingsDash()
    url_api = f"http://{THINGSBOARD_HOST}:8080/api/v1/{ACCESS_TOKEN}/telemetry"
    headers = {"X-Authorization": "Bearer " + td.jwt_token, "Content-Type": "application/json",
               "Accept": "application/json"}
    # client = mqtt.Client()
    # client.username_pw_set(ACCESS_TOKEN)
    # client.connect(THINGSBOARD_HOST, 1883)
    # client.loop_start()
    t = {'temperature_feedback': -6}
    print(t)
    x = requests.post(url_api, data=json.dumps(t))
    print(x)
    exit()
    topic = 'v1/devices/me/telemetry'
    client.publish(topic, json.dumps(t), 1)
    # l = [1, -1]
    # try:
    #     while True:
    #         t = {'temperature_feedback': random.choice(l)}
    #         print(t)
    #         # Sending humidity and temperature data to ThingsBoard
    #         client.publish('v1/devices/me/telemetry', json.dumps(t), 1)
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     pass

    client.loop_stop()
    client.disconnect()