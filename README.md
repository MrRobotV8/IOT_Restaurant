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
