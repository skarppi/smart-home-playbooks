from simple_pid import PID
from datetime import datetime, timezone
import time
from paho.mqtt import client as mqtt
import json 

from simple_pid import PID


class WaterBoiler:
    """
    Simple simulation of a water boiler which can heat up water
    and where the heat dissipates slowly over time
    """

    def __init__(self):
        self.water_temp = 10

    def update(self, boiler_power, dt):
        if boiler_power > 0:
            # print(self.water_temp, " + ", boiler_power, dt)
            # Boiler can only produce heat, not cold
            self.water_temp += 3 * boiler_power * dt

        # Some heat dissipation
        self.water_temp -= 90 * dt
        return self.water_temp

client = mqtt.Client("pid")

pid = PID(0.2, 0.15, 0, sample_time = 1800, proportional_on_measurement = False)
pid.setpoint=0
pid.output_limits = (25, 45)
pid.set_auto_mode(False)

run = True
PID_TOPIC = "sensors/pannu/pid"
SETPOINT_TOPIC = "sensors/indoor/command"
INPUT_TOPIC = "sensors/indoor"

# use wall clock instead of relative process time
def fix_pid_time(now):
    pid._last_time = now

start_time = time.time()
fix_pid_time(start_time)

def pid_restart(last_output):
    pid.set_auto_mode(False)
    pid.set_auto_mode(True, last_output=last_output)
    fix_pid_time(time.time())
    print("start pid from power ", last_output)


def pid_save_internal_state():
    return {
        'id': 'pid',
        'timestamp': datetime.now(timezone.utc).isoformat(timespec='microseconds'),
        'Kp': pid.Kp,
        'Ki': pid.Ki,
        'Kd': pid.Kd,
        'p': pid._proportional, 
        'i': pid._integral,
        'd': pid._derivative,
        'time': pid._last_time,
        'output': pid._last_output, 
        'input': pid._last_input,
        'target': pid.setpoint
    }

# import state of the pid from the last run
def pid_restore_internal_state(data):
    age = time.time() - data['time'] if 'time' in data else 0
    print("previous ", age , " seconds ", data)

    pid.setpoint = data['target'] if 'target' in data else 25

    # previous
    last_output = pid._last_output

    pid._proportional = data['p'] if 'p' in data else 0
    pid._integral = data['i'] if 'i' in data else 0
    pid._derivative = data['d'] if 'd' in data else 0
    pid._last_output =  data['output'] if 'output' in data else None
    pid._last_time = data['time'] if 'time' in data else time.time()
    pid._last_input = data['input'] if 'input' in data else None

    # if manually changed since last time
    if last_output != data['output'] if 'output' in data else None:
        pid_restart(data['output'])

def pid_loop(latest_input, dt_divider = 1):

    now = time.time()
    dt = now - pid._last_time if (now - pid._last_time) else 1e-16

    # print(now)
    # print(pid._last_time)

    last_output = pid._last_output

    output = pid(latest_input, dt / dt_divider)
    fix_pid_time(now)

    if last_output != output:
        data = pid_save_internal_state()
        print("publish ", output, dt, data)
        ret = client.publish(PID_TOPIC, json.dumps(data), qos=1, retain=True)
        # ret.wait_for_publish()

    return output, now, dt

def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))
    pass


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)

def on_message(client, userdata, message):

    # print("Received message '" + str(message.payload) + "' on topic '"
    #   + message.topic + "' with QoS " + str(message.qos))

    if message.topic == PID_TOPIC:
        data = json.loads(message.payload)
        pid_restore_internal_state(data)

    elif message.topic == SETPOINT_TOPIC:
        pid.setpoint = int(message.payload)

        print("setpoint ", pid.setpoint)

    elif message.topic == INPUT_TOPIC:
        data = json.loads(message.payload)

        print("input ", data)

        # 1 hour in real life equals 0.1 second sample time
        pid_loop(data['temp'], 600)

def connect():
    #client.tls_set()
    #client.username_pw_set("USERNAME", "PWD")
    client.on_message = on_message
    # client.on_connect = on_connect
    # client.on_publish = on_publish
    # client.on_subscribe = on_subscribe
    client.on_log = on_log
    #client.connect("server", 8883)
    client.connect("localhost", 1883)
    client.subscribe([
        (PID_TOPIC, 1),
        (SETPOINT_TOPIC, 1),
        (INPUT_TOPIC, 1)
    ])    
    client.loop_start()

def disconnect():
    client.disconnect()

connect()
# pid_loop(20)

while run:
    time.sleep(1)

disconnect()

def test():
    import matplotlib.pyplot as plt

    global start_time
    # # Keep track of values for plotting
    setpoint, y, x, output = [], [], [], []

    boiler = WaterBoiler()
    water_temp = boiler.water_temp

    data = None

    pid.setpoint = 20
    pid_restart(25)

    while time.time() - start_time < 10:
        if data is not None:
            pid_restore_internal_state(data)

        power, current_time, dt = pid_loop(water_temp)

        # print(power, current_time, dt * 100)

        water_temp = boiler.update(power, dt  * 10)

        x += [(current_time - start_time) * 10]
        y += [water_temp]
        setpoint += [pid.setpoint]
        output += [power]

        # if current_time - start_time > 2:
        #     pid.setpoint = 60

        # if current_time - start_time > 6:
        #     pid.setpoint = 40

        data = pid_save_internal_state()

        time.sleep(0.01)

    plt.plot(x, y, label='measured')
    plt.plot(x, setpoint, label='target')
    plt.plot(x, output, label='power')
    plt.xlabel('time')
    plt.ylabel('temperature')
    plt.legend()
    plt.show()

# test()