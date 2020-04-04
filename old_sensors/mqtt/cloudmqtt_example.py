# http://www.steves-internet-guide.com/mqtt/
# http://www.steves-internet-guide.com/mosquitto-broker/
# http://www.steves-internet-guide.com/mosquitto_pub-sub-clients/

# using mqtt to publish and subscribe, and mosquitto as a broker (mosquitto -v in bash)
import time
import paho.mqtt.client as mqttClient


broker= "m11.cloudmqtt.com"
port = 14223
user = "oqxvaeik"
password = "ktS1g-6jTGPc"



client = mqttClient.Client("PC-vcm")               #create new instance
client.username_pw_set(user, password=password)    #set username and password


def on_message(client, userdata, message): # https://pypi.org/project/paho-mqtt/#callbacks
    time.sleep(1)  # time.sleep() function to insert delays so as to give the client time to connect etc.
    print("received message = {}".format(str(message.payload.decode("utf-8"))))

# #assign function to callback client1.connect(broker,port)
# #establish connection client1.publish("house/bulb1","on")
######Bind function to callback
client.on_message=on_message  # Called when the broker responds to our connection request.
#####
client.connect(broker, port=port)#connect
client.loop_start()  # start loop to process received messages - client.loop() is important otherwise the callbacks aren’t triggered
# print("subscribing ")
# client.subscribe("apartment/+/+/light")  # subscribing to a topic -- house/# is also an option and house/+ too. # and + are called wild cards, #: for ALL levels house/... and + for one level
time.sleep(2)
print("publishing ")
# client.publish("togliatti/rooms/25/red_led", 1) # publish
client.publish("togliatti/rooms/25/relay", 1) # publish

# client.publish("apartment/rooms/roberto/light","this is the published message on the topic: apartment/rooms/roberto/light")#publish
# client.publish("apartment/heater","this is the published message on the topic: apartment/heater")
time.sleep(5)
client.disconnect() #disconnect
client.loop_stop() #stop loop

## the playing around with mosquitto broker, pub and sub is on the image: publisher_subscriber_mosquitto_example.PNG on this directory. They are good tools for debbuging.
