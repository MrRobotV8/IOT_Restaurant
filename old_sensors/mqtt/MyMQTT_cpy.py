import paho.mqtt.client as PahoMQTT
import datetime
import time
import sys
from thingspeak.ThingSpeakRequests import ThingSpeakRequests
import json
import requests
import math
import paho.mqtt.publish as publish

DEFAULT = object()  # can use also None
"""
# inst_mqtt = MyMQTT(clientID="rpi_subscriber", broker=broker, port=port,
#                               thingspeak=inst_thingspeak)
# inst_mqtt.create_client()
# time.sleep(0.5)
# inst_mqtt.connect()
# inst_mqtt.mySubscribe("viapalmirotogliatti", qos=2)
#
#
# run = True
# while run:
#     inst_mqtt.loop()
#     time.sleep(0.5)
#
#
#
"""
class MyMQTT:
	def __init__(self, userName, userNickname, broker, port, devices=DEFAULT, clean_session=False, password="", keep_alive=120,
					thingspeak=DEFAULT, thingsboard=DEFAULT, cloudbroker=DEFAULT, thingsboard_mqtt_broker_address = DEFAULT,
				 localbroker=DEFAULT, linktype="upload"):

		self.userNickname = userNickname # this is the client id, not the autentication
		self.userName = userName
		self.port = port
		self.broker = broker
		self.devices = devices
		self.password = password
		self.clean_session = clean_session
		self.keep_alive = keep_alive
		self.thingsboard = thingsboard
		self.thingsboard_mqtt_broker_address = thingsboard_mqtt_broker_address
		self.thingspeak = thingspeak
		self.cloudbroker = cloudbroker
		self.linktype=linktype
		self.localbroker=localbroker

		self.mqtt_bad_connection = False
		self.mqtt_connected = False
		self.dict_mqtt_return_codes={0: "Connection successful", 1: "Connection refused – incorrect protocol version",
								2: "Connection refused – invalid client identifier", 3: "Connection refused – server unavailable",
								4: "Connection refused – bad username or password", 5: "Connection refused – not authorised",
								"other": "Currently unused"}
		self.isSubscriber = False

		self.value = {"temperature": [], "humidity": []}
		self.time = {"temperature": [], "humidity": []}

	def create_client(self):
		# create an instance of paho.mqtt.client
		# Client(client_id="", clean_session=True, userdata=None, protocol=MQTTv311, transport="tcp"): https://www.eclipse.org/paho/clients/python/docs/
		self._client = PahoMQTT.Client(client_id=self.userNickname, clean_session=self.clean_session)
		# clean session: https://www.hivemq.com/blog/mqtt-essentials-part-3-client-broker-connection-establishment/
		# The clean session flag tells the broker whether the client wants to establish a persistent session or not.
		# In a persistent session (CleanSession = false), the broker stores all subscriptions for the client and all
		# missed messages for the client that subscribed with a Quality of Service (QoS) level 1 or 2. If the session
		# is not persistent (CleanSession = true), the broker does not store anything for the client and purges all
		# information from any previous persistent session.

		# needs to be set before connecting
		self._client.username_pw_set(username=self.userName, password=self.password)
		# register callbacks
		self._client.on_connect = self.on_connect
		self._client.on_disconnect = self.on_disconnect
		self._client.on_message = self.on_message

		# message_callback_add:
		# If using message_callback_add() and on_message, only messages that do not match a subscription specific filter
		# will be passed to the on_message callback.
		# wildcards allowed
		self._client.message_callback_add("viapalmirotogliatti/#", self.on_message_togliatti)

	def connect(self):
		# manage connection to broker
		# keepalive:
		# maximum period in seconds allowed between communications with the broker.
		# If no other messages are being exchanged, this controls the rate at
		# which the client will send ping messages to the broker.
		# The keepAlive value is designed, so the broker can recognise broken connections.
		#https://www.eclipse.org/paho/clients/python/docs/
		#https://www.hivemq.com/blog/mqtt-essentials-part-3-client-broker-connection-establishment/
		try:
			self._client.connect(host=self.broker, port=self.port, keepalive=self.keep_alive, bind_address="")
		except:
			print("connection failed")

		while not self.mqtt_connected and not self.mqtt_bad_connection:  # wait in loop
			print("waiting for the mqtt connection")
			self._client.loop()
			time.sleep(1)

		if self.mqtt_bad_connection:
			self._client.loop_stop()  # client stop loop
			sys.exit()

	def on_disconnect(self, client, userdata, rc):
		if rc != 0:
			print("MQTT unexpected disconnection.")
		else:
			print("MQTT clean disconnection.")
		self.mqtt_connected = False

	def on_connect(self, paho_mqtt, userdata, flags, rc):
		# The callback for when the client receives a CONNACK message response from the server/broker.
		try:
			print("Connection to broker %s with result code: %d, meaning: %s" % (self.broker, rc, self.dict_mqtt_return_codes[rc]))
		except:
			print("Connection to broker %s with result code: %d, meaning: %s" % (self.broker, rc, self.dict_mqtt_return_codes["other"]))

		if rc == 0:
			self.mqtt_connected = True
		else:
			self.mqtt_bad_connection = True

	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	#client.subscribe("$SYS/#")
	def on_message_togliatti(self, paho_mqtt , userdata, msg):

		switcher_months_january = {
			0: "January",
			1: "February",
			2: "March",
			3: "April",
			4: "May",
			5: "June",
			6: "July",
			7: "August",
			8: "September",
			9: "October",
			10: "November",
			11: "December"
		}

		switcher_weekdays_saturday = {
			0: "Saturday",
			1: "Sunday",
			2: "Monday",
			3: "Tuesday",
			4: "Wednesday",
			5: "Thursday",
			6: "Friday"
		}

		y_dict = {
					"apartment": "",
					"room": "",
					"room_id": "",
					"devices": {
						"dht11": {
							"temperature": "",
							"humidity": "",
							"last_update":"",
						},
						"eq3": {
							"values": [],
						},
						"mq2": {
							"values": [],
						}
					}
				}

		message_decode = str(msg.payload.decode("utf-8", "ignore"))

		try:
			message_in = json.loads(message_decode)  # decode json data
		except:
			message_in = message_decode  # decode json data

		if self.linktype == "upload":
			received_topic = str(msg.topic)
			received_topic = received_topic.split("/")
			print("topic received: ", received_topic)
			print("message received: " + str(message_in))

			y_dict["apartment"] = received_topic[0]
			y_dict["room"] = received_topic[1]
			y_dict["room_id"] = received_topic[2]
			device = received_topic[3]

			if 'dht' in device:
				y_dict["devices"][device]["temperature"] = message_in[device][0]
				y_dict["devices"][device]["humidity"] = message_in[device][1]
				y_dict["devices"][device]["last_update"] = str(datetime.datetime.now())

			elif 'eq3status' in device:
				reply = {}
				reply["last_update"] = str(datetime.datetime.now())
				self.reply = {}
				message = message_in["eq3_status"]
				if message[0] == 0x02 and message[1] == 0x01: # status notification(auto/manual mode):
											# 6 bytes, received after read or write profile command
					# lock status
					lock_nibble = '{:02x}'.format(message[2])[0] # get the first nibble of the byte
					if lock_nibble == '0':
						reply["lock_str"] = "keypad unlocked"
						reply["lock"] = False
					elif lock_nibble == '1':
						reply["lock_str"] = "locked due to open window detection"
						reply["lock"] = True
					elif lock_nibble == '2':
						reply["lock_str"] = "locked due to manual lock enabled"
						reply["lock"] = True
					elif lock_nibble == '3':
						reply["lock_str"] = "locked due to open window detection && manual lock enabled"
						reply["lock"] = True

					# mode status
					active_mode_nibble = '{:02x}'.format(message[2])[1]  # get the second nibble of the byte
					if active_mode_nibble == '8':
						reply["mode"] = "auto mode"
						reply["automatic"] = True
						reply["holiday"] = False
						reply["boost"] = False
					elif active_mode_nibble == '9':
						reply["mode"] = "manual mode"
						reply["automatic"] = False
						reply["holiday"] = False
						reply["boost"] = False
					elif active_mode_nibble == 'a':
						reply["mode"] = "holiday mode"
						reply["automatic"] = False
						reply["holiday"] = True
						reply["boost"] = False
					elif active_mode_nibble == 'c':
						reply["mode"] = "boost mode. at the end it returns to automatic mode"
						reply["automatic"] = True
						reply["holiday"] = False
						reply["boost"] = True
					elif active_mode_nibble == 'd':
						reply["mode"] = "boost mode. at the end it returns to manual mode"
						reply["automatic"] = False
						reply["holiday"] = False
						reply["boost"] = True
					elif active_mode_nibble == 'e':
						reply["mode"] = "boost mode. at the end it returns to holiday mode"
						reply["automatic"] = False
						reply["holiday"] = True
						reply["boost"] = True
					if message[3] != 'XX':
						reply["oppening"] = int(message[3]/0x64) * 100
					if message[4] != 'XX':
						reply["battery"] = message[4]
					if message[5] != 'XX':
						reply["target temperature"] = int(message[5])/2
					try:
						if message[6] != 'XX':
							# minutes can only be programmed in half-hour intervals (i.e. XX:00 or XX:30),
							# so the value of end_minutes/30 will always be equivalent to 0 or 1.
							reply["end_holiday_day"] = int(message[6])

						if message[7] != 'XX':
							reply["end_holiday_year"] = int(message[7]) + 2000

						if message[8] != 'XX':
							if (int(message[8]) % 2) == 0:
								# even number
								reply["end_hour"] = int(message[8])/2
								reply["end_minutes"] = 0*30
							else:
								# odd number
								reply["end_hour"] = (int(message[8]) - 1)/2
								reply["end_minutes"] = 1*30

						if message[9] != 'XX':
							reply["end_holiday_month"] = int(message[9])
					except:
						pass
					if message[0] == 0x02 and message[1] == 0x02:  # Profile Notif. (modify)
						if message[2] != 'XX':
							reply["modified_day"] = switcher_weekdays_saturday.get(int(message[2]), "Invalid weekday")

					if message[0] == 0x21:  # Profile Notif. (modify)
						if message[1] != 'XX':
							reply["day_of_the_week"] = switcher_weekdays_saturday.get(int(message[1]), "Invalid weekday")
					self.reply = reply
					# headers = {'Content-type': 'application/json'}
					# r = requests.post("157.230.116.49/api/v1/{}/attributes".format(self.devices[device.replace("status", "_"+y_dict["room_id"])]),
					# 				  data=json.dumps(reply), headers=headers)
					# print(r.status_code, r.reason)
					# print(reply)


			if self.thingspeak != DEFAULT:
				try:
					print("thingspeak:")
					self.thingspeak.write_data_json([1, 2], y_dict["devices"][received_topic[3]]["values"])
					print("thingspeak send finished")
				except:
					print("thingspeak caught in except")
					pass

			if self.thingsboard !=DEFAULT:
				try:
					print("thingsboard:")
					self.thingsboard.send_http_telemetry(device=received_topic[3]+"_"+received_topic[2], payload=message_in[received_topic[3]])
					print("thingsboard send finished")
				except:
					print("thingsboard caught in except")
					pass

			if self.cloudbroker !=DEFAULT:
				try:
					print("cloudbroker:")
					self.cloudbroker.myPublish(topic=str(msg.topic), msg=json.dumps(y_dict["devices"][received_topic[3]]))
					print("cloudbroker send finished")
				except:
					print("cloudbroker caught in except")
					pass

			if self.localbroker !=DEFAULT:
				try:
					print("localbroker:")
					self.localbroker.myPublish(topic=str(msg.topic), msg=message_in)
					print("localbroker send finished")
				except:
					print("localbroker caught in except")
					pass

			if self.thingsboard_mqtt_broker_address !=DEFAULT:
				try:
					print("publish.single thingsboard_mqtt")
					if ('eq3status' not in device):
						publish.single("v1/devices/me/telemetry", payload=json.dumps(y_dict["devices"][received_topic[3]]),
									   qos=0, retain=False, hostname=self.thingsboard_mqtt_broker_address,
									   port=1883,
									   auth={'username':self.devices[device+ "_" + y_dict["room_id"]],'password':""})
					else:
						publish.single("v1/devices/me/attributes", payload=json.dumps(self.reply),
									   qos=0, retain=False, hostname=self.thingsboard_mqtt_broker_address,
									   port=1883,
									   auth={
										   'username': self.devices[device.replace("status", "_" + y_dict["room_id"])],
										   'password': ""})
					print("thingsboard_mqtt send finished")
				except:
					print("thingsboard_mqtt caught in except")
					pass
				#client.disconnect()

		elif self.linktype == "download":
			received_topic = str(msg.topic)
			received_topic = received_topic.split("/")
			print("topic received: ", received_topic)

			if msg.topic == "viapalmirotogliatti/bedroom/21/eq3/rpc_command":
				if message_in == 'set_current_date_and_time':
					# byte 0: 03
					# byte 1: year % 100
					# byte 2: month
					# byte 3: day
					# byte 4: hour
					# byte 5: minutes
					# byte 6: seconds
					now = datetime.datetime.now()
					payload = json.dumps({"value": [0x03, (int(now.year % 100)), (now.month), (now.day),
													(now.hour), (now.minute), (now.second)]})
				elif message_in == 'select_temperature':
					# Activates the selected temperature
					# byte 0: 41
					# byte 1: temperature * 2
					temperature = 0
					temperature = 21 if int(temperature)>28 else int(temperature)
					payload = json.dumps({"value": [0x41, temperature*2]})

				elif message_in == 'select_comfort_temperature':
					# Activates the comfort temperature
					payload = json.dumps({"value": [0x43]})

				elif message_in == 'select_reduced_temperature':
					# Activates the reduced temperature
					payload = json.dumps({"value": [0x44]})

				elif message_in == 'set_comfort_and_reduced_temperature':
					new_comfort_temperature = 0
					new_reduced_temperature = 0
					new_comfort_temperature = int(new_comfort_temperature)
					new_reduced_temperature = int(new_reduced_temperature)
					payload = json.dumps({"value": [0x11, hex(new_comfort_temperature*2),
													hex(new_reduced_temperature*2)]})

				elif message_in == 'start_boost_mode':
					payload = json.dumps({"value": [0x45, 0x01]})

				elif message_in == 'stop_boost_mode':
					payload = json.dumps({"value": [0x45, 0x00]})

				elif message_in == 'select_auto_mode':
					payload = json.dumps({"value": [0x40, 0x00]})

				elif message_in == 'select_manual_mode':
					payload = json.dumps({"value": [0x40, 0x40]})

				elif message_in == 'select_holiday_mode':
					# Activates the holiday mode on the valve.
					# To be activated, it requires: the temperature
					# to be kept and the end date and time.
					# byte 0: 40
					# byte 1: (temperature * 2) + 128
					# byte 2: day
					# byte 3: year % 100
					# byte 4: (hour*2) + (minutes/30)
					# byte 5: month

					# months and days are calculated starting from 1. As a result, both the month of January and
					# the first day of each month will be identified by the value 0x01

					# minutes can only be programmed in half-hour intervals (i.e. XX:00 or XX:30),
					# so the value of minutes/30 will always be equivalent to 0 or 1.
					temperature = 0
					month = 0
					day = 0
					year = 0
					hour = 0
					minutes = 0

					isValidDate = True
					try:
						datetime.datetime(int(year), int(month), int(day))
					except ValueError:
						isValidDate = False

					temperature = int(temperature*2) + 128

					month = int(month)

					day = int(day)

					year = int(year)

					hour = 12 if int(hour) > 23 else int(hour)

					minutes = 1 if int(minutes/30) != 0 else 0
					if isValidDate:
						payload = json.dumps({"value": [0x40, hex(temperature), hex(day), hex(year % 100),
													hex((hour*2)+minutes), hex(month)]})
				elif message_in == 'enable_command_block':
					# It allows to lock the physical buttons on the valve.
					# Note that it allows however to manage the valve
					# through the application.
					payload = json.dumps({"value": [0x80, 0x01]})

				elif message_in == 'disable_command_block':
					payload = json.dumps({"value": [0x80, 0x00]})

				elif message_in == 'set_temperature_offset':
					# Allows to set a temperature offset in a range between -3.5°C and +3.5°C.

					# As the temperature is measured on the radiator, the temperature distribution can vary
					# throughout a room. To adjust this, a temperature offset of up to ±3.5 °C can be set.
					# If a nominal temperature of e.g. 20 °C is set but the room presents with only 18 °C,
					# an offset of -2.0 °C needs to be set.

					temperature = 0
					temperature = 0 if abs(temperature) > 3.5 else int(temperature)
					payload = json.dumps({"value": [0x13, hex(temperature*2 + 7)]})

				elif message_in == 'change_window_mode_settings':
					# With a rapidly reducing temperature, the radiator thermostat automatically detects
					# that a room is being ventilated. In order to save heating costs, the temperature is
					# then reduced for a certain period of time (15 minutes, set at the factory). Whilst this
					# function is active, the “window open” symbol appears on the display.
					#
					# Allows to set the duration and the temperature to keep when the window mode takes over. The
					# window mode is activated automatically when the valve detects a significant temperature drop

					# minutes can only assume values that are multiples of 5,
					# so the final content of byte 2 will be between 0x00 and 0x0C

					# byte 0: 14
					# byte 1: (temperature * 2)
					# byte 2: (minutes / 5)

					temperature = 0
					temperature = int(temperature)
					minutes = 0
					minutes = 60 if int(minutes) > 60 else int(minutes)

					payload = json.dumps({"value": [0x14, hex(temperature*2), hex(int(minutes/5))]})
				elif message_in == 'daily_profile_request':
					# It requires data relating to the schedule of a given day.
					# The information is received as a notification.

					# the days of the week are counted starting from Saturday
					# (00 is Saturday, ..., 06 is Friday)
					day_of_the_week = 0
					day_of_the_week = int(day_of_the_week)

					payload = json.dumps({"value": [0x10, hex(day_of_the_week)]})

				elif message_in == 'set_daily_profile':
					# Set the schedule for a given day of the week. It is necessary to choose a base temperature and it is
					# possible to modify it for at most three time intervals. If a profile is already present for the chosen
					# day, it will be replaced.
					# The command consists of at most 16 byte.
					pass
					# dummy_dict = {"value": [0x10, 0x01, 0x33, 0x44]}
					# set_daily_profile_dict = {"value": [0x10]}
					# day_of_the_week = int(dummy_dict["value"][1])
					# set_daily_profile_dict["value"].append(day_of_the_week)

			if self.localbroker !=DEFAULT:
				try:
					print("localbroker:")
					self.localbroker.myPublish(topic=str(msg.topic).replace("rpc_command","rx"), msg=payload)
					print("localbroker send finished")
					time.sleep(1)
					now = datetime.datetime.now()
					payload = json.dumps({"value": [0x03, (int(now.year % 100)), (now.month), (now.day),
													(now.hour), (now.minute), (now.second)]})
					self.localbroker.myPublish(topic=str(msg.topic).replace("rpc_command","rx"), msg=payload)

				except:
					print("localbroker caught in except")
					pass


	def on_message(self, paho_mqtt , userdata, msg):
		# The callback for when a PUBLISH message is received from the server.
		# A new message is received
		#self.notifier.notify(msg.topic, msg.payload)
		print("message received")
		print("topic: ", msg.topic)
		message_decode = str(msg.payload.decode("utf-8", "ignore"))
		try:
			message_in = json.loads(message_decode)  # decode json data
		except:
			message_in = message_decode  # decode json data
		pass
		print("message in: ", message_in)

	def myPublish(self, topic, msg, qos=0):
		# if needed, you can do some computation or error-check before publishing
		print ("publishing '%s' with topic '%s'" % (msg, topic))
		# publish a message with a certain topic
		self._client.publish(topic=topic, payload=msg, retain=False, qos=qos)

	def mySubscribe(self, topic, qos=0):
		# if needed, you can do some computation or error-check before subscribing
		print ("subscribing to topic: " + topic + ", with qos=" + str(qos))
		# subscribe for a topic
		self._client.subscribe(topic=topic, qos=qos)

		# just to remember that it works also as a subscriber
		self._isSubscriber = True
		self._topic = topic
	def loop(self):
		# https://pypi.org/project/paho-mqtt/#network-loop
		# loop(timeout=1.0, max_packets=1)
		# The max_packets argument is obsolete and should be left unset.
		self._client.loop_start()

	def forever_loop(self):
		# https://pypi.org/project/paho-mqtt/#network-loop
		# loop_forever(timeout=1.0, max_packets=1, retry_first_connection=False)
		# This is a blocking form of the network loop and will not return until the client calls disconnect(). It automatically handles reconnecting.
		self._client.loop_forever()

	def stop(self):
		if self.isSubscriber:
			# remember to unsubscribe if it is working also as subscriber
			self._client.unsubscribe(self._topic)
		self._client.loop_stop()
		self._client.disconnect()


def invmodp(a, p):
	'''
    The multiplicitive inverse of a in the integers modulo p.
    Return b s.t.
    a * b == 1 mod p
    '''

	for d in range(1, p):
		r = (d * a) % p
		if r == 1:
			break
	else:
		raise ValueError('%d has no inverse mod %d' % (a, p))
	return d

