
latest = {
    'sensors/pannu': { 'temp': '-' }, 
    'sensors/indoor': { 'temp': '-' }, 
    'sensors/vintti': { 'temp': '-' }, 
    'sensors/takapiha': { 'temp': '-' }, 
}

def temp(sensor, decimals):
    temp = latest['sensors/{0}'.format(sensor)]['temp']
    if type(temp) == int or float:
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
    return latest['harjula/sensors/pannu']['timestamp'].substring(11, 10)