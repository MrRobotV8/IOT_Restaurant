import requests
import json
DEFAULT = object()  # can use also None
import time

class ThingsBoardRequests:
    #Thingsboard HTTP API

    def __init__(self, devices):
        # for http
        self.devices = devices
        self.headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    def send_http_telemetry(self, device, payload):
        print("payload:", payload)
        if "dht" in device:
            dht_str = ["temperature", "humidity"]
            for i in range(2):
                r = requests.post("http://demo.thingsboard.io/api/v1/{}/telemetry".format(self.devices[device]),
                                  data=json.dumps({dht_str[i]: payload[i]}),
                                  headers={'Content-type': 'application/json'})
                print(dht_str[i], r.status_code, r.reason)
