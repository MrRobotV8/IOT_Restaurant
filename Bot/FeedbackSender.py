import json
import requests as req
import logging

# Enable logging for displaying prints
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class Sender:
    def __init__(self):
        with open('../catalog.json', 'r') as f:
            self.config = json.loads(f.read())['thingsboard']
        self.th_host = self.config['host']
        self.th_port = self.config['http_port']
        self.url = f'{self.th_host}:{self.th_port}/api/v1'
        self.username = self.config['username']
        self.password = self.config['password']

        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        payload = {"username": str(self.username), "password": str(self.password)}
        post_url = f'{self.th_host}:{self.th_port}/api/auth/login'
        x = req.post(post_url, data=json.dumps(payload), headers=headers)
        logger.info(f'Login to Thingsboard: POST {x.text}')
        if x.status_code == 200:
            self.jwt_token = json.loads(x.text)["token"]

    def send(self, token, payload, attribute):
        url = f'{self.url}/{token}/{attribute}'
        payload = json.dumps(payload)
        request = req.post(url=url, data=payload)
        logger.info(f'POST {request.text}')

    def get_device_telemetry(self, entity_id, keys=None, interval=None, limit=None, agg=None, entityType="DEVICE"):
        url_api = f"{self.th_host}:{self.th_port}/api/plugins/telemetry/{entityType}/{entity_id}/values/timeseries?"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json",
                   "Accept": "application/json"}
        is_first_parameter = True
        if keys is not None:
            if is_first_parameter:
                is_first_parameter = False
            else:
                url_api += f"&"
            if len(keys) == 1:
                url_api += f"keys={keys[0]}"
            else:
                url_api += f"keys={','.join(keys)}"
        if interval is not None:
            if is_first_parameter:
                is_first_parameter = False
            else:
                url_api += f"&"
            url_api += f"interval={interval}"
        if limit is not None:
            if is_first_parameter:
                is_first_parameter = False
            else:
                url_api += f"&"
            url_api += f"limit={limit}"
        if agg is not None:
            if is_first_parameter:
                is_first_parameter = False
            else:
                url_api += f"&"
            url_api += f"agg={agg}"
        response = req.get(url_api, headers=headers)
        if response.status_code == 200:
            return response
        logger.info(f'GET {response.text}')


if __name__ == '__main__':
    token_order = "a0d722d0-647f-11eb-bcf2-5f53f5d253b9"
    token_telemetry = "a0718330-647f-11eb-bcf2-5f53f5d253b9"

    s = Sender()
    s.send(f'{token_order}_item:table:6', {'reserved': True, 'request': False}, 'attributes')