//For Json
#include <Arduino.h>
#include <ArduinoJson.h>


#include <WiFi.h>
#include <PubSubClient.h>

// Update these with values suitable for your network.
const char* ssid = "vcm2";
const char* password = "20212345";
const char* mqtt_server = "139.59.148.149"; // dont put http, nor port
#define mqtt_port 1883
#define MQTT_USER "1ff2b990-5f52-11eb-bcf2-5f53f5d253b9_business:1"
#define MQTT_PASSWORD ""
#define MQTT_SERIAL_PUBLISH_CH "v1/devices/me/telemetry"
#define MQTT_SERIAL_RECEIVER_CH "/icircuit/ESP32/serialdata/rx"

WiFiClient wifiClient;

PubSubClient client(wifiClient);

#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include "Adafruit_BME680.h"


#define SEALEVELPRESSURE_HPA (1013.25)

Adafruit_BME680 bme; // I2C


void setup_wifi() {
    delay(10);
    // We start by connecting to a WiFi network
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    randomSeed(micros());
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str(),MQTT_USER,MQTT_PASSWORD)) {
      Serial.println("connected");
      //Once connected, publish an announcement...
      client.publish("/icircuit/presence/ESP32/", "hello world");
      // ... and resubscribe
      client.subscribe(MQTT_SERIAL_RECEIVER_CH);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void callback(char* topic, byte *payload, unsigned int length) {
    Serial.println("-------new message from broker-----");
    Serial.print("channel:");
    Serial.println(topic);
    Serial.print("data:");  
    Serial.write(payload, length);
    Serial.println();
}

void publishSerialData(char *serialData){
  if (!client.connected()) {
    reconnect();
  }
  client.publish(MQTT_SERIAL_PUBLISH_CH, serialData);
}

void setup() {
  Serial.begin(115200);
  while (!Serial);
  Serial.println(F("BME680 async test"));

  if (!bme.begin(0x76)) {
    Serial.println(F("Could not find a valid BME680 sensor, check wiring!"));
    while (1);
  }

  // Set up oversampling and filter initialization
  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150); // 320*C for 150 ms



  Serial.setTimeout(500);// Set time out for 
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  reconnect();
  
}

void loop() {
   client.loop();

  // Tell BME680 to begin measurement.
  unsigned long endTime = bme.beginReading();
  if (endTime == 0) {
    Serial.println(F("Failed to begin reading :("));
    return;
  }
  Serial.print(F("Reading started at "));
  Serial.print(millis());
  Serial.print(F(" and will finish at "));
  Serial.println(endTime);

  Serial.println(F("You can do other work during BME680 measurement."));
  delay(50); // This represents parallel work.
  // There's no need to delay() until millis() >= endTime: bme.endReading()
  // takes care of that. It's okay for parallel work to take longer than
  // BME680's measurement time.

  // Obtain measurement results from BME680. Note that this operation isn't
  // instantaneous even if milli() >= endTime due to I2C/SPI latency.
  if (!bme.endReading()) {
    Serial.println(F("Failed to complete reading :("));
    return;
  }

  // Temperature ////////////////////////////////////////////////////////
  StaticJsonDocument<50> doc_temp;
  JsonObject root_temp = doc_temp.to<JsonObject>();
  root_temp["temperature"] = bme.temperature;
  
  char temp_json_buffer[50];
  
  serializeJson(doc_temp, temp_json_buffer);
  Serial.print("Temperature JSON payload: ");
  Serial.println(temp_json_buffer);

  if (client.publish(MQTT_SERIAL_PUBLISH_CH, temp_json_buffer) == true)
  {
    Serial.println("Success sending Temperature MQTT message");
  } 
  else
  {
    Serial.println("Error sending Temperature MQTT message");
  }
  Serial.println();

  // Pressure /////////////////////////////////////////////////////////
  StaticJsonDocument<50> doc_press;
  JsonObject root_press = doc_press.to<JsonObject>();
  root_press["pressure"]=bme.pressure / 100.0;
  
  char press_json_buffer[50];
  
  serializeJson(doc_press, press_json_buffer);
  Serial.print("Pressure JSON payload: ");
  Serial.println(press_json_buffer);

  if (client.publish(MQTT_SERIAL_PUBLISH_CH, press_json_buffer) == true)
  {
    Serial.println("Success sending Pressure MQTT message");
  } 
  else
  {
    Serial.println("Error sending Pressure MQTT message");
  }
  Serial.println();

  // Humidity ///////////////////////////////////////////////////////////////
  StaticJsonDocument<50> doc_hum;
  JsonObject root_hum = doc_hum.to<JsonObject>();
  root_hum["humidity"] = bme.humidity;
  
  char hum_json_buffer[50];
  
  serializeJson(doc_hum, hum_json_buffer);
  Serial.print("Humidity JSON payload: ");
  Serial.println(hum_json_buffer);

  if (client.publish(MQTT_SERIAL_PUBLISH_CH, hum_json_buffer) == true)
  {
    Serial.println("Success sending Humidity MQTT message");
  } 
  else
  {
    Serial.println("Error sending Humidity MQTT message");
  }
  Serial.println();

  // Gas VOC /////////////////////////////////////////////////////////
  StaticJsonDocument<50> doc_gas;
  JsonObject root_gas = doc_gas.to<JsonObject>();
  root_gas["gas"] = bme.gas_resistance / 1000.0;
  
  char gas_json_buffer[50];
  
  serializeJson(doc_gas, gas_json_buffer);
  Serial.print("Gas JSON payload: ");
  Serial.println(gas_json_buffer);

  if (client.publish(MQTT_SERIAL_PUBLISH_CH, gas_json_buffer) == true)
  {
    Serial.println("Success sending Gas MQTT message");
  } 
  else
  {
    Serial.println("Error sending Gas MQTT message");
  }
  Serial.println();

  // Altitude /////////////////////////////////////////////////////////
  StaticJsonDocument<50> doc_alt;
  JsonObject root_alt = doc_alt.to<JsonObject>();
  root_alt["altitude"] = bme.readAltitude(SEALEVELPRESSURE_HPA);
  
  char alt_json_buffer[50];
  
  serializeJson(doc_alt, alt_json_buffer);
  Serial.print("Altitude JSON payload: ");
  Serial.println(alt_json_buffer);

  if (client.publish(MQTT_SERIAL_PUBLISH_CH, alt_json_buffer) == true)
  {
    Serial.println("Success sending Altitude MQTT message");
  } 
  else
  {
    Serial.println("Error sending Altitude MQTT message");
  }
  
  Serial.println();
  delay(5000);
}
