#!/usr/bin/env python3

import time
from gpiozero import PWMOutputDevice

SLEEP_INTERVAL = 5  # (seconds) How often we check the core temperature.
GPIO_PIN = 18  # Which GPIO pin you're using to control the fan.
MIN_FAN_SPEED = 0.4
MAX_FAN_SPEED = 1
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
    speed = ((temp * OFF_THRESHOLD) / FULL_SPEED_THRESHOLD) / 100
    speed = min(MAX_FAN_SPEED, speed)
    speed = max(MIN_FAN_SPEED, speed)
    return speed


def set_fan_speed(fan_device, new_speed):
    fan_device.value = 0
    time.sleep(1)
    fan_device.value = 1
    time.sleep(1)
    fan_device.value = new_speed


def main():
    fan = PWMOutputDevice(GPIO_PIN)
    while True:
        temp = get_temp()
        new_speed = get_speed(temp)
        print(f"Temp: {temp}; new fan speed:{new_speed}")
        set_fan_speed(fan, new_speed)
        time.sleep(SLEEP_INTERVAL)


if __name__ == '__main__':
    main()
