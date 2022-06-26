from machine import Pin, I2C
from time import gmtime
import bme280
import uasyncio as asyncio
import connection

i2c = I2C(1, scl=Pin(33), sda=Pin(32), freq=10000)


async def start():

    while True:
        year, month, day, hour, minute, second, ms, dayinyear = gmtime()

        if year < 2020:
            print("No time yet, sleeping 10...")
            await asyncio.sleep(10)
        else:
            now = "{:4}-{:02}-{:02}T{:02}:{:02}:{:02}.000000+00:00".format(
                year, month, day, hour, minute, second)

            bme = bme280.BME280(i2c=i2c)

            temp, pressure, humidity = bme.read_compensated_data()

            msg = {
                "id": "ESP32-bme280",
                "timestamp": now,
                "temp": temp,
                "pressure": pressure / 100,
                "humidity": humidity,
            }

            print(msg)

            await connection.publish('sensors/indoor',  msg)

            await asyncio.sleep(60)
