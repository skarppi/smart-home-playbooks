#include <OneWire.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <TimeLib.h>

// Network SSID
const char* ssid = "{{wlan_ssid}}";
const char* password = "{{wlan_passphrase}}";

// MQTT
WiFiClient espClient;
const char* mqtt_server = "192.168.200.1";
const char* temperature_topic_pannu = "sensors/pannu";
const char* temperature_topic_patteri = "sensors/patteri";

PubSubClient mqttClient(espClient);

// Define NTP Client to get time
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "192.168.200.1");

// Sensor on pin 4
OneWire  ds(D4);

void setup(void) {
  Serial.begin(9600);

  // Connect WiFi
  WiFi.hostname("ds18b20");
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
}

void reconnect() {
  while (!mqttClient.connected()) {
    Serial.print("Connecting to MQTT broker ...");
    if (mqttClient.connect("DS18820")) {
      Serial.println("OK");
    } else {
      Serial.print("Error : ");
      Serial.print(mqttClient.state());
      Serial.println(" Wait 5 seconds before retry");
      delay(5000);
    }
  }
}

char* getUTCTime() {
  timeClient.update();

  unsigned long t = timeClient.getEpochTime();

  // 2021-02-18T21:02:01.934083+00:00
  char now[34];
  sprintf(now, "%02d-%02d-%02dT%02d:%02d:%02d.000000+00:00", year(t), month(t), day(t), hour(t), minute(t), second(t));

  //Serial.print("Time is now ");
  //Serial.println(now);
  return now;
}

void loop(void) {
  byte i;
  byte present = 0;
  byte type_s;
  byte data[12];
  byte addr[8];
  float celsius;

  if ( !ds.search(addr)) {
    ds.reset_search();
    delay(60000);
    return;
  }

  if (!mqttClient.connected()) {
    reconnect();
  }
  mqttClient.loop();
  
  if (OneWire::crc8(addr, 7) != addr[7]) {
      Serial.println("CRC is not valid!");
      return;
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
      return;
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

  unsigned int raw = (data[1] << 8) | data[0];
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
  celsius = (float)raw / 16.0;

  StaticJsonDocument<200> doc;
  doc["id"] = "DS18B20-" + String(addr[7]);
  doc["timestamp"] = getUTCTime();
  doc["temp"] = celsius;

  char output[256];
  serializeJson(doc, output);

  Serial.println(output);

  digitalWrite(2,HIGH); 

  if (doc["id"] == "DS18B20-102") {
    mqttClient.publish(temperature_topic_pannu, output, true);
  } else if (doc["id"] == "DS18B20-81") {
    mqttClient.publish(temperature_topic_patteri, output, true);
  } else {
    Serial.print("Unknown ROM =");
    for( i = 0; i < 8; i++) {
      Serial.write(' ');
      Serial.print(addr[i], HEX);
    }
  }
  
  //
  mqttClient.disconnect();
  delay(2000);
  digitalWrite(2,LOW);
}
