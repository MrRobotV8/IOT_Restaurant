
import logging
import random

import requests
import json

def tenant_login(url, username, password):
    url_api = f"{url}/api/auth/login"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = {"username": str(username), "password": str(password)}
    x = requests.post(url_api, data=json.dumps(payload), headers=headers)
    if x.status_code==200:
        jwt_token = json.loads(x.text)["token"]
        return jwt_token

def create_customer(url, bearer, address=None, city=None, country=None, email=None, name=None, phone=None, state=None, title=None, zip=None):
    url_api = f"{url}/api/customer"
    headers = {"X-Authorization": "Bearer " + bearer, "Content-Type": "application/json"}
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
        customer_id = json.loads(x.text)["id"]["id"]
        return customer_id

def create_restaurant_asset(url, bearer, label=None, name=None):
    url_api = f"{url}/api/asset"
    headers = {"X-Authorization": "Bearer " + bearer, "Content-Type": "application/json"}
    payload = {}

    if label is not None:
        payload["label"] = label
    if name is not None:
        payload["name"] = name
    if type is not None:
        payload["type"] = "restaurant_children"

    x = requests.post(url_api, data=json.dumps(payload), headers=headers)
    if x.status_code==200:
        asset_id = json.loads(x.text)["id"]["id"]
        return asset_id

def relation_customer_contains_asset(url, bearer, customer_id, asset_id):
    url_api = f"{url}/api/relation"
    headers = {"X-Authorization": "Bearer " + bearer, "Content-Type": "application/json"}

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

def assign_asset_to_customer(url, bearer, customer_id, asset_id):
    url_api = f"{url}/api/customer/{customer_id}/asset/{asset_id}"
    headers = {"X-Authorization": "Bearer " + bearer, "Content-Type": "application/json"}

    payload={}
    x = requests.post(url_api, data=json.dumps(payload), headers=headers)
    if x.status_code==200:
        return True

def provision_restaurant_device(url, bearer, restaurant_name):
    url_api = f"{url}/api/v1/provision"
    headers = {"X-Authorization": "Bearer " + bearer, "Content-Type": "application/json"}

    payload = {
        "deviceName": f"{restaurant_name}",
        "provisionDeviceKey": "restaurant_provision_key",
        "provisionDeviceSecret": "provision_device_secret"
    }
    x = requests.post(url_api, data=json.dumps(payload), headers=headers)
    if x.status_code==200:
        acess_token = json.loads(x.text)["credentialsValue"]
        return acess_token

def save_restaurant_device(url, bearer, device_name, custom_access_token):
    url_api = f"{url}/api/device?accessToken={custom_access_token}"
    headers = {"X-Authorization": "Bearer " + bearer, "Content-Type": "application/json", "Accept": "application/json"}

    payload = {
        "name": device_name,
        "type": "restaurant_device_profile",
        "label": "restaurant device"
        }

    x = requests.post(url_api, data=json.dumps(payload), headers=headers)
    if x.status_code==200:
        device_id = json.loads(x.text)["id"]["id"]
        return device_id


def relation_asset_contains_device(url, bearer, asset_id, device_id):
    url_api = f"{url}/api/relation"
    headers = {"X-Authorization": "Bearer " + bearer, "Content-Type": "application/json"}

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

def assign_device_to_customer(url, bearer, customer_id, device_id):
    url_api = f"{url}/api/customer/{customer_id}/device/{device_id}"
    headers = {"X-Authorization": "Bearer " + bearer, "Content-Type": "application/json"}

    payload={}
    x = requests.post(url_api, data=json.dumps(payload), headers=headers)
    if x.status_code==200:
        return True

def save_table_device(url, bearer, table_number, custom_access_token):
    url_api = f"{url}/api/device?accessToken={custom_access_token}"
    headers = {"X-Authorization": "Bearer " + bearer, "Content-Type": "application/json", "Accept": "application/json"}

    payload = {
        "name": f"Table {table_number}",
        "type": "table_device_profile",
        "label": "table device"
        }

    x = requests.post(url_api, data=json.dumps(payload), headers=headers)
    if x.status_code==200:
        device_id = json.loads(x.text)["id"]["id"]
        return device_id

def save_togo_device(url, bearer, custom_access_token):
    url_api = f"{url}/api/device?accessToken={custom_access_token}"
    headers = {"X-Authorization": "Bearer " + bearer, "Content-Type": "application/json", "Accept": "application/json"}

    payload = {
        "name": f"To Go",
        "type": "togo_device_profile",
        "label": "togo device"
        }

    x = requests.post(url_api, data=json.dumps(payload), headers=headers)
    if x.status_code==200:
        device_id = json.loads(x.text)["id"]["id"]
        return device_id

