#include <Wire.h>
#include <OneWire.h>
#include <SparkFunBME280.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <TimeLib.h>

// Sensor on pin 4
OneWire  ds(D4);

// Network SSID
const char* ssid = "{{wlan_ssid}}";
const char* password = "{{wlan_passphrase}}";

// MQTT
WiFiClient espClient;
const char* mqtt_server = "192.168.200.1";
const char* topic = "sensors/vintti";

const char* outsideTopic = "sensors/takapiha";

PubSubClient mqttClient(espClient);

// Define NTP Client to get time
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "192.168.200.1");

//Global sensor objects
BME280 myBME280;

void setup() {
  Serial.begin(9600);

  // Connect WiFi
  WiFi.hostname("bme280");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
 
  // Print the IP address
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  mqttClient.setServer(mqtt_server, 1883);

  timeClient.begin();
  timeClient.update();

  Serial.println("Setup done");
  
  Wire.begin(D1,D2); // Define which ESP8266 pins to use for SDA=D1, SCL=D2 of the Sensor
  
  //Initialize BME280
  //For I2C, enable the following and disable the SPI section
  myBME280.settings.commInterface = I2C_MODE;
  myBME280.settings.I2CAddress = 0x76;
  myBME280.settings.runMode = 3; //Normal mode
  myBME280.settings.tStandby = 0;
  myBME280.settings.filter = 4;
  myBME280.settings.tempOverSample = 1;
  myBME280.settings.pressOverSample = 1;
  myBME280.settings.humidOverSample = 1;

  //Calling .begin() causes the settings to be loaded
  delay(10); //Make sure sensor had enough time to turn on. BME280 requires 2ms to start up.
  myBME280.begin();
}

void loop() {
  char output[256];
  
  char now[34];
  getUTCTime(now);
  Serial.println(now);

  if (!mqttClient.connected()) {
    reconnect();
  }
  mqttClient.loop();
   
  float BMEtemp = myBME280.readTempC();
  float BMEPressure = myBME280.readFloatPressure() / 100;
  float BMEhumid = myBME280.readFloatHumidity();

  StaticJsonDocument<200> doc;
  doc["id"] = "BME280";
  doc["timestamp"] = now;
  doc["temp"] = BMEtemp;
  doc["pressure"] = BMEPressure;
  doc["humidity"] = BMEhumid;
  doc["altitude"] = myBME280.readFloatAltitudeMeters();

  serializeJson(doc, output);
  Serial.println(output);

  mqttClient.publish(topic, output, true);

  float outside = readOutsideTemp();

  if (outside > -100) {
    StaticJsonDocument<200> doc;
    doc["id"] = "DS18B20";
    doc["timestamp"] = now;
    doc["temp"] = outside;
  
    serializeJson(doc, output);
    Serial.println(output);
  
    mqttClient.publish(outsideTopic, output, true);
  }
    
  mqttClient.disconnect();  

  delay(60000);
}

float readOutsideTemp() {
  byte i;
  byte present = 0;
  byte type_s;
  byte data[12];
  byte addr[8];
  float NA = -9999;

  if ( !ds.search(addr)) {
    ds.reset_search();
    Serial.println("OneWire device not found");
    return NA;
  }

  ds.reset_search();

  if (OneWire::crc8(addr, 7) != addr[7]) {
      Serial.println("CRC is not valid!");
      return NA;
  }
  Serial.println();

  // the first ROM byte indicates which chip
  switch (addr[0]) {
    case 0x10:
      Serial.println("Chip = DS18S20");  // or old DS1820
      type_s = 1;
      break;
    case 0x28:
      Serial.println("Chip = DS18B20");
      type_s = 0;
      break;
    case 0x22:
      Serial.println("Chip = DS1822");
      type_s = 0;
      break;
    default:
      Serial.println("Device is not a DS18x20 family device.");
      return NA;
  } 

  ds.reset();
  ds.select(addr);
  ds.write(0x44,1);         // start conversion, with parasite power on at the end
  
  delay(1000);     // maybe 750ms is enough, maybe not
  // we might do a ds.depower() here, but the reset will take care of it.
  
  present = ds.reset();
  ds.select(addr);    
  ds.write(0xBE);         // Read Scratchpad

  for ( i = 0; i < 9; i++) {           // we need 9 bytes
    data[i] = ds.read();
  }

  // convert the data to actual temperature

  int16_t raw =  (int16_t)((data[1] << 8) | data[0]);
  if (type_s) {
    raw = raw << 3; // 9 bit resolution default
    if (data[7] == 0x10) {
      // count remain gives full 12 bit resolution
      raw = (raw & 0xFFF0) + 12 - data[6];
    }
  } else {
    byte cfg = (data[4] & 0x60);
    if (cfg == 0x00) raw = raw << 3;  // 9 bit resolution, 93.75 ms
    else if (cfg == 0x20) raw = raw << 2; // 10 bit res, 187.5 ms
    else if (cfg == 0x40) raw = raw << 1; // 11 bit res, 375 ms
    // default is 12 bit resolution, 750 ms conversion time
  }
  return (float)raw / 16.0;
}

void reconnect() {
  while (!mqttClient.connected()) {
    Serial.print("Connecting to MQTT broker ...");
    if (mqttClient.connect("VMA342")) {
      Serial.println("OK");
    } else {
      Serial.print("Error : ");
      Serial.print(mqttClient.state());
      Serial.println(" Wait 5 seconds before retry");
      delay(5000);
    }
  }
}

void getUTCTime(char* now) {
  timeClient.update();

  unsigned long t = timeClient.getEpochTime();

  // 2021-02-18T21:02:01.934083+00:00
  sprintf(now, "%02d-%02d-%02dT%02d:%02d:%02d.000000+00:00", year(t), month(t), day(t), hour(t), minute(t), second(t));

  Serial.print("Time is now ");
  Serial.println(now);
}
