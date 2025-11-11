#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cleep.libs.internals.event import Event


class GpiosGpioOffEvent(Event):
    """
    Gpios.gpio.off event
    """

    EVENT_NAME = "gpios.gpio.off"
    EVENT_PARAMS = ["gpio", "init", "duration", "on"]

    def __init__(self, params):
        """
        Constructor

        Args:
            params (dict): event parameters
        """
        Event.__init__(self, params)
