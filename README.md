# Pi Fan Controller

Raspberry Pi fan controller.

## Description

This repository provides scripts that can be run on the Raspberry Pi that will
monitor the core temperature and start the fan when the temperature reaches
a certain threshold.

To use this code, you'll have to install a fan. The full instructions can be
found on our guide: [Control Your Raspberry Pi Fan (and Temperature) with Python](https://howchoo.com/g/ote2mjkzzta/control-raspberry-pi-fan-temperature-python).

In addition to the guide above, in order to use soft PWM, you will need to add a capacitor to avoid audible noise induced by the fan at PWM frequency.
Values for the capacitor are highly dependent on PWM frequency; the higher the frequency, the less capacitance is needed.

In addition, the values for minimum PWM for the fan will be influenced by PWM frequency as well.

The default configuration uses a 100µF electrolytic capacitor between the two fan leads, and a 500Hz PWM frequency.

In order to test out the minimum speed of a different fan manually, you can use the module interactively:

```sh
$ python
```
```python
from fancontrol import *

fan = PWMOutputDevice(GPIO_PIN, frequency=PWM_FREQUENCY)
```
Now `fan.value` can be set to values between `0.0` and `1.0` in order to find the minimum value that still allows the fan to spin reliably.

Start with a high fan speed (such as `0.9`), and slowly decrease the speed until the fan stops. This value (in addition to a security margin) will be the `MIN_PWM` value for your specific PWM frequency, capacitance and fan type.
