#!/usr/bin/env python3

import time
import os
import psutil
import logging
import sys
import requests
from gpiozero import PWMOutputDevice

SLEEP_INTERVAL = 20  # (seconds) How often we check the core temperature.
GPIO_PIN = 18  # Which GPIO pin you're using to control the fan.

MIN_FAN_SPEED = 0.6
MAX_FAN_SPEED = 1

OFF_THRESHOLD = 54
FULL_SPEED_THRESHOLD = 67

MAX_TEMP_FOR_RESTART = 75
CPU_PERCENTAGE_THRESHOLD = 20

SPEED_TRACKER_URL = os.environ.get("SPEED_TRACKER_URL")

log_level = logging.INFO
root = logging.getLogger()
root.setLevel(log_level)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(log_level)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

OVERRIDDEN = False


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
    speed = (temp - OFF_THRESHOLD) / (FULL_SPEED_THRESHOLD - OFF_THRESHOLD)
    if speed <= MIN_FAN_SPEED:
        speed = MIN_FAN_SPEED
    else:
        speed = min(MAX_FAN_SPEED, speed)
    return round(speed, 2)


def override_speed(new_speed):
    # fan = get_fan()
    global OVERRIDDEN
    OVERRIDDEN = True
    # fan.value = new_speed
    time.sleep(10)
    OVERRIDDEN = False


def get_current_speed():
    fan = get_fan()
    return fan.value


def set_fan_speed(fan, new_speed):
    if fan.value != new_speed:
        if fan.value == 0:
            restart_fan(fan)
        fan.value = new_speed


def restart_fan(fan):
    if fan.value != 0:
        fan.value = 0
        time.sleep(1)
    fan.value = 1
    time.sleep(1)


def report_fan_speed(speed):
    if SPEED_TRACKER_URL:
        post_data = {'fan_speed': speed}
        try:
            requests.post(SPEED_TRACKER_URL, data=post_data)
        except:
            logging.exception("Failed to report fan speed")


def main():
    fan = get_fan()
    restart_fan(fan)
    while True:
        temp = get_temp()
        if OVERRIDDEN:
            logging.info(f"Temp: {temp}; (fan speed overridden to: {fan.value})")
        else:
            new_speed = get_speed(temp)
            if new_speed != fan.value:
                logging.info(f"Temp: {temp}; New fan speed: {new_speed}")
                set_fan_speed(fan, new_speed)
                report_fan_speed(new_speed)
            else:
                logging.info(f"Temp: {temp}; (fan speed: {new_speed})")
        time.sleep(SLEEP_INTERVAL)


def get_fan():
    fan = PWMOutputDevice(GPIO_PIN)
    return fan


if __name__ == '__main__':
    main()
