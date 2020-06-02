#!/usr/bin/env python3

import subprocess
import time

from gpiozero import PWMOutputDevice

SLEEP_INTERVAL = 3  # (seconds) How often we check the core temperature.
GPIO_PIN = 18  # Which GPIO pin you're using to control the fan.
OUTPUTS = [0.5, 0.6, 0.7, 0.8, 0.9, 1]
TEMPS = [40.0, 45.0, 50.0, 55.0, 60.0, 65.0]


def get_temp():
    """Get the core temperature.
    Run a shell script to get the core temp and parse the output.
    Raises:
        RuntimeError: if response cannot be parsed.
    Returns:
        float: The core temperature in degrees Celsius.
    """
    output = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True)
    temp_str = output.stdout.decode()
    try:
        return float(temp_str.split('=')[1].split('\'')[0])
    except (IndexError, ValueError):
        raise RuntimeError('Could not parse temperature output.')



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

    fan = PWMOutputDevice(GPIO_PIN)

    while True:
        fan.value = get_speed()

        time.sleep(SLEEP_INTERVAL)
