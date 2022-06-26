import time
from mqtt_as import config

history = {
    'sensors/pannu': [],
}

latest = {
    'sensors/pannu': {'temp': '-'},
    'sensors/pannu/command': '-',
    'sensors/indoor': {'temp': '-'},
    'sensors/indoor/refreshrate': 1,
    'sensors/vintti': {'temp': '-'},
    'sensors/takapiha': {'temp': '-'},
}


def raw(sensor):
    return latest['sensors/{0}'.format(sensor)]


def temp(sensor, decimals):
    return format(raw(sensor)['temp'], decimals)


def format(value, decimals):
    if type(value) == int or type(value) == float:
        if decimals == 1:
            return '{:.1f}°'.format(value)
        if decimals == 2:
            return '{:.2f}°'.format(value)
        return '{0}°'.format(value)
    else:
        return '-'


def timestamp():
    now = time.time()
    year, month, day, hour, minute, second, ms, dayinyear = time.gmtime(now)

    # Rules for Finland: DST ON: March last Sunday at 03:00 + 1h, DST OFF: October last Sunday at 04:00 - 1h
    dstend = time.mktime(
        (year, 10, (31 - (int(5 * year / 4 + 1)) % 7), 4, 0, 0, 0, 6, 0))

    dstbegin = time.mktime(
        (year, 3, (31 - (int(5 * year / 4 + 4)) % 7), 3, 0, 0, 0, 6, 0))

    stdtime = now < dstbegin or now > dstend
    local_hour = hour + config['tz'] + (0 if stdtime else 1)

    return '{:02d}.{:02d}'.format(local_hour % 24, minute)


def temp_history(sensor):
    values = []
    for data in history['sensors/{0}'.format(sensor)]:
        if type(data['temp']) == int or type(data['temp']) == float:
            values.append(data['temp'])
    return values
