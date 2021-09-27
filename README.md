# Raspberry Pi Playbooks

Collection of Ansible and Arduino scripts for setting up Raspberry Pi as a weather, security, and home automation hub.

# Components

## boot

Example files to copy to Raspberry Pi's ```boot``` partition in order to activate wireless network and ssh on the first boot.

Find out the correct IP address e.g. using ```arp -a``` command on a Mac and ssh to the server with default user (```pi```/```raspberry```). Change password and copy your ssh public key into ```.ssh/authorized_keys```. Now you are ready to execute Ansible playbooks.

[More about setting up headless Raspberry Pi](https://www.raspberrypi.org/documentation/configuration/wireless/headless.md)

## Playbooks

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

Setup a MQTT broker which gathers all observations from wired sensors and other devices on the local network. MQTT bridge forwards all messages to a remote server where they can be stored (InfluxDB) and visualized (Grafana).

Raspberry Pi is wired with BME280 temperature, humidity and pressure sensor. The sensor is read once per minute ```bme280mqtt.py``` and values are sent in a MQTT message.

Outside temperature is polled using the [FMI Open data WFS service](https://en.ilmatieteenlaitos.fi/open-data-manual).

##### wireguard.yml

Establish Wireguard VPN tunnel to remote server. Raspberry Pi has no open ports to the world
but is accessible through Wireguard.

[WireGuard Site-to-Site](https://gist.github.com/insdavm/b1034635ab23b8839bf957aa406b5e39).

#### router.yml

Share 4G internet connection to wireless devices. Could use Raspberry Pi's internal wireless (hostapd) but external routers offer better range and dual bands (ESP8266 has no 5Ghz wlan).

#### eth-bridge-to-wlan.yml

Share existing wireless network to wired ethernet device e.g TV.

#### motion.yml

Add Raspberry Pi HQ Camera as a security camera with Motion Eye.

#### vattenfall.yml

Scrape energy consumption data from Vattenfall website daily.

[Vattenfall Oma Energia](https://omaenergia.vattenfall.fi/)
## Arduino

Sketch files below are for Wemos D1 Mini ESP8266 device. They connect to Raspberry Pi network, read measurements once per minute and send them as a MQTT message.

##### DS18B20

Waterproof 1-Wire DS18B20 digital temperature sensor.

##### VMA342

Air quality sensor combo board with CCS811 and BME280 sensors.