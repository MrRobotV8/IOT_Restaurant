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

