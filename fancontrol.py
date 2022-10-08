#!/usr/bin/env python3

import time

from gpiozero import PWMOutputDevice

SLEEP_INTERVAL = 3  # (seconds) How often we check the core temperature.
ON_THRESHOLD = 65  # (degrees Celsius) Fan kicks on at this temperature.
OFF_THRESHOLD = 55  # (degress Celsius) Fan shuts off at this temperature.
OUTPUTS = [0.5, 0.6, 0.7, 0.8, 0.9, 1]
TEMPS = [40.0, 45.0, 50.0, 55.0, 60.0, 65.0]
USE_PWM = True
GPIO_PIN = 18 if USE_PWM else 17 # Which GPIO pin you're using to control the fan.



def get_temp():
    """Get the core temperature.

    Read file from /sys to get CPU temp in temp in C *1000

    Returns:
        int: The core temperature in thousanths of degrees Celsius.
    """
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        temp_str = f.read()

    try:
        return int(temp_str) / 1000
    except (IndexError, ValueError,) as e:
        raise RuntimeError('Could not parse temperature output.') from e

def get_speed():
    """
    Gets the temp of the board and assigns percentage of max max speed correspondingly
    Returns: A value between 0-1. Can be configured by adjusting OUTPUTS and TEMPS.
    """
    speed = 0.0
    for i in range(len(TEMPS)):  # loop through list of temps
        if get_temp() > TEMPS[i]:
            speed = OUTPUTS[i]  # set speed to the corresponding temp
    return speed


if __name__ == '__main__':

    # Validate the on and off thresholds
    if not USE_PWM and OFF_THRESHOLD >= ON_THRESHOLD:
        raise RuntimeError('OFF_THRESHOLD must be less than ON_THRESHOLD')

    fan = PWMOutputDevice(GPIO_PIN)

    if USE_PWM:
        while True:
            fan.value = get_speed()

            time.sleep(SLEEP_INTERVAL)
    else:
        temp = get_temp()

        # Start the fan if the temperature has reached the limit and the fan
        # isn't already running.
        # NOTE: `fan.value` returns 1 for "on" and 0 for "off"
        if temp > ON_THRESHOLD and not fan.value:
            fan.on()

        # Stop the fan if the fan is running and the temperature has dropped
        # to 10 degrees below the limit.
        elif fan.value and temp < OFF_THRESHOLD:
            fan.off()