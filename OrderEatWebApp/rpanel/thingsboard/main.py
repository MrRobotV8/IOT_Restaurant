import requests
import json

class ThingsDash:
    def __init__(self):
        # ThingsBoard REST API URL
        self.url = "http://139.59.148.149"
        self.port = 8080
        self.url_all = f"{self.url}:{self.port}"

        # Default Tenant Administrator credentials
        self.username = "tenant@thingsboard.org"
        self.password = "tenant"

        # login
        self.jwt_token = self.tenant_login()

    def tenant_login(self):
        url_api = f"{self.url_all}/api/auth/login"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        payload = {"username": str(self.username), "password": str(self.password)}
        x = requests.post(url_api, data=json.dumps(payload), headers=headers)
        if x.status_code==200:
            self.jwt_token = json.loads(x.text)["token"]
            return self.jwt_token

    def create_customer(self, address=None, city=None, country=None, email=None, name=None, phone=None, state=None, title=None, zip=None):
        url_api = f"{self.url_all}/api/customer"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json"}
        payload = {}
        if address is not None:
            payload["address"] = address
        if city is not None:
            payload["city"] = city
        if country is not None:
            payload["country"] = country
        if email is not None:
            payload["email"] = email
        if name is not None:
            payload["name"] = name
        if phone is not None:
            payload["phone"] = phone
        if state is not None:
            payload["state"] = state
        if title is not None:
            payload["title"] = title
        if zip is not None:
            payload["zip"] = zip

        x = requests.post(url_api, data=json.dumps(payload), headers=headers)
        if x.status_code==200:
            self.customer_id = json.loads(x.text)["id"]["id"]
            return self.customer_id

    def create_restaurant_asset(self, label=None, name=None):
        url_api = f"{self.url_all}/api/asset"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json"}
        payload = {}

        if label is not None:
            payload["label"] = label
        if name is not None:
            payload["name"] = name
        if type is not None:
            payload["type"] = "restaurant_children"

        x = requests.post(url_api, data=json.dumps(payload), headers=headers)
        if x.status_code==200:
            self.asset_id = json.loads(x.text)["id"]["id"]
            return self.asset_id

    def relation_customer_contains_asset(self, customer_id, asset_id):
        url_api = f"{self.url_all}/api/relation"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json"}

        payload= {
            "from": {
                "id": f"{customer_id}",
                "entityType": "CUSTOMER"
            },
            "type": "Contains",
            "to": {
                "entityType": "ASSET",
                "id": f"{asset_id}"
            },
        }
        x = requests.post(url_api, data=json.dumps(payload), headers=headers)
        if x.status_code==200:
            return True

    def assign_asset_to_customer(self, customer_id, asset_id):
        url_api = f"{self.url_all}/api/customer/{customer_id}/asset/{asset_id}"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json"}

        payload={}
        x = requests.post(url_api, data=json.dumps(payload), headers=headers)
        if x.status_code==200:
            return True

    def provision_restaurant_device(self, restaurant_name):
        url_api = f"{self.url_all}/api/v1/provision"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json"}

        payload = {
            "deviceName": f"{restaurant_name}",
            "provisionDeviceKey": "restaurant_provision_key",
            "provisionDeviceSecret": "provision_device_secret"
        }
        x = requests.post(self, url_api, data=json.dumps(payload), headers=headers)
        if x.status_code==200:
            self.acess_token = json.loads(x.text)["credentialsValue"]
            return self.acess_token

    def save_restaurant_device(self, device_name, custom_access_token):
        url_api = f"{self.url_all}/api/device?accessToken={custom_access_token}"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json", "Accept": "application/json"}

        payload = {
            "name": device_name,
            "type": "restaurant_device_profile",
            "label": "restaurant device"
            }

        x = requests.post(url_api, data=json.dumps(payload), headers=headers)
        if x.status_code==200:
            self.device_id = json.loads(x.text)["id"]["id"]
            return self.device_id

    def relation_asset_contains_device(self, asset_id, device_id):
        url_api = f"{self.url_all}/api/relation"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json"}

        payload= {
            "from": {
                "id": f"{asset_id}",
                "entityType": "ASSET"
            },
            "type": "Contains",
            "to": {
                "entityType": "DEVICE",
                "id": f"{device_id}"
            },
        }
        x = requests.post(url_api, data=json.dumps(payload), headers=headers)
        if x.status_code==200:
            return True

    def assign_device_to_customer(self, customer_id, device_id):
        url_api = f"{self.url_all}/api/customer/{customer_id}/device/{device_id}"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json"}

        payload={}
        x = requests.post(url_api, data=json.dumps(payload), headers=headers)
        if x.status_code==200:
            return True

    def save_table_device(self, table_number, custom_access_token, restaurant_id):
        url_api = f"{self.url_all}/api/device?accessToken={custom_access_token}"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json", "Accept": "application/json"}

        payload = {
            "name": f"{restaurant_id} - Table {table_number}",
            "type": "table_device_profile",
            "label": "table device"
            }

        x = requests.post(url_api, data=json.dumps(payload), headers=headers)
        if x.status_code==200:
            self.device_id = json.loads(x.text)["id"]["id"]
            return self.device_id

    def save_togo_device(self,  custom_access_token, restaurant_id):
        url_api = f"{self.url_all}/api/device?accessToken={custom_access_token}"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json", "Accept": "application/json"}

        payload = {
            "name": f"To Go {restaurant_id}",
            "type": "togo_device_profile",
            "label": "togo device"
            }

        x = requests.post(url_api, data=json.dumps(payload), headers=headers)
        if x.status_code==200:
            self.device_id = json.loads(x.text)["id"]["id"]
            return self.device_id

    def set_device_attributes(self, device_token, payload):
        url_api = f"{self.url_all}/api/v1/{device_token}/attributes"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json", "Accept": "application/json"}

        x = requests.post(url_api, data=json.dumps(payload), headers=headers)
        if x.status_code==200:
            return True

    def save_dashboard(self, payload):
        url_api = f"{self.url_all}/api/dashboard"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json", "Accept": "application/json"}

        x = requests.post(url_api, data=json.dumps(payload), headers=headers)
        if x.status_code==200:
            self.dashboard_id = json.loads(x.text)["id"]["id"]
            return self.dashboard_id

    def assign_dashboard_to_customer(self, customer_id, dashboard_id):
        url_api = f"{self.url_all}/api/customer/{customer_id}/dashboard/{dashboard_id}"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json", "Accept": "application/json"}

        payload={}

        x = requests.post(url_api, data=json.dumps(payload), headers=headers)
        if x.status_code==200:
            return True

    def assign_dashboard_to_public_customer(self, dashboard_id):
        url_api = f"{self.url_all}/api/customer/public/dashboard/{dashboard_id}"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json", "Accept": "application/json"}

        payload={}

        x = requests.post(url_api, data=json.dumps(payload), headers=headers)
        if x.status_code==200:
            self.dashboard_id = json.loads(x.text)["id"]["id"]
            self.public_client_id = json.loads(x.text)["assignedCustomers"][0]["customerId"]["id"]
            self.dashboard_url = f"{self.url_all}/dashboard/{self.dashboard_id}?publicId={self.public_client_id}"
            return self.dashboard_id, self.public_client_id, self.dashboard_url

    def create_togo_order(self, device_access_token, payload):
        url_api = f"{self.url_all}/api/v1/{device_access_token}/telemetry"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json", "Accept": "application/json"}
        x = requests.post(url_api, data=json.dumps(payload), headers=headers)
        if x.status_code==200:
            return True

    def create_table_order(self, device_access_token, payload):
        url_api = f"{self.url_all}/api/v1/{device_access_token}/telemetry"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json", "Accept": "application/json"}
        x = requests.post(url_api, data=json.dumps(payload), headers=headers)
        if x.status_code==200:
            return True

