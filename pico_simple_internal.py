# pico_simple.py Minimal publish/subscribe test program for Pyboard MQTT bridge

# Author: Peter Hinch.
# Copyright Peter Hinch 2017-2021 Released under the MIT license.

# Host is assumed to have no LED's. Output is via console.
# From PC issue (for example)
# Turn the Pyboard green LED on (or off):
# mosquitto_pub -h 192.168.0.10 -t green -m on
# Print publications from the Pyboard:
# mosquitto_sub -h 192.168.0.10 -t result

import uasyncio as asyncio
from pbmqtt import MQTTlink
import hw_pico as hardware  # Pin definitions. Heartbeat on Pico LED.
import net_local  # WiFi credentials

qos = 1  # for test all messages have the same qos.



def get_internal_temp():
    sensor_temp = machine.ADC(4)
    conversion_factor = 3.3 / (65535)
    while True:
        reading = sensor_temp.read_u16() * conversion_factor
        temperature = 27 - (reading - 0.706)/0.001721
        temperaturef = temperature * 9/5 + 32
        print(temperaturef)
        # utime.sleep(2)
        return temperaturef


    
async def publish(mqtt_link, tim):
    count = 1
    while True:
                 
        await mqtt_link.publish('result', str(count), False, qos)
        count += 1
        print('Sending {0}'.format(count))
        await mqtt_link.publish('InternalTemperature',str(get_internal_temp()),False,qos)
        await asyncio.sleep(tim)
        


def cbgreen(topic, msg, retained):
    print('Green', msg)

def cbnet(state, _):  # Show WiFi state. Discard mqtt_link arg.
    print('cbnet: network is ', 'up' if state else 'down')

async def main(mqtt_link):
    asyncio.create_task(mqtt_link.subscribe('green', qos, cbgreen))  # "LED" control qos 1
    asyncio.create_task(publish(mqtt_link, 10))
    while True:
        await asyncio.sleep(10)


MQTTlink.will('result', 'simple client died')
mqtt_link = MQTTlink(hardware.d, net_local.d, wifi_handler=(cbnet,()), verbose=True) #, debug=True

try:
    asyncio.run(main(mqtt_link))
finally:
    asyncio.new_event_loop()
