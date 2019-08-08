#!/usr/bin/env python3

import subprocess
import time

from gpiozero import OutputDevice


LIMIT = 65  # degrees
SLEEP_INTERVAL = 5  # seconds


def get_temp():
    output = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True)
    temp_str = output.stdout.decode()
    try:
        return float(temp_str.split('=')[1].split('\'')[0])
    except (IndexError, ValueError):
        raise RuntimeError('Could not parse temperature output.')


if __name__ == '__main__':
    fan = OutputDevice(17)

    while True:
        temp = get_temp()


        # Start the fan if the temperature has reached the limit and the fan
        # isn't already running.
        # NOTE: `fan.value` returns 1 for "on" and 0 for "off"
        if temp > LIMIT and not fan.value:
            fan.on()

        # Stop the fan if the fan is running and the temperature has dropped
        # to 10 degrees below the limit.
        elif fan.value and temp < (LIMIT - 10):
            fan.off()

        time.sleep(SLEEP_INTERVAL)
