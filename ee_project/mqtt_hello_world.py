from mqttclient import MQTTClient
import network
import sys
import time
from board import ADC0, A5
from machine import Pin, ADC

"""Publish and subscribe hello statements to test MQTT on ESP32Go to https://hobbyquaker.github.io/mqtt-admin/ to interact with your microcontroller via MQTTGo to https://iot.eclipse.org/getting-started/ for socket parameters. Topic must match between microcontroller and web client."""

# Important: change the line below to a unique string,
# e.g. your name/esp34/helloworld
session = "fredrik/esp32/helloworld"
BROKER = "iot.eclipse.org"


# check wifi connection
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Troppo", "hej12345")
wlan.isconnected()
ip = wlan.ifconfig()[0]
if ip == '0.0.0.0':
    print("no wifi connection")
    sys.exit()
else:
    print("connected to WiFi at IP", ip)
    
# connect to MQTT broker
print("Connecting to MQTT broker", BROKER, "...", end="")
mqtt = MQTTClient(BROKER)
print("Connected!")

# Define function to execute when a message is recieved on a subscribed topic.

def mqtt_callback(topic, msg):
    print("RECEIVE topic = {}, msg = {}".format(topic.decode('utf-8'),msg.decode('utf-8')))
    
# Set callback function
mqtt.set_callback(mqtt_callback)

# Set a topic you will subscribe too. Publish to this topic via web client and watch microcontroller recieve messages.
mqtt.subscribe(session + "/host/hello")


"""
 Testing solenoid
"""
a5 = Pin(A5, mode=Pin.OUT)
a5(1)


while True:
    
    """
        Temp Sensor
    """
    adc0 = ADC(Pin(ADC0))

    # set full-scale range
    adc0.atten(ADC.ATTN_11DB)

    # perform conversion
    thermistor_value = adc0.read()

    # convert to temperature
    r = 10000 / (65535/thermistor_value - 1)

    def steinhart_temperature_C(r, Ro=10000.0, To=25.0, beta=3950.0):
        import math
        steinhart = math.log(r / Ro) / beta # log(R/Ro) / beta
        steinhart += 1.0 / (To + 273.15) # log(R/Ro) / beta + 1/To
        steinhart = (1.0 / steinhart) - 273.15 # Invert, convert to C
        return steinhart

    tempData = steinhart_temperature_C(r)
    
    """
        Send Data
    """
    
    # Microcontroller sends hellos statements.
    topic = "{}/mcu/hello".format(session)
    data = str(tempData)
    print("send topic='{}' data='{}'".format(topic, data))
    mqtt.publish(topic, data)
    time.sleep(0.5)
    # Check for any messages in subscribed topics.
    for _ in range(10):
        mqtt.check_msg()
        time.sleep(0.5)
        
# free up resources
# alternatively reset the microphyton board before executing this program again
mqtt.disconnect()