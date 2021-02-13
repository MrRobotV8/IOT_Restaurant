# IOT_Restaurant
Iot Project

# WEB APP - Django Framework 
Name Folder: FastFood 
Name project: orderEat

# setup python virtual env

run following command in folder Fastfood: 


source venv/bin/activate

once your virtual env is activated and you would like to run the platform in your local host, run the following command:

python manage.py runserver

# TO DO WEB APP


# [TB] Custom Thingsboard
## [TB] Introduction:
The dashboard exploits [Thingsboard CE](https://github.com/thingsboard/thingsboard), specifically the following features:
* **Rule Chains:** Default Root Rule Chain with additional "save attributes" node for shared attributes, and additional "rule chain" node for Alarm Rule Chain. Alarm Rule Chain manages the creation and clearance of alarms based on customer feedbacks according to a custom javascript code;
* **HTTP/MQTT/REST API:** For client, asset and device provision, their telemetry and client/share attributes;
* **Relations:** Relation between Assets, Devices and Clients;
* **Dashboard**

## [TB] Architecture:
![Architecture](https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Sensors%26Actuators/dashboard_high_level_architecture.png "Architecture")

## [TB] Rule Chains:
![Alarm Rule Chain](https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Sensors%26Actuators/alarm_rule_chain.png "Alarm Rule Chain")
![Root Rule Chain](https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Sensors%26Actuators/root_rule_chain.png "Root Rule Chain")

# [S&A] Sensors and Actuators
## [S&A] Introduction
* **Main Components:** [ESP32 Dev Kic C](https://www.espressif.com/en/products/devkits/esp32-devkitc/overview); [BME680](https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Sensors%26Actuators/BME680ShuttleBoard.pdf)
* **Communication:** 
  * **BME680<->ESP32:** I2C; 
  * **BME680<->Thingsboard:** MQTT

## [S&A] Setup
* **Comments:** BME680 SDO -> GND for I2C Address: 0x76
![Wiring](https://github.com/MrRobotV8/IOT_Restaurant/blob/master/Sensors%26Actuators/Wiring.jpg "Wiring")
