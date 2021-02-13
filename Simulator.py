import json 
import time
import random
import threading
import paho.mqtt.client as mqtt
from pyrebase import pyrebase
from datetime import datetime

class Simulator:
	def __init__(self):
		self.cnt = 0 #counter for restaurants
		#incremental factors for sensors
		self.alpha = 0.15 
		self.beta = 0.10
		self.delta = 0.05

		#reference min/max temperature in Turin
		self.TEMP ={
			"Jan":[-3,6], "Feb":[-1,8], "Mar":[2,13], "Apr":[6,17], 
			"May":[10,21], "Jun":[14,25], "Jul":[16,28], "Aug":[16,27],
			"Sep":[13,23], "Oct":[7,17], "Nov":[2,11], "Dec":[-2,7]}

		#reference humidity in Turin
		self.HUM = {
			"Jan":75, "Feb":75, "Mar":67, "Apr":72,
			"May":75, "Jun":74, "Jul":72, "Aug":73, 
			"Sep":75, "Oct":79, "Nov":80, "Dec":80 }

		self.firebase_data() #initialize self.hours and self.token_lst
		self.occupied = False 
		self.start_time = datetime.now()

	def simulate_room_data(self, prev_temp, prev_hum, prev_bath, prev_noise):
		month = datetime.strftime(self.now,"%b")
		month_num = datetime.strftime(self.now,"%m")

		min_temp, max_temp = self.TEMP[month]
		humidity = self.HUM[month]
		rest_open = self.is_rest_open() #bool: check if restaurant is open

		if rest_open: #open restaurant
			ref_noise = random.uniform(30,60)
			if 3 <= int(month_num) <= 8: 	#summer
				ref_temp = random.uniform(23,26)
			else: 							#winter
				ref_temp = random.uniform(17,20)
			ref_hum = random.uniform(50,humidity)

			if random.uniform(0,1) > self.delta: bathroom = prev_bath
			else: bathroom = not prev_bath 
			#changes bathroom status with probability = self.delta

		else: #closed restaurant
			ref_noise = random.uniform(10,30)
			if 3 <= int(month_num) <= 8: ref_temp = random.uniform(23,max_temp)
			else: ref_temp = random.uniform(min_temp,20)
			ref_hum = random.uniform(.8*humidity, 1.2*humidity)
			bathroom = 0

		temp = (1-self.alpha)*prev_temp + self.alpha*ref_temp
		humidity = (1-self.beta)*prev_hum + self.beta*ref_hum

		if humidity > 100: humidity=100

		noise = (1-self.alpha)*prev_noise + self.alpha*ref_noise

		return round(temp,2), round(humidity,2), int(bathroom), int(noise)

	def is_rest_open(self):
		status = False
		for e in self.hours:
			hour = self.now
			op_H, cl_H = e.split('-')
			op_hour = hour.replace(hour=int(op_H), minute=0)

			if int(cl_H) != 0: cl_hour = hour.replace(hour=int(cl_H), minute=0)
			else: cl_hour = hour.replace(hour=23, minute=59)

			if op_hour<hour<cl_hour: status=True

		status = True
		return status

	def run(self, client, rest_name):
		interval = 5 #interval time between sending data
		t,h,b,b_prev,n = 20,50,0,0,35

		client.loop_start()
		while True:
			self.now = datetime.now()
			
			t,h,b,n = self.simulate_room_data(t,h,b,n)
			sensor_data = {
				'temperature': t,
				'humidity': h,
				'noise':n}
			client.publish('v1/devices/me/telemetry', json.dumps(sensor_data), 1)

			if b != b_prev: 
				client.publish('v1/devices/me/attributes', json.dumps({'bathroom_busy': b}))
			b_prev = b

			print(rest_name)
			print('Temp.:{} [°C]; Hum.: {} [%]; Noise: {}; Toilet occupied: {}\n'.format(t,h,n,bool(b)))

			time.sleep(interval)

			if stop_threads: break

		client.loop_stop()
		client.disconnect()


	def firebase_data(self):
		with open('catalog.json') as f:
			config_file = json.load(f)
		config = config_file['firebase']

		self.firebase = pyrebase.initialize_app(config)
		self.auth = self.firebase.auth()
		self.db = self.firebase.database()

		self.full_rest_names = []
		full_rest_list = list(self.db.child('restaurants').shallow().get().val())
		self.n_restaurants = len(full_rest_list)
		print(full_rest_list)
		print(self.n_restaurants)

		for x in full_rest_list:
			path = 'restaurants/'+str(x)+'/details/name'
			self.full_rest_names.append(self.db.child(path).get().val())

		self.token_lst = []

		for rest_hash in full_rest_list[:self.n_restaurants]:
			path_l = 'restaurants/'+str(rest_hash)+'/details/lunch-slot'
			path_d = 'restaurants/'+str(rest_hash)+'/details/dinner-slot'
			path_tok = 'restaurants/'+str(rest_hash)+'/details/token_telemetry'
			
			self.hours = self.db.child(path_l).get().val()
			tmp = self.db.child(path_d).get().val()

			if self.hours != None: [self.hours.append(x) for x in tmp]
			else: self.hours = tmp

			token = self.db.child(path_tok).get().val()+'_business:1'
			self.token_lst.append(token)

	def thingsboard(self):
		random.seed(self.cnt)

		ACCESS_TOKEN = self.token_lst[self.cnt]
		rest_name = self.full_rest_names[self.cnt]
		THINGSBOARD_HOST = '139.59.148.149'
		print(self.cnt,':',ACCESS_TOKEN)

		client = mqtt.Client()
		client.username_pw_set(ACCESS_TOKEN)
		client.connect(THINGSBOARD_HOST, 1883, 60)
		self.run(client, rest_name)

if __name__ == '__main__':
	stop_threads = False
	simulation_duration = 60*2 #seconds

	SIM = Simulator()

	threads = []
	for i in range(SIM.n_restaurants):
		threads.append(threading.Thread(target=SIM.thingsboard))

	for t in threads:
		t.start()
		print(t.getName())
		time.sleep(0.1)
		SIM.cnt += 1
		time.sleep(0.1)

	time.sleep(simulation_duration)
	stop_threads = True
