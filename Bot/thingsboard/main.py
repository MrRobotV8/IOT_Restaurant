import requests
import json
import os

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

    def create_restaurant_asset(self, asset_label=None, asset_name=None):
        url_api = f"{self.url_all}/api/asset"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json"}
        payload = {}

        if asset_label is not None:
            payload["label"] = asset_label
        if asset_name is not None:
            payload["name"] = asset_name
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

    # def assign_device_to_public(self, asset_id):
    #     url_api = f"{self.url_all}/api/customer/public/asset/{asset_id}"
    #     headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json"}
    #     payload={}
    #     x = requests.post(url_api, data=json.dumps(payload), headers=headers)
    #     if x.status_code==200:
    #         return True

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

    def save_restaurant_device(self, device_name, device_label, device_token):
        url_api = f"{self.url_all}/api/device?accessToken={device_token}"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json", "Accept": "application/json"}

        payload = {
            "name": device_name,
            "type": "restaurant_device_profile",
            "label": device_label
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

    def relation_device_contains_device(self, device_id_parent, device_id_child):
        url_api = f"{self.url_all}/api/relation"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json"}

        payload= {
            "from": {
                "id": f"{device_id_parent}",
                "entityType": "DEVICE"
            },
            "type": "Contains",
            "to": {
                "entityType": "DEVICE",
                "id": f"{device_id_child}"
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

    def assign_device_to_public(self, device_id):
        url_api = f"{self.url_all}/api/customer/public/device/{device_id}"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json"}
        payload={}
        x = requests.post(url_api, data=json.dumps(payload), headers=headers)
        if x.status_code==200:
            return True

    def save_table_device(self, table_number, device_token, device_restaurant_id):
        url_api = f"{self.url_all}/api/device?accessToken={device_token}"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json", "Accept": "application/json"}

        payload = {
            "name": f"{device_restaurant_id} - Table {table_number}",
            "type": "table_device_profile",
            "label": f"Table {table_number}"
            }

        x = requests.post(url_api, data=json.dumps(payload), headers=headers)
        if x.status_code==200:
            self.device_id = json.loads(x.text)["id"]["id"]
            return self.device_id

    def save_togo_device(self,  device_token, restaurant_device_id):
        url_api = f"{self.url_all}/api/device?accessToken={device_token}"
        headers = {"X-Authorization": "Bearer " + self.jwt_token, "Content-Type": "application/json", "Accept": "application/json"}

        payload = {
            "name": f"{restaurant_device_id} - To Go",
            "type": "togo_device_profile",
            "label": "To Go"
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
            decoded_json = json.loads(x.text)
            self.dashboard_id = decoded_json["id"]["id"]
            self.public_client_id = decoded_json["assignedCustomers"][-1]["customerId"]["id"]
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

    def customize_dashboard(self, restaurant_dashboard_path, restaurant_label, customer_id):
        print(os.listdir())
        with open(restaurant_dashboard_path, "r") as f:
            dash_custom = json.load(f)
            dash_custom["title"] = dash_custom["title"] + " - " + restaurant_label
            dash_custom["configuration"]["states"]["default"]["name"] = restaurant_label
            dash_custom["configuration"]["filters"]['13b2a505-0a36-8ea8-ec1e-99459f04d698']["keyFilters"][0][
                "predicates"][0]["keyFilterPredicate"]["value"]["defaultValue"] = customer_id
        return dash_custom

if __name__ == "__main__":

    td = ThingsDash()
    public = True

    # create customer/owner
    customer_id = td.create_customer(title="Dan Group LTDA", address="Corso Carlo e Nello Rosselli, 82, 10129 Torino TO, Italia")

    # create restaurant asset
    building_name = f"{customer_id}_building:1"
    building_label = "Corso Rosseli"
    asset_id = td.create_restaurant_asset(asset_name=building_name, asset_label=building_label)  # name should be unique, label no
    # assign asset/building to customer
    td.relation_customer_contains_asset(customer_id, asset_id)
    if public:
        td.assign_device_to_public(asset_id)
    else:
        td.assign_asset_to_customer(customer_id, asset_id)

    # create restaurant device
    restaurant_name = f"{asset_id}_business:1"
    restaurant_token = restaurant_name
    restaurant_label = "A Casa Di Pulcinella"
    restaurant_device_id = td.save_restaurant_device(device_name=restaurant_name, device_label=restaurant_label, device_token=restaurant_name)
    # set restaurant attributes
    td.set_device_attributes(restaurant_token, {"customer_owner": customer_id, "address": "Corso Carlo e Nello Rosselli, 82, 10129 Torino TO, Italia", "description": "", "name": "", "phone": "", "seats": "", "status":"", "dinner_slot": "", "lunch_slot": ""})
    # assign device to asset
    td.relation_asset_contains_device(asset_id, restaurant_device_id)
    # assign device to customer
    if public:
        td.assign_device_to_public(restaurant_device_id)
    else:
        td.assign_device_to_customer(customer_id, restaurant_device_id)


    # create the tables
    dict_tables = {2:1, 4:1, 6:2}  # this should be given by ciccio
    table_number = 0
    for n_seats, n_tables in dict_tables.items():
        for i in range(n_tables):
            table_number += 1
            # create device table
            table_token = f"{restaurant_device_id}_item:table:{table_number}"
            table_device_id = td.save_table_device(table_number=table_number, device_token=table_token, device_restaurant_id=restaurant_device_id)
            # set table attributes
            td.set_device_attributes(table_token, {"customer_owner": customer_id, "seats": n_seats})
            # assign device to customer
            if public:
                td.assign_device_to_public(table_device_id)
            else:
                td.assign_device_to_customer(customer_id, table_device_id)
            # assign device to asset
            td.relation_asset_contains_device(asset_id, table_device_id)
            # assign device to restaurant device
            td.relation_device_contains_device(restaurant_device_id, table_device_id)

    # create the togo device
    togo_token = f"{restaurant_device_id}_togo"
    togo_device_id = td.save_togo_device(device_token=togo_token, restaurant_device_id=restaurant_device_id)
    # assign device to asset
    td.relation_asset_contains_device(asset_id, togo_device_id)
    # assign device to customer
    if public:
        td.assign_device_to_public(togo_device_id)
    else:
        td.assign_device_to_customer(customer_id, togo_device_id)
    # set togo attributes
    td.set_device_attributes(togo_token, {"customer_owner": customer_id})

    # creates a dashboard and assigns it to the owner
    custom_dash = td.customize_dashboard(restaurant_dashboard_path="restaurant_default.json", restaurant_label=restaurant_label, customer_id=customer_id)
    dashboard_id = td.save_dashboard(custom_dash)
    if public:
        # make the dashboard public and get its url
        dashboard_id, public_client_id, dashboard_url = td.assign_dashboard_to_public_customer(dashboard_id)
        print(f"Customer dashboard URL: {dashboard_url}")
    else:
        td.assign_dashboard_to_customer(customer_id, dashboard_id)

    # create order to go
    td.create_togo_order(device_access_token=togo_token, payload={"client": "Ciccio", "order": "1;2", "adress": "canolo grosso siciliano prego"})
    td.create_togo_order(device_access_token=togo_token, payload={"client": "Ricca", "order": "7;5", "adress": "sono amico del padrono"})
    td.create_togo_order(device_access_token=togo_token, payload={"client": "Victor", "order": "8;23", "adress": "lo stesso di Ciccio"})
    td.create_togo_order(device_access_token=togo_token, payload={"client": "Dan", "order": "23;7;19", "adress": "sono il padrono"})

    # create an order in table 1
    td.create_table_order(device_access_token=f"{restaurant_device_id}_item:table:1", payload={"order": "1;2"})
    td.create_table_order(device_access_token=f"{restaurant_device_id}_item:table:1", payload={"order": "3;4"})
    td.create_table_order(device_access_token=f"{restaurant_device_id}_item:table:2", payload={"order": "5;6"})
    td.create_table_order(device_access_token=f"{restaurant_device_id}_item:table:3", payload={"order": "7;8"})
    td.create_table_order(device_access_token=f"{restaurant_device_id}_item:table:4", payload={"order": "9;10"})

    print("end")