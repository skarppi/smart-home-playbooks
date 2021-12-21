import time

latest = {
    'sensors/pannu': { 'temp': '-' }, 
    'sensors/indoor': { 'temp': '-' }, 
    'sensors/vintti': { 'temp': '-' }, 
    'sensors/takapiha': { 'temp': '-' }, 
}

def temp(sensor, decimals):
    temp = latest['sensors/{0}'.format(sensor)]['temp']
    if type(temp) == int or type(temp) == float:
        if decimals == 1:
            return '{:.1f}°'.format(temp)
        if decimals == 2:
            return '{:.2f}°'.format(temp)
        if decimals == 3:
            return '{:.3f}°'.format(temp)
        return '{0}°'.format(temp)
    else:
        return '-'

def timestamp():
    now =  time.localtime()
    return '{:02d}:{:02d}'.format(now[3], now[4])
