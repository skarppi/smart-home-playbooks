import time

history = {
    'sensors/pannu': [], 
}

latest = {
    'sensors/pannu': { 'temp': '-' }, 
    'sensors/indoor': { 'temp': '-' }, 
    'sensors/vintti': { 'temp': '-' }, 
    'sensors/takapiha': { 'temp': '-' }, 
}

def temp(sensor, decimals):
    temp = latest['sensors/{0}'.format(sensor)]['temp']
    return format(temp, decimals)

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
    now =  time.localtime()
    return '{:02d}:{:02d}'.format(now[3], now[4])

def temp_history(sensor):
    values = []
    for data in history['sensors/{0}'.format(sensor)]:
        if type(data['temp']) == int or type(data['temp']) == float:
            values.append(data['temp'])
    return values