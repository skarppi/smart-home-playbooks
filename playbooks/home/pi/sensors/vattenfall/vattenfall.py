#!/usr/bin/python3

import json
from paho.mqtt import client as mqtt
from urllib import request, parse, error
from datetime import datetime, timezone, timedelta
from dateutil import tz
from http import cookiejar
import re
import os
import ssl
import certifi

ssl._create_default_https_context = ssl._create_stdlib_context

loginData = {
        "UserName": "{{vattenfall_username}}",
        "Password": "{{vattenfall_password}}",
        "Configuration": "CABPHUB"
    }

dirname = os.path.dirname(__file__)
cookieFilePath = f"{dirname}/cookies.txt"
tokenFilePath = f"{dirname}/token.txt"
latestFilePath = f"{dirname}/latest.txt"

jar = cookiejar.MozillaCookieJar(cookieFilePath)
handler = request.HTTPCookieProcessor(jar)
opener = request.build_opener(handler)

client = mqtt.Client("Vattenfall")
client.username_pw_set("{{mqtt_remote_username}}", "{{mqtt_remote_password}}")
client.tls_set()
client.connect("{{mqtt_remote_host}}", {{mqtt_remote_port}})
client.loop_start()

def fetchToken(url):
    try:
        print("Calling " + url)
        with opener.open(url) as res:
            print(res.url)
            print(res.status)
            print(res.headers)

            body = res.read().decode('utf-8')
            tokenPattern = re.compile(r'.*<input name="__RequestVerificationToken" type="hidden" value="([^\\"]+)".*', re.DOTALL)

            token = tokenPattern.match(body).group(1)
            if not token:
                print("No verification token")
                return False
            return token
    except error.URLError as e:
        print(e.reason)
        print(e)
        return False

def login():
    loginToken = fetchToken("https://omaenergia.vattenfall.fi/EnergyReporting/EnergyReporting")

    try:
        loginReq = request.Request(
                    "https://omaenergia.vattenfall.fi/Authentication/Login",
                    parse.urlencode(loginData).encode('ascii'),
                    { "__requestverificationtoken": loginToken }
                    )

        with opener.open(loginReq) as loginRes:
            loginJson = json.loads(loginRes.read().decode('utf-8'))
            if not loginJson["ReturnStatus"]:
                print("login failed " + loginJson)
                return False

            print(loginJson)
            reportingToken = fetchToken("https://omaenergia.vattenfall.fi" + loginJson["Redirect"])
            print("started with token " + reportingToken)

            return reportingToken

    except error.URLError as e:
        print(e.reason)
        print(e)
        return False

def readDeliverySites(token):
    deliverySites = readJson(
        "https://omaenergia.vattenfall.fi/EnergyReporting/GetDeliverysites",
        {
            "showHistorical": "false",
            "fetchSharedContractDeliverysites": "false"
        }, { "__RequestVerificationToken": token })
    if not deliverySites or not deliverySites["Status"]:
        print("No delivery sites available")
        print(deliverySites)
        raise OSError("Session expired or something") 

    deliverySiteCode = re.match(r'.*data-deliverysite="(\d+)".*', deliverySites["Content"], re.DOTALL).group(1)
    deliverySiteCustomer = re.match(r'.*data-customer="(\d+)".*', deliverySites["Content"], re.DOTALL).group(1)

    deliverySite = readJson(
        "https://omaenergia.vattenfall.fi/EnergyReporting/ShowDeliverysite",
        {
            "code": deliverySiteCode,
            "customerCode": deliverySiteCustomer
        }, { "__RequestVerificationToken": token })
    # print(deliverySite)

def readConsumption(token, latest):
    payload = readJson(
        "https://omaenergia.vattenfall.fi/EnergyReporting/ShowReportingView",
        {
            'view': 'DayP',
            'dateStart': latest.date().isoformat(),
            'dateEnd': latest.date().isoformat(),
            "resolution": "",
            "direction": "",
            "options": ""
        }, { "__RequestVerificationToken": token })
    if payload:
        config = json.loads(payload["config"])

        for entry in config["dataProvider"]:
            timestamp = datetime.fromisoformat(entry["date"])
            
            if timestamp > latest:
                if entry["PS_STATUS"] == "Mitattu":
                    publish({
                        'id': "vattenfall", 
                        'timestamp': timestamp.astimezone(timezone.utc).isoformat(timespec='microseconds'),
                        'consumption': entry["PS"]
                    })
                    latest = timestamp
                else:
                    return latest

    return latest

def readJson(url, data, headers):
    req = request.Request(
        url,
        parse.urlencode(data).encode('ascii'),
        headers)
    print(req.full_url)
    print(req.data)

    try:
        with opener.open(req) as res:
            body = res.read()

            print(res.url)
            print(res.status)
            # print(res.headers)

            if "json" not in res.info().get('Content-Type'):
                print("Not returning JSON")
                return None

            return json.loads(body)

    except error.URLError as e:
        print(e.reason)
        print(e)
        return None

def publish(msg):
    print(msg)
    ret = client.publish("sensors/vattenfall", json.dumps(msg), qos=1)
    ret.wait_for_publish()

def getValidToken():

    try:
        with open(tokenFilePath, "r") as reader:
            token = reader.read()

        jar.load(cookieFilePath, True, True)

        readDeliverySites(token)

        print("Already logged in")
        return token
    except OSError as e:
        print("Login expired")

        jar.clear()

        token = login()
        if token:
            with open(tokenFilePath, "w") as writer:
                writer.write(token)
            
            jar.save(cookieFilePath, True, True)

            readDeliverySites(token)

            return token
        else:
            return False

def readLatestDate():
    with open(latestFilePath, "r") as reader:
        latest = reader.read()
        if latest:
            return datetime.fromisoformat(latest)

    return datetime.fromisoformat('2021-01-23T00:00:00+02:00')

def writeLatestDate(date):
    with open(latestFilePath, "w") as writer:
        writer.write(date.isoformat())

token = getValidToken()
if token:
    current = readLatestDate()

    while (True):
        print("query " + current.isoformat())

        last = readConsumption(token, current)
        print("last = " + last.isoformat())

        writeLatestDate(last)

        if last.hour == 23:
            current = last + timedelta(hours=1)

            print("next day " + current.isoformat())
        else:
            print("Done")
            exit()