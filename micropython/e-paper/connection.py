from mqtt_as import MQTTClient, config
from config import wifi_led, blue_led
import uasyncio as asyncio
import ujson

from state import latest, history

wifi_led(False)
blue_led(False)

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

    json = ujson.loads(msg)

    if sensor in latest:
        latest[sensor] = json

    if sensor in history:
        history[sensor].append(json)
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

    print('Local time before synchronization：%s' % str(time.localtime()))

    now=ntptime.time()
    year, month, day, hour, minute, second, ms, dayinyear = time.localtime(now)

    szTime = "{:4}-{:02}-{:02} {:02}:{:02}:{:02}".format( year, month, day, hour, minute, second )
    print( "Time : " , szTime )

    ntptime.host = config['ntp']
    offset = config['tz']

    # Rules for Finland: DST ON: March last Sunday at 03:00 + 1h, DST OFF: October last Sunday at 04:00 - 1h
    dstend = time.mktime((year, 10, (31 - (int(5 * year / 4 + 1)) % 7), 4, 0, 0, 0, 6, 0))
    print(dstend)

    dstbegin = time.mktime((year, 3, (31 - (int(5 * year / 4 + 4)) % 7), 3, 0, 0, 0, 6, 0))
    print(dstbegin)

    if now < dstbegin or now > dstend:
        print( "Standard Time")
        ntptime.NTP_DELTA = 3155673600-( offset * 3600) 
    else:
        print( "Daylight Time")
        ntptime.NTP_DELTA = 3155673600-( (offset+1) * 3600)

    # set the RTC to correct time 
    ntptime.settime()
    year, month, day, hour, minute, second, ms, dayinyear = time.localtime()
    szTime = "{:4}-{:02}-{:02} {:02}:{:02}:{:02}".format( year, month, day, hour, minute, second )
    print( "setTime : " , szTime )

    print('Local time after synchronization：%s' % str(time.localtime()))

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

def close():
    client.close()