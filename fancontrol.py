#!/usr/bin/env python3

import time
import logging

from gpiozero import PWMOutputDevice


FULL_ON_TEMP = 65.  # [degC] temp for max PWM
OFF_TEMP = 55.  # [degC] temp for min PWM
INTERVAL = 5.  # [s] refresh interval
GPIO_PIN = 17  # Pin to connect transistor base
MAX_PWM = 1.  # PWM at max on temp
MIN_PWM = .7  # PWM at lowest on temp
MIN_STARTUP_PWM = .9  # PWM to use on startup
PWM_FREQUENCY = 500  # [Hz] - with 100uF, and .7 min PWM


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


def turn_on_or_off(pwm_device: PWMOutputDevice, temp: int):
    if fan.is_active and temp < OFF_TEMP:
        fan.off()
        print("Turned off")
    elif not fan.is_active and temp >= OFF_TEMP:
        fan.on()
        fan.value = MIN_STARTUP_PWM
        print("Turned on")


if __name__ == "__main__":
    assert OFF_TEMP < FULL_ON_TEMP, "OFF_TEMP must be lower than FULL_ON_TEMP"
    assert MIN_STARTUP_PWM >= MIN_PWM, "MIN_STARTUP_PWM must be at least MIN_PWM"
    assert MAX_PWM > MIN_PWM, "MAX_PWM must be higher than MIN_PWM"

    fan = PWMOutputDevice(GPIO_PIN, frequency=PWM_FREQUENCY)
    turn_on_or_off(fan, get_temp())

    pwm_range = MAX_PWM - MIN_PWM
    temp_range = FULL_ON_TEMP - OFF_TEMP

    while True:
        temp = get_temp()
        pwm = pwm_range * (temp - OFF_TEMP) / temp_range + MIN_PWM
        if fan.is_active:
            fan.value = max(min(pwm, MAX_PWM), MIN_PWM)
        turn_on_or_off(fan, temp)

        print(f"Current temp|PWM: {temp:.2f}|{fan.value:.2f}")
        time.sleep(INTERVAL)
