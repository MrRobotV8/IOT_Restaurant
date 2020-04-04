# v1/devices/me/rpc/request/+

from mqtt.MyMQTT import MyMQTT

inst_mqtt_rpc_thingsboard = MyMQTT(userNickname="UmmUi4zLyPiqy7XGLZw1", userName="UmmUi4zLyPiqy7XGLZw1",
                                broker="157.230.116.49", port=1883, password="")
inst_mqtt_rpc_thingsboard.create_client()
inst_mqtt_rpc_thingsboard.connect()
inst_mqtt_rpc_thingsboard.mySubscribe("v1/devices/me/rpc/request/+")

run = True
while run:
    inst_mqtt_rpc_thingsboard.loop()
