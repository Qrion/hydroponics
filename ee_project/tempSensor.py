##### How do I calibrate to the temp is correct?
####

from board import ADC0
from machine import Pin, ADC

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

