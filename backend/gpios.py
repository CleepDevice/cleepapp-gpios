#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Thread
import logging
import time
import uptime

# pylint: disable=no-name-in-module
from RPi.GPIO import (
    LOW as GPIO_LOW,
    HIGH as GPIO_HIGH,
    BOARD as GPIO_BOARD,
    OUT as GPIO_OUT,
    IN as GPIO_IN,
    PUD_DOWN as GPIO_PUD_DOWN,
    PUD_UP as GPIO_PUD_UP,
    RPI_INFO as GPIO_RPI_INFO,
)

# pylint: disable=no-name-in-module
from RPi.GPIO import (
    cleanup as GPIO_cleanup,
    setup as GPIO_setup,
    input as GPIO_input,
    output as GPIO_output,
    setmode as GPIO_setmode,
    setwarnings as GPIO_setwarnings,
)
from cleep.exception import (
    InvalidParameter,
    Unauthorized,
    MissingParameter,
    CommandError,
)
from cleep.core import CleepModule

__all__ = ["Gpios"]


class GpioInputWatcher(Thread):
    """
    Class that watches for changes on specified input pin
    We don't use GPIO lib implemented threaded callback due to a bug when executing a timer within callback function.

    Note:
        This object doesn't configure pin!
    """

    DEBOUNCE = 0.20

    def __init__(self, pin, device_uuid, on_callback, off_callback, level=GPIO_LOW):
        """
        Constructor

        Args:
            pin (int): gpio pin number
            device_uuid (str): device uuid
            on_callback (function): on callback
            off_callback (function): off callback
            level (GPIO.LOW|GPIO.HIGH): triggered level
        """
        # init
        Thread.__init__(self)
        Thread.daemon = True
        self.logger = logging.getLogger("Gpios")
        # self.logger.setLevel(logging.DEBUG)
        self.device_uuid = device_uuid

        # members
        self.continu = True
        self.pin = pin
        self.logger.debug(
            "Register new input callback for %s which trigger on '%s'",
            device_uuid,
            level,
        )
        self.level = level
        self.debounce = GpioInputWatcher.DEBOUNCE
        self.on_callback = on_callback
        self.off_callback = off_callback

    def stop(self):
        """
        Stop process
        """
        self.continu = False

    def _get_input_level(self):  # pragma: no cover
        """
        Return input value

        Returns:
            (RPi.GPIO.HIGH | RPi.GPIO.LOW): input level
        """
        return GPIO_input(self.pin)

    def run(self):
        """
        Run watcher
        """
        last_level = None
        time_on = 0

        try:
            while self.continu:
                current_level = self._get_input_level()

                if last_level is None:
                    # first iteration, send initial value
                    if current_level == self.level:
                        self.on_callback(self.device_uuid)
                    else:
                        self.off_callback(self.device_uuid, 0)

                elif current_level == last_level:
                    # no level changes drop it
                    pass

                elif current_level == self.level:
                    self.logger.trace("Input %s on" % str(self.pin))
                    time_on = uptime.uptime()
                    self.on_callback(self.device_uuid)
                    time.sleep(self.debounce)

                elif current_level != last_level:
                    self.logger.trace("Input %s off" % str(self.pin))
                    self.off_callback(self.device_uuid, uptime.uptime() - time_on)
                    time.sleep(self.debounce)

                last_level = current_level
                time.sleep(0.125)

        except Exception:  # pragma: no cover
            self.logger.exception("Exception in GpioInputWatcher:")


