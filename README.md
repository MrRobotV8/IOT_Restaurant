# IOT_Restaurant
OrderEat project for course Programming for IOT @ PoliTo.

1) Scalable on the number of users;
2) Scalable on the number of restaurants;
3) Scalable to manage various IoT devices, users and contexts (e.g. adding/removing new devices, users and context at run-time without modifying the source-code). 
4) Automatic setup process;
5) Comfort for the customer;
6) Consumption control for restaurateur;
7) Unique Configuration File; 
8) Guarantee information exchange among the actors in the system over the internet (REST and MQTT)

-Config File is shared in the folder between actors

# WEB APP - Django Framework 
- Name Folder: OrderEatWebApp 
- Name project: orderEat 
- Name app1: food ---> Customer Panel 
- Name app2: rpanel ---> Restaurant Panel
- Name app3: tg-menu --> Customer Panel for Telegram Orders at Restuarant

To run the web app in your localhost, be sure to install the following requirements in a virtual environment, activate the venv and the run the following command: 

$ python manage.py runserver

====
Then click CTRL + link(localhost:8080) in the console and the platform will be available in the browser. 

*You can find a deployed version of the platform here: 
[link](order-eat2021-django.herokuapp.com) 

We have tried to adopt *Agile Methodology*
## Requirements
- asgiref==3.3.1 \n
- dj-database-url==0.5.0 \n
- Django==3.1.4
- django-heroku==0.3.1
- gcloud==0.17.0
- googleapis-common-protos==1.52.0
- gunicorn==20.0.4
- httplib2==0.18.1
- jws==0.1.3
- oauth2client==3.0.0
- paho-mqtt==1.5.1
- Pillow==8.0.1
- protobuf==3.14.0
- psycopg2==2.8.6
- pyasn1==0.4.8
- pyasn1-modules==0.2.8
- pycryptodome==3.4.3
- Pyrebase==3.0.27
- python-jwt==2.0.1
- pytz==2020.5
- requests==2.11.1
- requests-toolbelt==0.7.0
- rsa==4.6
- six==1.15.0
- sqlparse==0.4.1
- whitenoise==5.2.0

## WHY DJANGO?
Django is characterized by:
1) *High-level framework for rapid web development*
2) *Complete stack of tools*
3) *Data modelled with Python classes*
4) *Production-ready data admin interface, generated dynamically*
5) *Elegant system for mapping URLs to Python code*
6) *Generic views’ to handle common requests*
7) *Clean, powerful template language*
8) *OOP approach*
## Default app
![Order Eat](https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Resources/OrderEatDeafaultAPP.png "Start app")
## Three different apps
The platform has been divided in three different applications exploiting OOP and tasks division
![Three Apps](https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Resources/threeapps.png "Three App")
## Url Pattern
![Url Patterns](https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Resources/Url%20Pattern.png "Url Pattern")

# [TB] Custom Thingsboard CE
## [TB] Introduction:
The dashboard exploits [Thingsboard CE](https://github.com/thingsboard/thingsboard) installed on a Ubuntu Server 18.04 LTS VM ([PaaS](https://en.wikipedia.org/wiki/Platform_as_a_service)). The main utilized features are:
* **Rule Chains:** Default Root Rule Chain with additional "save attributes" node for shared attributes, and additional "rule chain" node for Alarm Rule Chain. Alarm Rule Chain manages the creation and clearance of alarms based on customer feedbacks according to a custom javascript code;
* **HTTP/MQTT/REST API:** For client, asset and device provision, their telemetry and client/share attributes;
* **Relations:** Relation between Assets, Devices and Clients;
* **Dashboard**
### Thingsboard CE High-Level Architecture
![TB Architecture](https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Resources/thingsboard_architecture_overview.png "TB Architecture")

## [TB] Architecture:
![Custom TB Architecture](https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Resources/dashboard_high_level_architecture.png "Custom TB Architecture")

## [TB] Rule Chains:
![Alarm Rule Chain](https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Resources/alarm_rule_chain.png "Alarm Rule Chain")
![Root Rule Chain](https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Resources/root_rule_chain.png "Root Rule Chain")

# [S&A] Sensors and Actuators
## [S&A] Introduction
* **Main Components:** [ESP32 Dev Kic C](https://www.espressif.com/en/products/devkits/esp32-devkitc/overview); [BME680](https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Resources/BME680ShuttleBoard.pdf)
* **Communication:** 
  * **BME680<->ESP32:** I2C; 
  * **BME680<->Thingsboard:** MQTT

## [S&A] Setup
* **Comments:** BME680 SDO -> GND for I2C Address: 0x76
![Wiring](https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Resources/Wiring.jpg "Wiring")
