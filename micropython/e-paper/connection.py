from mqtt_as import MQTTClient, config
from config import wifi_led, blue_led
import uasyncio as asyncio
import ujson

from state import latest

 # Instantiate event loop with any args before running code that uses it
loop = asyncio.get_event_loop()

# Demonstrate scheduler is operational.
async def heartbeat():
    blue_led(True)
    await asyncio.sleep(1)
    blue_led(False)

def sub_cb(topic, msg, retained):
    sensor = topic.decode()

    print((sensor, msg, retained))
    loop.create_task(heartbeat())

    if sensor in latest:
        latest[sensor] = ujson.loads(msg)

async def wifi_han(state):
    wifi_led(not state)
    if state:
        print('WiFi is up.')
    else:
        print('WiFi is down.')
    await asyncio.sleep(1)

async def conn_han(client):
    await client.subscribe('sensors/#', 1)

# Define configuration
config['subs_cb'] = sub_cb
config['wifi_coro'] = wifi_han
config['connect_coro'] = conn_han
config['clean'] = False
config['will'] = ('result', 'Goodbye cruel world!', False, 0)
config['keepalive'] = 120
config['clean'] = True

# Set up client
MQTTClient.DEBUG = True  # Optional
client = MQTTClient(config)

async def start():
    try:
        print('Connecting...')
        await client.connect()
    except OSError:
        print('Connection failed.')
        return
    
    while True:
        await asyncio.sleep(5)

def close():
    client.close()