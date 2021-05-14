#!/usr/bin/env python3

import time

from gpiozero import PWMOutputDevice

SLEEP_INTERVAL = 5  # (seconds) How often we check the core temperature.
GPIO_PIN = 18  # Which GPIO pin you're using to control the fan.
OFF_THRESHOLD = 55
FULL_SPEED_THRESHOLD = 65


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


def get_speed(temp):
    speed = temp / (FULL_SPEED_THRESHOLD - OFF_THRESHOLD)
    return speed


def main():
    fan = OutputDevice(GPIO_PIN)

    while True:
        temp = get_temp()

        new_speed = get_speed(temp)

        print(f"Temp: {temp}; new fan speed:{new_speed}")
        fan.value = new_speed

        time.sleep(SLEEP_INTERVAL)


if __name__ == '__main__':
    main()
