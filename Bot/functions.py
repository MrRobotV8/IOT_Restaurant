import time
import json


def open_json(file):
    with open(file) as f:
        obj = json.loads(f.read())
    return obj


def write_json(file, obj):
    with open(file, 'w') as f:
        f.write(json.dumps(obj, indent=4))


def keys_restaurants(restaurant_obj):
    keys_names = [(k, v['name']) for k, v in restaurant_obj.items()]
    return keys_names
