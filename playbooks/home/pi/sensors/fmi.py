#!/usr/bin/python3

import json
import sys
from paho.mqtt import client as mqtt
import urllib.request
from datetime import datetime, timezone
from xml.etree import ElementTree

geoid = sys.argv[1]
if not geoid:
	print("No geoid")
	exit()

url = f"https://opendata.fmi.fi/wfs?request=getFeature&storedquery_id=fmi::observations::weather::multipointcoverage&geoid={geoid:s}&parameters=temperature"
response = urllib.request.urlopen(url).read()

root = ElementTree.fromstring(response)

ns = {
	'gml': 'http://www.opengis.net/gml/3.2', 
	'gmlcov': 'http://www.opengis.net/gmlcov/1.0'}

def getLastPoint(root, tag):
	tempsStr = root.findall(tag, ns)[0].text
	temps = tempsStr.strip().split('\n')
	return temps[len(temps)-1].strip()


temp = getLastPoint(root, './/gml:doubleOrNilReasonTupleList')
timestamp = getLastPoint(root, './/gmlcov:positions').split(' ')[3]

msg = {
	'timestamp': datetime.fromtimestamp(int(timestamp), timezone.utc).isoformat(timespec='microseconds'),
	'temp': round(float(temp), 2)
}

print(msg)

client = mqtt.Client("bme280")
client.connect("localhost", 1883)
client.loop_start()
ret = client.publish("sensors/outdoor", json.dumps(msg), qos=1)
print(ret)
ret.wait_for_publish()

client.disconnect()
