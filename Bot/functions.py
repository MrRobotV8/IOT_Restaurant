import time
import json


def open_json(file):
	with open(file) as f:
		obj = json.loads(f.read())
	return obj

def write_json(file, obj):
	with open(file, 'w') as f:
		f.write(json.dumps(obj, indent=4))

def update_customers(user, people, time, key_restaurant, customer_obj, restaurant_obj):
	tmp_obj = {
		'time':time,
		'people':people
	}

	cust_obj = {
		'active_booking':{
			'key':key_restaurant,
			'time':time,
			'people':people
		}
	}
	customer_obj[user] = cust_obj
	restaurant_obj[key_restaurant]['customers'][user] = tmp_obj
	
	write_json('Customers.json', customer_obj)
	write_json('restaurant.json', restaurant_obj)

def keys_restaurants(restaurant_obj):
	keys_names = [(k,v['name']) for k,v in restaurant_obj.items()]
	return keys_names