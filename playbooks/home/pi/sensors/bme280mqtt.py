#!/usr/bin/python3

import os
import smbus2
import bme280
import bme280.const as oversampling
import json 
from paho.mqtt import client as mqtt
from datetime import timezone
from time import sleep

# For some reason the sensor values varies a lot with spikes down.
# To remedy this, take multiple samples and pick the highest temperature
# which gives consistent values.
samples = 5

port = 1
address = 0x77
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

def failed(msg, error):
    print(msg)
    print(error)
    print(os.system("raspi-gpio get"))
    print(os.system("i2cdetect -y 1"))
    raise error

def read():

    try:
       calibration_params = bme280.load_calibration_params(bus, address)
    except BaseException as error:
        failed("Failed to read calibration params", error)

    # the sample method will take a single reading and return a
    # compensated_reading object
    try:
        data = bme280.sample(bus, address, calibration_params, oversampling.x4)
    except BaseException as error:
        failed("Failed to read calibration params", error)

    return {
        'id': str(data.id), 
        'timestamp': data.timestamp.astimezone(timezone.utc).isoformat(),
        'temp': round(data.temperature, 2),
        'pressure': round(data.pressure, 2),
        'humidity': round(data.humidity, 2)
    }

def send(msg):
    client = mqtt.Client("bme280")
    client.connect("localhost", 1883)
    client.loop_start()
    ret = client.publish("sensors/indoor", json.dumps(msg), qos=1)
    ret.wait_for_publish()
    client.disconnect()

messages = []
for i in range(samples):
    messages.append(read())
    sleep(0.2)
print (messages)

maxMsg = max(messages, key=lambda m: m["temp"])

print ("max", maxMsg)
send(maxMsg)