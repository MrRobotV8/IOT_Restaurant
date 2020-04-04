# http://www.steves-internet-guide.com/mqtt/
# http://www.steves-internet-guide.com/mosquitto-broker/
# http://www.steves-internet-guide.com/mosquitto_pub-sub-clients/
import json
# using mqtt to publish and subscribe, and mosquitto as a broker (mosquitto -v in bash)
import time
import paho.mqtt.client as paho
# broker="broker.hivemq.com"
# broker="iot.eclipse.org"
broker = "m24.cloudmqtt.com"

# broker = '192.168.1.1' #do not require to put the port. e.g. :8080 or :1883
#define callback
def on_message(client, userdata, message): # https://pypi.org/project/paho-mqtt/#callbacks
    time.sleep(1)  # time.sleep() function to insert delays so as to give the client time to connect etc.
    print("received message = {}".format(str(message.payload.decode("utf-8"))))

client= paho.Client("kkkkk")  # create client object
# #assign function to callback client1.connect(broker,port)
# #establish connection client1.publish("house/bulb1","on")
######Bind function to callback
client.on_message=on_message  # Called when the broker responds to our connection request.
#####
print("connecting to broker ", broker)
client.connect(broker, port=14223)#connect
client.username_pw_set(username="oqxvaeik", password="ktS1g-6jTGPc")

client.loop_start()  # start loop to process received messages - client.loop() is important otherwise the callbacks aren’t triggered
# print("subscribing ")
client.subscribe("viapalmirotogliatti/#")  # subscribing to a topic -- house/# is also an option and house/+ too. # and + are called wild cards, #: for ALL levels house/... and + for one level
time.sleep(2)
print("publishing ")
# client.publish("togliatti/rooms/25/red_led", 1) # publish
#client.publish("togliatti/bedroom/21/relay", payload=0, qos=2) # publish
pload = {'value': 12}
pload2="{\"value\": 12}"
# client.publish(topic="tb/mqtt-integration-tutorial/sensors/SN-001/temperature", payload=json.dumps({'value': 44}), qos=2)  # publish
client.publish(topic="viapalmirotogliatti/bedroom/21/dht11", payload=json.dumps({'temperature': 22, 'humidity': 59}), qos=2)  # publish


client.loop_start()

# client.publish("apartment/rooms/roberto/light","this is the published message on the topic: apartment/rooms/roberto/light")#publish
# client.publish("apartment/heater","this is the published message on the topic: apartment/heater")
time.sleep(4)
client.disconnect() #disconnect
client.loop_stop() #stop loop

## the playing around with mosquitto broker, pub and sub is on the image: publisher_subscriber_mosquitto_example.PNG on this directory. They are good tools for debbuging.
