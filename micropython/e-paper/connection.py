from mqtt_as import MQTTClient, config
from config import wifi_led, blue_led
import uasyncio as asyncio
import ujson

from state import latest, history

wifi_led(False)
blue_led(False)


def sub_cb(topic, msg, retained):
    sensor = topic.decode()

    print((sensor, msg, retained))

    if type(msg) == int or type(msg) == float:
        data = msg
    else:
        data = ujson.loads(msg)

    if sensor in latest:
        latest[sensor] = data

    if sensor in history:
        history[sensor].append(data)
        if len(history[sensor]) > 15:
            del history[sensor][0]


# ###################################################################### #
# Set RTC localTime from UTC and apply DST offset
# Requires import machine, utime, ntptime
# assumes active network, otherwise will raise error whch is not currently dealt with
# Note: dstOffset should be between -12 and +14
# ###################################################################### #
def sync_time():
    import ntptime
    import time

    print('Time before synchronization：%s' % str(time.gmtime()))

    now = ntptime.time()
    year, month, day, hour, minute, second, ms, dayinyear = time.gmtime(now)

    szTime = "{:4}-{:02}-{:02} {:02}:{:02}:{:02}".format(
        year, month, day, hour, minute, second)
    print("Time : ", szTime)

    ntptime.host = config['ntp']

    # set the RTC to correct time
    ntptime.settime()

    year, month, day, hour, minute, second, ms, dayinyear = time.gmtime()
    szTime = "{:4}-{:02}-{:02} {:02}:{:02}:{:02}".format(
        year, month, day, hour, minute, second)
    print("setTime : ", szTime)

    print('Time after synchronization：%s' % str(time.gmtime()))


async def wifi_han(state):
    wifi_led(not state)
    if state:
        print('WiFi is up.')

        import network
        wlan = network.WLAN(network.STA_IF)
        print(wlan.ifconfig())

        import webrepl
        webrepl.start()

        sync_time()
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


async def publish(topic, msg):
    await client.publish(topic,  ujson.dumps(msg), qos=1)


def close():
    client.close()
