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

# [dj] WEB APP - Django Framework 
- Name Folder: OrderEatWebApp 
- Name project: orderEat 
- Name app1: food ---> Customer Panel 
- Name app2: rpanel ---> Restaurant Panel
- Name app3: tg-menu --> Customer Panel for Telegram Orders at Restuarant

To run the web app in your localhost, be sure to install the following requirements in a virtual environment, activate the venv and the run the following command: 

$ python manage.py runserver

====
Then click CTRL + link(localhost:8080) in the console and the platform will be available in the browser. 

*You can find a deployed version through Heroku ([PaaS](https://en.wikipedia.org/wiki/Platform_as_a_service)) of the platform here*: 
[link](order-eat2021-django.herokuapp.com) 

## [dj] Default app
![Order Eat](https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Resources/OrderEatDeafaultAPP.png "Start app")
## [dj] Three different apps
The platform has been divided in three different applications exploiting OOP and tasks division
![Three Apps](https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Resources/threeapps.png "Three App")
## [dj] Url Pattern
![Url Patterns](https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Resources/Url%20Pattern.png "Url Pattern")

# [TB] Custom Thingsboard CE
## [TB] Introduction:
The dashboard exploits [Thingsboard CE](https://github.com/thingsboard/thingsboard) installed on a Ubuntu Server 18.04 LTS VM ([IaaS](https://en.wikipedia.org/wiki/Infrastructure_as_a_service)). The main utilized features are:
* **Rule Chains:** Default Root Rule Chain with additional "save attributes" node for shared attributes, and additional "rule chain" node for Alarm Rule Chain. Alarm Rule Chain manages the creation and clearance of alarms based on customer feedbacks according to a custom javascript code;
* **HTTP/MQTT/REST API:** For client, asset and device provision, their telemetry and client/share attributes;
* **Relations:** Relation between Assets, Devices and Clients;
* **Dashboard**
### Thingsboard CE High-Level Architecture
<img src="https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Resources/thingsboard_architecture_overview.png" width="650" />

## [TB] Architecture:
![Custom TB Architecture](https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Resources/dashboard_high_level_architecture.png "Custom TB Architecture")

## [TB] Rule Chains:
<img src="https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Resources/alarm_rule_chain.png" width="750" />

<img src="https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Resources/root_rule_chain.png" width="750" />


# [S&A] Sensors and Actuators
## [S&A] Introduction
* **Main Components:** 
  * [ESP32 Dev Kic C](https://www.espressif.com/en/products/devkits/esp32-devkitc/overview); 
  * [BME680](https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Resources/BME680ShuttleBoard.pdf)
* **Communication:** 
  * **BME680⟺ESP32:** I2C; 
  * **ESP32⟺Thingsboard:** MQTT

## [S&A] Setup
* **Comments:** BME680 SDO ⟹ GND for I2C Address: 0x76

<img src="https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Resources/Wiring.jpg" width="750" />


# [TGB] TelegramBot
1) Interactive chat
2) User friendly keyboard to improve interactiviy
3) Communication with Thingsboard
4) Communication with Firebase
