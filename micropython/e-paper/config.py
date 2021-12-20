from mqtt_as import config

config['ssid'] = '{{wlan_ssid}}'
config['wifi_pw'] = '{{wlan_passphrase}}'

config['client_id'] = 'esp32'
config['server'] = '{{mqtt_remote_host}}'
config['ssl'] = True
config['user'] = '{{mqtt_remote_username}}'
config['password'] = '{{mqtt_remote_password}}'

# ESP32 is assumed to have user supplied active low LED's on same pins.
# Call with blue_led(True) to light

from machine import Pin
def ledfunc(pin):
    pin = pin
    def func(v):
        pin(not v)  # Active low on ESP8266
    return func
wifi_led = ledfunc(Pin(0, Pin.OUT, value = 0))  # Red LED for WiFi fail/not ready yet
blue_led = ledfunc(Pin(2, Pin.OUT, value = 1))  # Message received
