import paho.mqtt.client as mqtt
import logging
import datetime
import json

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
                    datefmt='%d/%m/%Y %H:%M ',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class Subscriber:
    def __init__(self, clientID, broker="mqtt.eclipse.org", port=1883, topic="", qos=1, token=""):
        self.msg_body = {}
        self.clientID_ = clientID
        self.broker_ = broker
        self.port_ = port
        self.mqtt_client = mqtt.Client(self.clientID_, clean_session=False)
        self.mqtt_client.username_pw_set(token)
        self.isSubscribe_ = False
        self.topic_ = topic
        self.qos_ = qos

        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        logger.info(f"User {self.clientID_} initialized.")

    def on_connect(self):
        pass

    def on_message(self, client, userdata, msg):
        logger.info("New Message!")
        self.msg_body = json.loads(msg.payload)

    def on_disconnect(self):
        pass

    def subscribe(self):
        self.mqtt_client.subscribe(topic=self.topic_, qos=self.qos_)
        self.isSubscribe_ = True
        logger.info(f"Client {self.clientID_} subscribe to the topic: {self.topic_}")

    def start(self):
        self.mqtt_client.connect(host=self.broker_, port=self.port_)
        self.mqtt_client.loop_start()
        # logger.info(f"Client {self.clientID_} connected to the Broker {self.broker_}")

    def stop(self):
        if self.isSubscribe_:
            self.mqtt_client.unsubscribe(self.topic_)
            logger.info(f"MQTT client {self.clientID_} unsubscribed from topic {self.topic_}.")

        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        logger.info(f"Client {self.clientID_} disconnected from the Broker")