if __name__ == "__main__":

    td = ThingsDash()

    # create customer/owner
    customer_id = td.create_customer(title="Dan", address="Corso Carlo e Nello Rosselli, 82, 10129 Torino TO, Italia")

    # create restaurant asset
    restaurant_name = "A Casa Di Pulcinella"
    asset_id = td.create_restaurant_asset(name=restaurant_name)

    # assign asset to customer
    td.relation_customer_contains_asset(customer_id, asset_id)
    td.assign_asset_to_customer(customer_id, asset_id)

    # create restaurant device
    # access_token = provision_restaurant_device(url_all, jwt_token, "churrascaria boi gordo")
    restaurant_device_id = td.save_restaurant_device(restaurant_name, "custom_access_token")
    # set restaurant attributes
    restaurant_token = f"{asset_id}_1"
    td.set_device_attributes(restaurant_token, {"address": "Corso Carlo e Nello Rosselli, 82, 10129 Torino TO, Italia", "description": "", "name": "", "phone": "", "seats": "", "status":"", "dinner_slot": "", "lunch_slot": ""})
    # assign device to asset
    td.relation_asset_contains_device(asset_id, restaurant_device_id)
    # assign device to customer
    td.assign_device_to_customer(customer_id, restaurant_device_id)

    # create the tables
    dict_tables = {2:1, 4:1, 6:2}  # this should be given by ciccio
    table_number = 0
    for n_seats, n_tables in dict_tables.items():
        for i in range(n_tables):
            table_number += 1
            # create device table
            table_token = f"{restaurant_device_id}_{table_number}"
            table_device_id = td.save_table_device(table_number, table_token)
            # set table attributes
            td.set_device_attributes(table_token, {"seats": n_seats})
            # assign device to asset
            td.relation_asset_contains_device(asset_id, table_device_id)
            # assign device to customer
            td.assign_device_to_customer(customer_id, table_device_id)

    # create the togo device
    togo_token = f"{restaurant_device_id}_togo" #TODO: STORE IN FIREBASE FOR EACH RESTAURANT 
    
    togo_device_id = td.save_togo_device(togo_token)
    # assign device to asset
    td.relation_asset_contains_device(asset_id, togo_device_id)
    # assign device to customer
    td.assign_device_to_customer(customer_id, togo_device_id)

    # creates a dashboard and assigns it to the owner
    f = open("template_restaurant.json")
    dash_json = json.load(f)
    dashboard_id = td.save_dashboard(dash_json)
    td.assign_dashboard_to_customer(customer_id, dashboard_id)

    # make the dashboard public and get its url
    dashboard_id, public_client_id, dashboard_url = td.assign_dashboard_to_public_customer(dashboard_id)
    print(dashboard_url)

    # create order to go
    td.create_togo_order(togo_token, {"client": "Ciccio", "order": "1;2", "adress": "canolo grosso siciliano prego"})
    td.create_togo_order(togo_token, {"client": "Ricca", "order": "7;5", "adress": "sono amico del padrono"})
    td.create_togo_order(togo_token, {"client": "Victor", "order": "8;23", "adress": "lo stesso di Ciccio"})
    td.create_togo_order(togo_token, {"client": "Dan", "order": "23;7;19", "adress": "sono il padrono"})

    # create an order in table 1
    td.create_table_order(f"{restaurant_device_id}_1", {"client": "Pietro", "order": "3"})

    




    print("end")