import time
import json


def open_json(file):
	with open(file) as f:
		obj = json.loads(f.read())
	return obj

def write_json(file, obj):
	with open(file, 'w') as f:
		f.write(json.dumps(obj, indent=4))


def update_customers(user, people, time, obj):
	tmp_obj = {
		'time':time,
		'people':people
	}
	obj[user] = tmp_obj
	write_json('Customers.json', obj)