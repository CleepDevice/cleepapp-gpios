#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cleep.libs.internals.event import Event


class GpiosGpioOnEvent(Event):
    """
    Gpios.gpio.on event
    """

    EVENT_NAME = "gpios.gpio.on"
    EVENT_PARAMS = ["gpio", "init", "on"]

    def __init__(self, params):
        """
        Constructor

        Args:
            params (dict): event parameters
        """
        Event.__init__(self, params)