# RASPI GPIO numbering scheme:
# @see http://raspi.tv/2013/rpi-gpio-basics-4-setting-up-rpi-gpio-numbering-systems-and-inputs
# GPIO#   Pin#  Dedicated I/O
# --------A/B----------------
# GPIO2   3
# GPIO3   5
# GPIO4   7     *
# GPIO14  8
# GPIO15  10
# GPIO17  11    *
# GPIO18  12    *
# GPIO27  13    *
# GPIO22  15    *
# GPIO23  16    *
# GPIO24  18    *
# GPIO10  19
# GPIO9   21
# GPIO25  22    *
# GPIO11  23
# GPIO8   24
# GPIO7   26
# -------A+/B+/B2/Zero/B3--------
# GPIO0   27
# GPIO1   28
# GPIO5   29    *
# GPIO6   31    *
# GPIO12  32    *
# GPIO13  33    *
# GPIO19  35
# GPIO16  36
# GPIO26  37    *
# GPIO20  38
# GPIO21  40
class Gpios(CleepModule):
    """
    Raspberry pi gpios class

    This application is a wapper to RpiGPIO library
    https://sourceforge.net/p/raspberry-gpio-python/wiki/browse_pages/
    """

    MODULE_AUTHOR = "Cleep"
    MODULE_VERSION = "1.3.0"
    MODULE_DEPS = []
    MODULE_DESCRIPTION = "Configure your raspberry pins"
    MODULE_LONGDESCRIPTION = "Gives you access to raspberry pins to configure your inputs/ouputs as you wish quickly and easily."
    MODULE_TAGS = ["gpios", "inputs", "outputs"]
    MODULE_CATEGORY = "DRIVER"
    MODULE_URLINFO = "https://github.com/tangb/cleepmod-gpios"
    MODULE_URLHELP = "https://github.com/tangb/cleepmod-gpios/wiki"
    MODULE_URLSITE = None
    MODULE_URLBUGS = "https://github.com/tangb/cleepmod-gpios/issues"

    MODULE_CONFIG_FILE = "gpios.conf"

    GPIOS_REV1 = {
        "GPIO0": 3,
        "GPIO1": 5,
        "GPIO4": 7,
        "GPIO14": 8,
        "GPIO15": 10,
        "GPIO17": 11,
        "GPIO18": 12,
        "GPIO21": 13,
        "GPIO22": 15,
        "GPIO23": 16,
        "GPIO24": 18,
        "GPIO10": 19,
        "GPIO9": 21,
        "GPIO25": 22,
        "GPIO11": 23,
        "GPIO8": 24,
        "GPIO7": 26,
    }
    GPIOS_REV2 = {
        "GPIO4": 7,
        "GPIO17": 11,
        "GPIO18": 12,
        "GPIO22": 15,
        "GPIO23": 16,
        "GPIO24": 18,
        "GPIO25": 22,
        "GPIO27": 13,
        "GPIO2": 3,
        "GPIO3": 5,
        "GPIO7": 26,
        "GPIO8": 24,
        "GPIO9": 21,
        "GPIO10": 19,
        "GPIO11": 23,
        "GPIO14": 8,
        "GPIO15": 10,
    }
    GPIOS_REV3 = {
        "GPIO5": 29,
        "GPIO6": 31,
        "GPIO12": 32,
        "GPIO13": 33,
        "GPIO26": 37,
        "GPIO0": 27,
        "GPIO1": 28,
        "GPIO19": 35,
        "GPIO16": 36,
        "GPIO20": 38,
        "GPIO21": 40,
    }
    PINS_REV1 = {
        1: "3.3V",
        2: "5V",
        3: "GPIO0",
        4: "5V",
        5: "GPIO1",
        6: "GND",
        7: "GPIO4",
        8: "GPIO14",
        9: "GND",
        10: "GPIO15",
        11: "GPIO17",
        12: "GPIO18",
        13: "GPIO21",
        14: "GND",
        15: "GPIO22",
        16: "GPIO23",
        17: "3.3V",
        18: "GPIO24",
        19: "GPIO10",
        20: "GND",
        21: "GPIO9",
        22: "GPIO25",
        23: "GPIO11",
        24: "GPIO8",
        25: "GND",
        26: "GPIO7",
    }
    PINS_REV2 = {
        1: "3.3V",
        2: "5V",
        3: "GPIO2",
        4: "5V",
        5: "GPIO3",
        6: "GND",
        7: "GPIO4",
        8: "GPIO14",
        9: "GND",
        10: "GPIO15",
        11: "GPIO17",
        12: "GPIO18",
        13: "GPIO27",
        14: "GND",
        15: "GPIO22",
        16: "GPIO23",
        17: "3.3V",
        18: "GPIO24",
        19: "GPIO10",
        20: "GND",
        21: "GPIO9",
        22: "GPIO25",
        23: "GPIO11",
        24: "GPIO8",
        25: "GND",
        26: "GPIO7",
    }
    PINS_REV3 = {
        1: "3.3V",
        2: "5V",
        3: "GPIO2",
        4: "5V",
        5: "GPIO3",
        6: "GND",
        7: "GPIO4",
        8: "GPIO14",
        9: "GND",
        10: "GPIO15",
        11: "GPIO17",
        12: "GPIO18",
        13: "GPIO27",
        14: "GND",
        15: "GPIO22",
        16: "GPIO23",
        17: "3.3V",
        18: "GPIO24",
        19: "GPIO10",
        20: "GND",
        21: "GPIO9",
        22: "GPIO25",
        23: "GPIO11",
        24: "GPIO8",
        25: "GND",
        26: "GPIO7",
        27: "DNC",
        28: "DNC",
        29: "GPIO5",
        30: "GND",
        31: "GPIO6",
        32: "GPIO12",
        33: "GPIO13",
        34: "GND",
        35: "GPIO19",
        36: "GPIO16",
        37: "GPIO26",
        38: "GPIO20",
        39: "GND",
        40: "GPIO21",
    }

    MODE_INPUT = "input"
    MODE_OUTPUT = "output"
    MODE_RESERVED = "reserved"

    INPUT_DROP_THRESHOLD = 0.150  # in ms

    def __init__(self, bootstrap, debug_enabled):
        """
        Constructor

        Args:
            bootstrap (dict): bootstrap objects
            debug_enabled: debug status
        """
        CleepModule.__init__(self, bootstrap, debug_enabled)

        # members
        self._input_watchers = {}
        self.gpios_on_states = {}

        # events
        self.gpios_gpio_off = self._get_event("gpios.gpio.off")
        self.gpios_gpio_on = self._get_event("gpios.gpio.on")

    def _configure(self):
        """
        Configure application
        """
        # configure raspberry pi
        GPIO_setmode(GPIO_BOARD)
        GPIO_setwarnings(False)

    def get_module_devices(self):
        config_devices = super().get_module_devices()

        # update volatile gpios "on" state (gpios with keep to False will
        # not have current state propagated otherwise)
        for device_uuid, config_device in config_devices.items():
            device_on = config_device.get("on", False)
            config_device["on"] = self.gpios_on_states.get(device_uuid, device_on)

        return config_devices

    def _on_start(self):
        """
        Start application
        """
        # configure gpios
        devices = self.get_module_devices()
        for uuid in devices:
            self._configure_gpio(devices[uuid])

    def _on_stop(self):
        """
        Stop application
        """
        # stop input watchers
        for uuid in self._input_watchers:
            self._input_watchers[uuid].stop()

        # cleanup gpios
        GPIO_cleanup()

    def _gpio_setup(self, pin, mode, pull_mode=None):
        """
        Gpio setup

        Args:
            pin (number): Pin number
            mode (number): Pin mode (GPIO_IN|GPIO_OUT)
            pull_mode (number): Pin pull mode, for input only (GPIO_PUD_UP|GPIO_PUD_DOWN)
        """
        if mode == GPIO_IN and pull_mode:
            GPIO_setup(pin, mode, pull_up_down=pull_mode)
        elif mode == GPIO_IN and not pull_mode:
            GPIO_setup(pin, mode)
        elif mode == GPIO_OUT:
            GPIO_setup(pin, mode)

    def _gpio_output(self, pin, level):
        """
        Set gpio output level

        Args:
            pin (int): pin number
            level (int): RPi.GPIO.LOW or RPi.GPIO.HIGH
        """
        GPIO_output(pin, level)

    def __launch_input_watcher(self, device):
        """
        Launch input watcher for specified device

        Args:
            device (dict): device data
        """
        self.logger.debug(
            'Launch input watcher for device "%s" (inverted=%s)'
            % (device["uuid"], device["inverted"])
        )
        level = GPIO_HIGH if device.get("inverted", False) else GPIO_LOW
        watcher = GpioInputWatcher(
            device["pin"],
            device["uuid"],
            self.__input_on_callback,
            self.__input_off_callback,
            level,
        )
        self._input_watchers[device["uuid"]] = watcher
        watcher.start()

    def _configure_gpio(self, device):
        """
        Configure GPIO (internal use)

        Args:
            device (dict): device object

        Returns:
            bool: True if gpio is configured False otherwise
        """
        self.logger.debug("Configure gpio for device %s" % (device))

        # check if gpio is not reserved
        if device["mode"] == self.MODE_RESERVED:
            self.logger.debug("Reserved gpio cannot be configured")
            return True

        try:
            # get gpio pin
            if device["mode"] == self.MODE_OUTPUT:
                self.logger.debug(
                    "Configure gpio %s pin %d as OUTPUT with on=%s",
                    device["gpio"],
                    device["pin"],
                    device["on"],
                )

                if device["on"]:
                    self._gpio_setup(device["pin"], GPIO_OUT)
                    self.turn_on(device["uuid"])

                    # and broadcast gpio status at startup
                    self.logger.debug(
                        "Broadcast event %s for gpio %s",
                        "gpios.gpio.on",
                        device["gpio"],
                    )
                    self.gpios_gpio_on.send(
                        params={"gpio": device["gpio"], "init": True, "on": True},
                        device_id=device["uuid"],
                    )

                else:
                    self._gpio_setup(device["pin"], GPIO_OUT)
                    self.turn_off(device["uuid"])

                    # and broadcast gpio status at startup
                    self.logger.debug(
                        "Broadcast event %s for gpio %s",
                        "gpios.gpio.off",
                        device["gpio"],
                    )
                    self.gpios_gpio_off.send(
                        params={
                            "gpio": device["gpio"],
                            "init": True,
                            "duration": 0,
                            "on": False,
                        },
                        device_id=device["uuid"],
                    )

            elif device["mode"] == self.MODE_INPUT:
                # always PUD_UP: https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/
                self._gpio_setup(device["pin"], GPIO_IN, pull_mode=GPIO_PUD_UP)

                # and launch input watcher
                self.__launch_input_watcher(device)

            return True

        except Exception:
            self.logger.exception("Exception during GPIO configuration:")
            return False

    def _reconfigure_gpio(self, device):
        """
        Reconfigure specified gpio. A reconfiguration consists of stopping watcher and launch it again with new parameters

        Args:
            device (dict): device data

        Returns:
            True if gpio reconfigured successfully, False otherwise
        """
        # stop watcher
        deconfigured = self._deconfigure_gpio(device)
        if not deconfigured:
            return False

        # launch new watcher
        self.__launch_input_watcher(device)
        return True

    def _deconfigure_gpio(self, device):
        """
        Deconfigure device stopping its watcher

        Args:
            device (dict): device data

        Returns:
            True if gpio deconfigured successfully, False otherwise
        """
        if device["mode"] == self.MODE_OUTPUT:
            # nothing to deconfigure for output
            return True

        # get watcher
        if device["uuid"] not in self._input_watchers:
            self.logger.debug('No gpio watcher found for device "%s"' % device)
            return False

        # stop and launch again watcher
        self._input_watchers[device["uuid"]].stop()
        del self._input_watchers[device["uuid"]]

        return True

    def __input_on_callback(self, device_uuid):
        """
        Callback when input is turned on (internal use)

        Args:
            device_uuid (string): device uuid
        """
        self.logger.debug("on_callback for gpio %s triggered" % device_uuid)
        device = self._get_device(device_uuid)
        if device is None:
            raise Exception('Device "%s" not found' % device_uuid)

        # save current state
        device["on"] = True
        if device.get("keep", False):
            self._update_device(device_uuid, device)
        else:
            self.gpios_on_states[device_uuid] = device["on"]

        # broadcast event
        self.gpios_gpio_on.send(
            params={"gpio": device["gpio"], "init": False, "on": True},
            device_id=device_uuid,
        )

    def __input_off_callback(self, device_uuid, duration):
        """
        Callback when input is turned off

        Args:
            device_uuid (string): device uuid
            duration (float): trigger duration
        """
        self.logger.debug("off_callback for gpio %s triggered" % device_uuid)
        device = self._get_device(device_uuid)
        if device is None:
            raise Exception('Device "%s" not found' % device_uuid)

        # save current state
        device["on"] = False
        if device["keep"]:
            self._update_device(device_uuid, device)
        else:
            self.gpios_on_states[device_uuid] = device["on"]

        # broadcast event
        self.gpios_gpio_off.send(
            params={
                "gpio": device["gpio"],
                "init": False,
                "duration": duration,
                "on": False,
            },
            device_id=device_uuid,
        )

    def _get_revision(self):
        """
        Return raspberry pi revision

        Returns:
            int: raspberry pi revision number
        """
        return GPIO_RPI_INFO["P1_REVISION"]

    def get_module_config(self):
        """
        Return module full config

        Returns:
            gpios configuration::

                {
                    revision (int): revision number (1|2|3)
                    pinsnumber (int): number of board pins
                }

        """
        config = {}

        config["revision"] = self._get_revision()
        config["pinsnumber"] = self.get_pins_number()

        return config

    def get_pins_usage(self):
        """
        Return pins usage

        Returns:
            dict: dict of pins::

                {
                    pin (int): {
                        label (str): Gpio label ("GPIOX"|"5v"|"3.3v"|"gnd"|"dnc"),
                        gpio (dict): {
                            assigned (bool): True if gpio assigned,
                            owner (str): gpio application owner or None,
                        }
                    },
                    ...
                }

        """
        output = {}

        # get pins descriptions according to raspberry pi revision
        all_pins = {}
        rev = self._get_revision()
        if rev == 1:
            all_pins = self.PINS_REV1
        elif rev == 2:
            all_pins = self.PINS_REV2
        elif rev == 3:
            all_pins = self.PINS_REV3
        self.logger.debug("all_pins %s" % all_pins)

        # fill pins usage
        all_gpios = self.get_raspi_gpios()
        self.logger.debug("all_gpios %s" % all_gpios)
        devices = self.get_module_devices()
        for pin_number in all_pins:
            # default pin data
            output[pin_number] = {"label": all_pins[pin_number], "gpio": None}

            # fill gpio data
            if all_pins[pin_number] in all_gpios:
                gpio_name = all_pins[pin_number]
                assigned = False
                owner = None
                for uuid in devices:
                    if devices[uuid]["gpio"] == gpio_name:
                        assigned = True
                        owner = devices[uuid]["owner"]
                        break

                output[pin_number]["gpio"] = {"assigned": assigned, "owner": owner}

        return output

    def get_assigned_gpios(self):
        """
        Return assigned gpios

        Returns:
            list: List of gpios::

                [ "GPIO3", "GPIO5", ... ]

        """
        return [device["gpio"] for _, device in self.get_module_devices().items()]

    def get_raspi_gpios(self):
        """
        Return available GPIO pins according to board revision

        Returns:
            dict: Dict of gpios::

                {
                    "GPIO1": 5,
                    "GPIO1": 5,
                    ...
                }

        """
        rev = self._get_revision()

        if rev == 1:
            return self.GPIOS_REV1
        if rev == 2:
            return self.GPIOS_REV2
        if rev == 3:
            gpios = self.GPIOS_REV2.copy()
            gpios.update(self.GPIOS_REV3)
            return gpios

        return {}

    def get_pins_number(self):
        """
        Return pins number according to board revision

        Returns:
            int: pins number
        """
        rev = self._get_revision()

        if rev in (1, 2):
            return 26
        if rev == 3:
            return 40

        return 0

    def reserve_gpio(self, name, gpio, usage, command_sender):
        """
        Reserve a gpio used to configure raspberry pi (ie onewire, lirc...)
        This action only flag this gpio as reserved to avoid using it again

        Args:
            name (str): name of gpio
            gpio (str) : gpio value
            usage (str) : describe gpio usage
            command_sender (str): command request sender (used to set gpio in readonly mode)

        Returns:
            dict: Created gpio device::

                {
                    name (str): name of gpio
                    mode (str): Gpio mode ("output"|"input")
                    pin (number): Gpio pin number
                    gpio (str): Gpio id (GPIOX)
                    keep (bool): True if gpio value is stored in config and restored after reboot
                    on (bool): True if gpio is on
                    inverted (bool): Gpio has inverted state
                    owner (str): Application that owns the gpio
                    type (str): Always "gpio"
                    subtype (str): Same value than mode
                }

        Raises:
            CommandError: Command failed
            MissingParameter: Missing command parameter
            InvalidParameter: Invalid command parameter
        """
        # fix command_sender: rpcserver is the default gpio entry point
        if command_sender == "rpcserver":
            command_sender = "gpios"

        # check values
        if gpio:
            found_gpio = self._search_device("gpio", gpio)
            if found_gpio is not None and found_gpio["subtype"] != usage:
                raise InvalidParameter(
                    'Gpio "%s" is already reserved for "%s" usage'
                    % (found_gpio["gpio"], found_gpio["subtype"])
                )
            if found_gpio is not None and found_gpio["subtype"] == usage:
                return found_gpio
        self._check_parameters(
            [
                {
                    "name": "name",
                    "value": name,
                    "type": str,
                    "validator": lambda val: self._search_device("name", val) is None,
                    "message": 'Name "%s" is already used' % name,
                },
                {
                    "name": "gpio",
                    "value": gpio,
                    "type": str,
                    "validator": lambda val: val in self.get_raspi_gpios().keys(),
                    "message": 'Gpio "%s" does not exist for this raspberry pi' % gpio,
                },
                {"name": "usage", "value": usage, "type": str},
            ]
        )

        # gpio is valid, prepare new entry
        data = {
            "name": name,
            "mode": self.MODE_RESERVED,
            "pin": self.get_raspi_gpios()[gpio],
            "gpio": gpio,
            "keep": False,
            "on": False,
            "inverted": False,
            "owner": command_sender,
            "type": "gpio",
            "subtype": usage,
        }

        # add device
        self.logger.debug("data=%s" % data)
        device = self._add_device(data)
        if device is None:
            raise CommandError("Unable to add device")

        return device

    def get_reserved_gpios(self, usage):
        """
        Return reserved gpios for specified usage

        Args:
            usage (str): gpio reserved usage

        Returns:
            list: list of reserved gpios (full data)::

                [
                    {
                        gpio: "GPIO1",
                        pin: 1,
                        ...
                    },
                    ...
                ]

        """
        if usage is None or len(usage) == 0:
            raise MissingParameter('Parameter "usage" is missing')

        gpios = self._search_devices("subtype", usage)
        return [gpio for gpio in gpios if gpio["mode"] == self.MODE_RESERVED]

    def is_reserved_gpio(self, gpio):
        """
        Return True if gpio is reserved

        Args:
            gpio (str): gpio

        Returns:
            bool: True if gpio is reserved, False otherwise
        """
        device = self._search_device("gpio", gpio)
        if device is None:
            return False

        self.logger.debug("is_reserved_gpio: %s" % device)
        if device["mode"] == self.MODE_RESERVED:
            return True

        return False

    def add_gpio(self, name, gpio, mode, keep, inverted, command_sender):
        """
        Add new gpio

        Args:
            name (str): name of gpio
            gpio (str): selected gpio ("GPIOX")
            mode (str): mode ("input"|"output")
            keep (bool): keep state when restarting
            inverted (bool): if true a callback will be triggered on gpio high level instead of low level
            command_sender (str): command request sender (optional)

        Returns:
            dict: created gpio device ::

                {
                    name (str): name of gpio
                    mode (str): Gpio mode ("output"|"input")
                    pin (number): Gpio pin number
                    gpio (str): Gpio id (GPIOX)
                    keep (bool): True if gpio value is stored in config and restored after reboot
                    on (bool): True if gpio is on
                    inverted (bool): Gpio has inverted state
                    owner (str): Application that owns the gpio
                    type (str): Always "gpio"
                    subtype (str): Same value than mode
                }

        Raises:
            CommandError: Command failed
            MissingParameter: Missing command parameter
            InvalidParameter: Invalid command parameter specified
        """
        # fix command_sender: rpcserver is the default gpio entry point
        if command_sender == "rpcserver":
            command_sender = "gpios"

        # check values
        self._check_parameters(
            [
                {
                    "name": "name",
                    "value": name,
                    "type": str,
                    "validator": lambda val: self._search_device("name", val) is None,
                    "message": 'Name "%s" is already used' % name,
                },
                {
                    "name": "gpio",
                    "value": gpio,
                    "type": str,
                    "validators": [
                        {
                            "validator": lambda val: val
                            in self.get_raspi_gpios().keys(),
                            "message": 'Gpio "%s" does not exist for this raspberry pi'
                            % gpio,
                        },
                        {
                            "validator": lambda val: self._search_device("gpio", gpio)
                            is None,
                            "message": 'Gpio "%s" is already used by other application'
                            % gpio,
                        },
                    ],
                },
                {
                    "name": "mode",
                    "value": mode,
                    "type": str,
                    "validator": lambda val: val in (self.MODE_INPUT, self.MODE_OUTPUT),
                },
                {"name": "keep", "value": keep, "type": bool},
                {"name": "inverted", "value": inverted, "type": bool},
            ]
        )

        # gpio is valid, prepare new entry
        data = {
            "name": name,
            "mode": mode,
            "pin": self.get_raspi_gpios()[gpio],
            "gpio": gpio,
            "keep": keep,
            "on": False,
            "inverted": inverted,
            "owner": command_sender,
            "type": "gpio",
            "subtype": mode,
        }

        # add device
        device = self._add_device(data)
        if device is None:
            raise CommandError("Unable to add device")

        # configure it
        self._configure_gpio(device)

        return device

    def delete_gpio(self, device_uuid, command_sender):
        """
        Delete gpio

        Args:
            device_uuid (str): device identifier
            command_sender (str): command sender

        Returns:
            bool: True if device was deleted, False otherwise

        Raises:
            CommandError: Command failed
            MissingParameter: Missing command parameter
            Unauthorized: Command cannot be executed by application
            InvalidParameter: Invalid command parameter
        """
        # fix command_sender: rpcserver is the default gpio entry point
        if command_sender == "rpcserver":
            command_sender = "gpios"

        # check values
        self._check_parameters(
            [
                {"name": "device_uuid", "value": device_uuid, "type": str},
            ]
        )
        device = self._get_device(device_uuid)
        if device is None:
            raise InvalidParameter('Device "%s" does not exist' % device_uuid)
        if device["owner"] != command_sender:
            raise Unauthorized("Device can only be deleted by its owner")

        # device is valid, remove entry
        if not self._delete_device(device_uuid):
            raise CommandError('Failed to delete device "%s"' % device["uuid"])

        self._deconfigure_gpio(device)

        return True

    def update_gpio(self, device_uuid, name, keep, inverted, command_sender):
        """
        Update gpio

        Args:
            device_uuid (str): device identifier
            name (str): gpio name
            keep (bool): keep status flag
            inverted (bool): inverted flag
            command_sender (str): command sender

        Returns:
            dict: updated gpio device::

                {
                    name (str): name of gpio
                    mode (str): Gpio mode ("output"|"input")
                    pin (number): Gpio pin number
                    gpio (str): Gpio id (GPIOX)
                    keep (bool): True if gpio value is stored in config and restored after reboot
                    on (bool): True if gpio is on
                    inverted (bool): Gpio has inverted state
                    owner (str): Application that owns the gpio
                    type (str): Always "gpio"
                    subtype (str): Same value than mode
                }

        Raises:
            CommandError: Command failed
            MissingParameter: Missing command parameter
            Unauthorized: Command cannot be executed by application
            InvalidParameter: Invalid command parameter
        """
        # fix command_sender: rpcserver is the default gpio entry point
        if command_sender == "rpcserver":
            command_sender = "gpios"

        # check values
        self._check_parameters(
            [
                {"name": "device_uuid", "value": device_uuid, "type": str},
                {"name": "name", "value": name, "type": str},
                {"name": "keep", "value": keep, "type": bool},
                {"name": "inverted", "value": inverted, "type": bool},
            ]
        )
        device = self._get_device(device_uuid)
        if device is None:
            raise InvalidParameter('Device "%s" does not exist' % device_uuid)
        if device["owner"] != command_sender:
            raise Unauthorized("Device can only be updated by its owner")

        # device is valid, update entry
        device["name"] = name
        device["keep"] = keep
        device["inverted"] = inverted
        if not self._update_device(device_uuid, device):
            raise CommandError('Failed to update device "%s"' % device["uuid"])

        # relaunch watcher
        self._reconfigure_gpio(device)

        return device

    def turn_on(self, device_uuid):
        """
        Turn on specified output gpio

        Args:
            device_uuid (str): device identifier

        Returns:
            bool: True if command executed successfully

        Raises:
            CommandError: Command failed
        """
        # check values
        device = self._get_device(device_uuid)
        if device is None:
            raise CommandError("Device not found")
        if device["mode"] != self.MODE_OUTPUT:
            raise CommandError(
                'Gpio "%s" configured as "%s" cannot be turned on'
                % (device["gpio"], device["mode"])
            )

        # turn on output
        self.logger.debug("Turn on GPIO %s" % device["gpio"])
        level = GPIO_LOW if device.get("inverted", False) else GPIO_HIGH
        self._gpio_output(device["pin"], level)

        # save current state
        device["on"] = True
        if device["keep"]:
            self._update_device(device_uuid, device)
        else:
            self.gpios_on_states[device_uuid] = device["on"]

        # broadcast event
        self.gpios_gpio_on.send(
            params={"gpio": device["gpio"], "init": False}, device_id=device_uuid
        )

        return True

    def turn_off(self, device_uuid):
        """
        Turn off specified output gpio

        Args:
            device_uuid (str): device identifier

        Returns:
            bool: True if command executed successfully

        Raises:
            CommandError: Command failed
        """
        device = self._get_device(device_uuid)
        if device is None:
            raise CommandError("Device not found")
        if device["mode"] != self.MODE_OUTPUT:
            raise CommandError(
                'Gpio "%s" configured as "%s" cannot be turned off'
                % (device["gpio"], device["mode"])
            )

        # turn off output
        self.logger.debug("Turn off GPIO %s" % device["gpio"])
        level = GPIO_HIGH if device.get("inverted", False) else GPIO_LOW
        self._gpio_output(device["pin"], level)

        # save current state
        device["on"] = False
        if device["keep"]:
            self._update_device(device_uuid, device)
        else:
            self.gpios_on_states[device_uuid] = device["on"]

        # broadcast event
        self.gpios_gpio_off.send(
            params={"gpio": device["gpio"], "init": False, "duration": 0},
            device_id=device_uuid,
        )

        return True

    def is_on(self, device_uuid):
        """
        Return gpio status (on or off)

        Args:
            device_uuid (str): device identifier

        Returns:
            bool: True if device is on, False if device is off

        Raises:
            CommandError: Command failed
        """
        # check values
        device = self._get_device(device_uuid)
        if device is None:
            raise CommandError("Device not found")
        if device["mode"] == self.MODE_RESERVED:
            raise CommandError(
                'Gpio "%s" configured as "%s" cannot be checked'
                % (device["gpio"], device["mode"])
            )

        return device["on"]

    def is_gpio_on(self, gpio):
        """
        Get value of specified gpio. Gpio doesn't have to be declared as device

        Args:
            gpio (str): gpio name

        Returns:
            bool: True if gpio is on, False otherwise
        """
        # check values
        all_gpios = self.get_raspi_gpios()
        self._check_parameters(
            [
                {
                    "name": "gpio",
                    "value": gpio,
                    "type": str,
                    "validator": lambda val: gpio in all_gpios.keys(),
                },
            ]
        )

        pin = all_gpios[gpio]
        self.logger.debug('Read value for gpio "%s" (pin %s)' % (gpio, pin))

        return GPIO_input(pin) == GPIO_HIGH

    def reset_gpios(self):
        """
        Reset all gpios turning them off
        """
        devices = self.get_module_devices()
        for uuid in devices:
            if devices[uuid]["mode"] == Gpios.MODE_OUTPUT:
                self.turn_off(uuid)
