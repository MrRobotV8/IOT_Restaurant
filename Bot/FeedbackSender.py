import json
import requests as req


class Sender:
    def __init__(self, host='139.59.148.149'):
        self.host = host

    def send(self, token, payload):
        self.url = f'http://{self.host}:8080/api/v1/{token}/telemetry'
        payload = json.dumps(payload)
        request = req.post(url=self.url, data=payload)
        print(request.status_code)
        print(request.text)
