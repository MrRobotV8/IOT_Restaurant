from thingspeak.ThingSpeakRequests import ThingSpeakRequests
from mqtt.MyMQTT import MyMQTT
import time


## initializing mqtt connetion with Thingsboard
# https://thingsboard.io/docs/getting-started-guides/helloworld/
# Set ThingsBoard host to "demo.thingsboard.io" or "localhost"
broker = "demo.thingsboard.io"
port = 1883
# Replace YOUR_ACCESS_TOKEN with one from Device details panel.
# clientID = "YOUR_ACCESS_TOKEN"
clientID = "AM9bdv6zUIRfWYOV6trV"  # access token for via_palmiro_togliatti_devices

# Publish serial number and firmware version attributes
# mosquitto_pub -d -h "$THINGSBOARD_HOST" -t "v1/devices/me/attributes" -u "$ACCESS_TOKEN" -f "attributes-data.json"
inst_mqtt_thingsboard = MyMQTT(clientID=clientID, broker=broker, port=port)
inst_mqtt_thingsboard.create_client()
inst_mqtt_thingsboard.connect()
# MQTT_TOPIC = [("Server1/kpi1",0),("Server2/kpi2",0),("Server3/kpi3",0)]
inst_mqtt_thingsboard.mySubscribe("viapalmirotogliatti", qos=2)

run = True
while run:
    # inst_mqtt_thingspeak.loop()
    inst_mqtt_thingsboard.loop()
    time.sleep(0.5)