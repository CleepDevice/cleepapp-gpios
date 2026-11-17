# Stub Raspberry Pi GPIO before collecting tests (hosts without RPi hardware).
import sys
import types
from unittest.mock import MagicMock

_gpio = types.ModuleType("RPi.GPIO")
_gpio.LOW = 0
_gpio.HIGH = 1
_gpio.BOARD = 10
_gpio.BCM = 11
_gpio.OUT = 0
_gpio.IN = 1
_gpio.PUD_DOWN = 20
_gpio.PUD_UP = 22
_gpio.RPI_INFO = {"P1_REVISION": 3}
_gpio.cleanup = MagicMock()
_gpio.setup = MagicMock()
_gpio.input = MagicMock(return_value=0)
_gpio.output = MagicMock()
_gpio.setmode = MagicMock()
_gpio.setwarnings = MagicMock()

_rpi = types.ModuleType("RPi")
_rpi.GPIO = _gpio
sys.modules.setdefault("RPi", _rpi)
sys.modules.setdefault("RPi.GPIO", _gpio)
