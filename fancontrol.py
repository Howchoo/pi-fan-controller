#!/usr/bin/env python3

import time

from gpiozero import OutputDevice

MAX_THRESHOLD = 60.0 # (degrees Celsius) Fan kicks on at full speed at this temperature.
MIN_THRESHOLD = 50.0 # (degress Celsius) Fan kicks on at minimum speed at this temperature.
SLEEP_INTERVAL = 1.0 # (miliseconds) How long one tick last
GPIO_PIN = 17 # Which GPIO pin you're using to control the fan.
MIN_TICKS = 200 # Number of min ticks in cycle
MAX_TICKS = 1000 # Number of max ticks in cycle
FAN_ON = 1
FAN_OFF = 0

def get_temp():
    """Get the core temperature.

    Read file from /sys to get CPU temp in temp in C *1000

    Returns:
        int: The core temperature in thousanths of degrees Celsius.
    """
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        temp_str = f.read()

def normalize_temp(temp):
    temp = ((float(temp) - MIN_THRESHOLD) / (MAX_THRESHOLD - MIN_THRESHOLD))
    if temp < 0.0:
        temp = 0.0
    if temp > 1.0:
        temp = 1.0
    return float(temp)

def count_fire_tick(temp):
    temp = ((MAX_TICKS / MIN_TICKS) - (MAX_TICKS / MIN_TICKS) * float(temp))
    if temp <= 0:
        temp = 1
    return float(temp)

def fan_command(command, fan):
    if command == FAN_ON and not fan.value:
        fan.on()
    if command == FAN_OFF and fan.value:
        fan.off()

def run_cycle(fire_tick, fan):
    i = 0
    while i < MAX_TICKS:
        if (i % int(fire_tick)) == 0:
            fan_command(FAN_ON, fan)
        time.sleep(SLEEP_INTERVAL / 1000.0)
        if (i % int(fire_tick)) != 0:
            fan_command(FAN_OFF, fan)

if __name__ == '__main__':

    fan = OutputDevice(GPIO_PIN)

    while True:
        temp = get_temp()

        temp = normalize_temp(temp)

        temp = count_fire_tick(temp)

        run_cycle(temp, fan)
