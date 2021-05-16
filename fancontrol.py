#!/usr/bin/env python3

import time
import psutil
from gpiozero import PWMOutputDevice

SLEEP_INTERVAL = 20  # (seconds) How often we check the core temperature.
GPIO_PIN = 18  # Which GPIO pin you're using to control the fan.
MIN_FAN_SPEED = 0.4
MAX_FAN_SPEED = 1
OFF_THRESHOLD = 54
FULL_SPEED_THRESHOLD = 62
MAX_TEMP_FOR_RESTART = 75
CPU_PERCENTAGE_THRESHOLD = 15


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


def get_speed(temp, cpu_usage):
    speed = (temp - OFF_THRESHOLD) / (FULL_SPEED_THRESHOLD - OFF_THRESHOLD)
    if temp < 70 and cpu_usage <= CPU_PERCENTAGE_THRESHOLD or speed <= 0:
        speed = 0
    elif speed <= MIN_FAN_SPEED:
        speed = MIN_FAN_SPEED
    else:
        speed = min(MAX_FAN_SPEED, speed)
    return round(speed, 2)


def set_fan_speed(fan_device, new_speed):
    if fan_device.value == 0:
        fan_device.value = 1
        time.sleep(1)
    fan_device.value = new_speed


def main():
    fan = PWMOutputDevice(GPIO_PIN)
    set_fan_speed(fan, 1)
    while True:
        temp = get_temp()
        new_speed = get_speed(temp, psutil.cpu_percent())
        print(f"Temp: {temp}; new fan speed:{new_speed}")
        set_fan_speed(fan, new_speed)
        time.sleep(SLEEP_INTERVAL)


if __name__ == '__main__':
    main()