def set_device_attributes(url, bearer, device_token, payload):
    url_api = f"{url}/api/v1/{device_token}/attributes"
    headers = {"X-Authorization": "Bearer " + bearer, "Content-Type": "application/json", "Accept": "application/json"}

    x = requests.post(url_api, data=json.dumps(payload), headers=headers)
    if x.status_code==200:
        return True

def save_dashboard(url, bearer, payload):
    url_api = f"{url}/api/dashboard"
    headers = {"X-Authorization": "Bearer " + bearer, "Content-Type": "application/json", "Accept": "application/json"}

    x = requests.post(url_api, data=json.dumps(payload), headers=headers)
    if x.status_code==200:
        dashboard_id = json.loads(x.text)["id"]["id"]
        return dashboard_id

def assign_dashboard_to_customer(url, bearer, customer_id, dashboard_id):
    url_api = f"{url}/api/customer/{customer_id}/dashboard/{dashboard_id}"
    headers = {"X-Authorization": "Bearer " + bearer, "Content-Type": "application/json", "Accept": "application/json"}

    payload={}

    x = requests.post(url_api, data=json.dumps(payload), headers=headers)
    if x.status_code==200:
        return True

def assign_dashboard_to_public_customer(url, bearer, dashboard_id):
    url_api = f"{url}/api/customer/public/dashboard/{dashboard_id}"
    headers = {"X-Authorization": "Bearer " + bearer, "Content-Type": "application/json", "Accept": "application/json"}

    payload={}

    x = requests.post(url_api, data=json.dumps(payload), headers=headers)
    if x.status_code==200:
        dashboard_id = json.loads(x.text)["id"]["id"]
        public_client_id = json.loads(x.text)["assignedCustomers"][0]["customerId"]["id"]
        dashboard_url = f"{url}/dashboard/{dashboard_id}?publicId={public_client_id}"
        return dashboard_id, public_client_id, dashboard_url

# rnd = random.randint(0, 999)
# ThingsBoard REST API URL
url = "http://139.59.148.149"
port = 8080
url_all = f"{url}:{port}"
# Default Tenant Administrator credentials
username = "tenant@thingsboard.org"
password = "tenant"

# login
jwt_token = tenant_login(url_all, username="tenant@thingsboard.org", password="tenant")


# create customer
customer_id = create_customer(url_all, jwt_token, title="joao", address="av coscovado")

# create restaurant asset
restaurant_name = "churrascaria boi gordo"
asset_id = create_restaurant_asset(url_all, jwt_token, name=restaurant_name)

# assign asset to customer
relation_customer_contains_asset(url_all, jwt_token, customer_id, asset_id)
assign_asset_to_customer(url_all, jwt_token, customer_id, asset_id)

# create restaurant device
# access_token = provision_restaurant_device(url_all, jwt_token, "churrascaria boi gordo")
restaurant_device_id = save_restaurant_device(url_all, jwt_token, restaurant_name, "custom_access_token")
# set restaurant attributes
restaurant_token = f"{asset_id}_1"
set_device_attributes(url_all, jwt_token, restaurant_token, {"address": "via boi gordo", "description": "", "name": "", "phone": "", "seats": "", "status":"", "dinner_slot": "", "lunch_slot": ""})
# assign device to asset
relation_asset_contains_device(url_all, jwt_token, asset_id, restaurant_device_id)
# assign device to customer
assign_device_to_customer(url_all, jwt_token, customer_id, restaurant_device_id)

# create the tables
dict_tables = {2:1, 4:1, 6:2}  # this should be given by ciccio
table_number = 0
for n_seats, n_tables in dict_tables.items():
    for i in range(n_tables):
        table_number += 1
        # create device table
        table_token = f"{restaurant_device_id}_{table_number}"
        table_device_id = save_table_device(url_all, jwt_token, table_number, table_token)
        # set table attributes
        set_device_attributes(url_all, jwt_token, table_token, {"seats": n_seats})
        # assign device to asset
        relation_asset_contains_device(url_all, jwt_token, asset_id, table_device_id)
        # assign device to customer
        assign_device_to_customer(url_all, jwt_token, customer_id, table_device_id)

# create the togo device
togo_token = f"{restaurant_device_id}_togo"
togo_device_id = save_togo_device(url_all, jwt_token, togo_token)
# assign device to asset
relation_asset_contains_device(url_all, jwt_token, asset_id, togo_device_id)
# assign device to customer
assign_device_to_customer(url_all, jwt_token, customer_id, togo_device_id)

# creates a dashboard and assigns it to the owner
f = open("template_restaurant.json")
dash_json = json.load(f)
dashboard_id = save_dashboard(url_all, jwt_token, dash_json)
assign_dashboard_to_customer(url_all, jwt_token, customer_id, dashboard_id)

# make the dashboard public and get its url
dashboard_id, public_client_id, dashboard_url = assign_dashboard_to_public_customer(url_all, jwt_token, dashboard_id)
print(dashboard_url)