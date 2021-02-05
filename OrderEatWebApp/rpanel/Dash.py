"Ciccio Refactoring" 
from thingsboard.main import ThingsDash

class Dash(ThingsDash):
    def __init__(self, config):
        ThingsDash.__init__(self)
        #self.database = database
        self.email = config['email']
        self.uid = config['uid']
        self.address = config['address']
        self.name = config['name']
        self.status = config['status']
        self.description = config['description']
        self.seats = config['seats']
        self.phone = config['phone']
        self.tables = config['tables']
        print(config)
        #self.lunch_slot = config['lunch-slot'] # comment
        #self.dinner_slot = config['dinner-slot'] # comment
            

    def create_dash(self):
        public = True
        owner_id = self.create_customer(title=self.email, address=self.address)  
        print("owner_id:")
        print(owner_id)
        building_name = f"{owner_id}_building:1"
        print("building name " + str(building_name))
        building_label = self.address  # Indirizzo del ristorante
        print("builing_label " + str(building_label))
        building_id = self.create_restaurant_asset(asset_name=building_name, asset_label=building_label)
        print("builing_id " + str(building_id))
        #TOKEN_TELEMETRY
        #self.database.child('restaurants').child(self.uid).child('details').child('token_telemetry').set(building_id)
        #assign asset/building to customer
        self.relation_customer_contains_asset(owner_id, building_id)
        if public:
            self.assign_device_to_public(building_id)
        else:
            self.assign_asset_to_customer(owner_id, building_id)

        #create restaurant device
        restaurant_name = f"{building_id}_business:1"
        restaurant_token = restaurant_name #Entity Name
        restaurant_label = self.name  # Nome del ristorante
        restaurant_device_id = self.save_restaurant_device(device_name=restaurant_name, device_label=restaurant_label,
                                                        device_token=restaurant_name)
        #TOKEN_ORDER
        #self.database.child('restaurants').child(self.uid).child('details').child('token_order').set(restaurant_device_id)
        # set restaurant attributes
        self.set_device_attributes(restaurant_token, {"customer_owner": owner_id, 
                                                    "address": self.address,
                                                    "description": self.description,
                                                    "name": self.name,
                                                    "phone": self.phone,
                                                    "seats": self.seats,
                                                    "status": self.status,
                                                    "dinner_slot": "",
                                                    "lunch_slot": ""})  #TODO: delete?
        # assign device to asset
        self.relation_asset_contains_device(building_id, restaurant_device_id)
        # assign device to customer
        if public:
            self.assign_device_to_public(restaurant_device_id)
        else:
            self.assign_device_to_customer(owner_id, restaurant_device_id)

        # create the tables
        dict_tables = {2: int(self.tables['2']), 4: int(self.tables['4']), 6: int(self.tables['6'])} 
        print(dict_tables) # this should be given by ciccio
        table_number = 0
        for n_seats, n_tables in dict_tables.items():
            for i in range(n_tables):
                table_number += 1
                # create device table
                table_token = f"{restaurant_device_id}_item:table:{table_number}"
                table_device_id = self.save_table_device(table_number=table_number, device_token=table_token,
                                                    device_restaurant_id=restaurant_device_id)
                # set table attributes
                self.set_device_attributes(table_token, {"customer_owner": owner_id, "seats": n_seats})
                # assign device to customer
                if public:
                    self.assign_device_to_public(table_device_id)
                else:
                    self.assign_device_to_customer(owner_id, table_device_id)
                # assign device to asset
                self.relation_asset_contains_device(building_id, table_device_id)
                # assign device to restaurant device
                self.relation_device_contains_device(restaurant_device_id, table_device_id)

        # create the togo device
        togo_token = f"{restaurant_device_id}_togo"
        togo_device_id = self.save_togo_device(togo_token, restaurant_device_id)
        # assign device to asset
        self.relation_asset_contains_device(building_id, togo_device_id)
        # assign device to owner
        if public:
            self.assign_device_to_public(togo_device_id)
        else:
            self.assign_device_to_customer(owner_id, togo_device_id)
        # set togo attributes
        self.set_device_attributes(togo_token, {"customer_owner": owner_id})

        # creates a dashboard and assigns it to the owner
        custom_dash = self.customize_dashboard(restaurant_dashboard_path="thingsboard/restaurant_default.json",
                                            restaurant_label=restaurant_label, customer_id=owner_id)
        dashboard_id = self.save_dashboard(custom_dash)
        if public:
            # make the dashboard public and get its url
            dashboard_id, public_client_id, dashboard_url = self.assign_dashboard_to_public_customer(dashboard_id)
            print(f"Customer dashboard URL: {dashboard_url}")
        else:
            self.assign_dashboard_to_customer(owner_id, dashboard_id)
        #DASHBOARD_URL
        #self.database.child('restaurants').child(self.uid).child('details').child('thingsboard').set(dashboard_url)
        things_dict = {
            'token_telemetry': building_id,
            'token_order': restaurant_device_id,
            'thingsboard': dashboard_url
        }
        return things_dict
