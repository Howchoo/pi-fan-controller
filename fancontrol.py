#!/usr/bin/env python3

import time
import logging

from gpiozero import PWMOutputDevice

"""
ON_TEMP should be higher than the Raspi idle temperature (usually
between 50-70 degC, depending on the base load), otherwise the fan will
continuously switch ON and OFF.
OFF_TEMP should be reachable with the minimum fan speed in the idle state,
otherwise the fan will be continuously ON after triggered once (usually
around 50 degC).
"""

FULL_ON_TEMP = 80.  # [degC] temp for max PWM
ON_TEMP = 68.  # [degC] temp to switch on
OFF_TEMP = 50.  # [degC] temp for min PWM
INTERVAL = 5.  # [s] refresh interval
GPIO_PIN = 17  # Pin to connect transistor base
MAX_PWM = 1.  # PWM at max on temp
MIN_PWM = .64  # PWM at lowest on temp
MIN_STARTUP_PWM = .9  # PWM to use on startup
PWM_FREQUENCY = 500  # [Hz] - with 100uF, and .7 min PWM
FAN_MODES = ["linear", "exponential"]
FAN_MODE = "exponential"


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

def turn_on_or_off(pwm_device: PWMOutputDevice, temp: int) -> None:
    if pwm_device.is_active and temp < OFF_TEMP:
        pwm_device.off()
        print("Turned off")
    elif not pwm_device.is_active and temp >= ON_TEMP:
        pwm_device.on()
        pwm_device.value = MIN_STARTUP_PWM
        print("Turned on")

def calc_pwm(pwm_range: float, temp_range: float, temp: float) -> float:
    if FAN_MODE == "linear":
        return pwm_range * (temp - OFF_TEMP) / temp_range + MIN_PWM
    elif FAN_MODE == "exponential":
        return (1.001 ** (3.7 * (temp - OFF_TEMP) / temp_range) ** 5 - 1) * pwm_range + MIN_PWM

def fancontrol_loop():
    fan = PWMOutputDevice(GPIO_PIN, frequency=PWM_FREQUENCY)

    pwm_range = MAX_PWM - MIN_PWM
    temp_range = FULL_ON_TEMP - OFF_TEMP

    while True:
        temp = get_temp()
        if fan.is_active:
            pwm = calc_pwm(pwm_range, temp_range, temp)
            fan.value = max(min(pwm, MAX_PWM), MIN_PWM)
        turn_on_or_off(fan, temp)

        print(f"Current temp|PWM: {temp:.2f}|{fan.value:.2f}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    assert ON_TEMP > OFF_TEMP, "ON_TEMP must be higher than OFF_TEMP"
    assert ON_TEMP < FULL_ON_TEMP, "ON_TEMP must be lower than FULL_ON_TEMP"
    assert MIN_STARTUP_PWM >= MIN_PWM, "MIN_STARTUP_PWM must be at least MIN_PWM"
    assert MAX_PWM > MIN_PWM, "MAX_PWM must be higher than MIN_PWM"
    assert FAN_MODE in FAN_MODES, f"FAN_MODE must be one of {str(FAN_MODES)}"

    fancontrol_loop()
