# Smart home playbooks

Collection of scripts for setting up home automation sensors, monitoring and control devices. 
Raspberry Pi acts as a hub and collects sensor data from numerous wireless ESP8266/ESP32 devices. 
Raspberry Pi has 4G connectivity and MQTT bridge forwards all collected messages to a remote server where they can be stored (InfluxDB) and visualized (Grafana).

# Components

## boot

Example files to copy to Raspberry Pi's ```boot``` partition in order to activate wireless network and ssh on the first boot.

Find out the correct IP address e.g. using ```arp -a``` command on a Mac and ssh to the server with default user (```pi```/```raspberry```). Change password and copy your ssh public key into ```.ssh/authorized_keys```. Now you are ready to execute Ansible playbooks.

[More about setting up headless Raspberry Pi](https://www.raspberrypi.org/documentation/configuration/wireless/headless.md)

## Ansible Playbooks for setting up Raspberry Pi

```
pip3 install ansible
```

Add your hosts into ```/etc/ansible/hosts```
```
[raspberrypi]
rpi
[raspberrypi:vars]
ansible_python_interpreter=/usr/bin/python3
```

Execute playbooks
```
cd playbooks
cp common.yml.{template,}
ansible-playbook setup.yml
```

##### setup.yml 

Basic setup of Raspberry Pi 4b.

##### 4g.yml

Configure Huawei E392 4G dongle. ```inet_down.sh``` script tries to fix broken internet and/or reboot in case ifup/down didn't fix the connection.

##### weather.yml

Setup a MQTT broker which gathers observations from connected sensors and other wireless devices on the local network. 

Raspberry Pi is wired with BME280 temperature, humidity and pressure sensor. The sensor is read once per minute ```bme280mqtt.py``` and values are sent in a MQTT message.

Outside temperature is polled using the [FMI Open data WFS service](https://en.ilmatieteenlaitos.fi/open-data-manual).

##### wireguard.yml

Establish Wireguard VPN tunnel to a remote server. Raspberry Pi has no open ports to the world
but is accessible through Wireguard tunnel from the remote server.

[WireGuard Site-to-Site](https://gist.github.com/insdavm/b1034635ab23b8839bf957aa406b5e39).

#### router.yml

Share 4G internet connection to wireless devices. Could use Raspberry Pi's internal wireless (hostapd) but external routers offer better range and dual bands (ESP8266 has no 5Ghz wlan).

#### eth-bridge-to-wlan.yml

Share existing wireless network to wired ethernet device e.g TV.

#### motion.yml

Add Raspberry Pi HQ Camera as a security camera with Motion Eye.

#### vattenfall.yml

Scrape energy consumption data from [Vattenfall Oma Energia](https://omaenergia.vattenfall.fi/) daily.

#### airplay.yml

Airplay server. Can use Raspberrys audio-out jack or USB dac.

## Arduino

Sketch files below are for Wemos D1 Mini ESP8266 device. They connect to Raspberry Pi network, read measurements once per minute and send them as a MQTT message.

##### Central heating control and monitor

[Waveshare MG996R Servo](https://www.waveshare.com/product/modules/motors-servos/mg996r-servo.htm) linked to temperature knob of central heating unit. Two waterproof 1-Wire DS18B20 digital temperature sensors reading outbound and inbound temperatures.

##### Outside and inside temperature sensors

BME280 sensor for indoor temperature and includes support for another 1-Wire DS18B20 sensor for outdoor reading.

##### VMA342

The same as BME280 above but in addition has support for air quality sensor combo board (CCS811).

## Micropython

Tested on ESP32 devices only.

#### e-paper

ESP32 device with connected E-paper display shows latest temperature measurements.