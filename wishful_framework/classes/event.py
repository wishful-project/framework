import logging

__author__ = "Piotr Gawlowicz, Anatolij Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, zubow}@tkn.tu-berlin.de"


class Event(object):
    def __init__(self):
        pass


class TimeEvent(Event):
    def __init__(self, func, args=(), interval=1, iface=None):
        super(TimeEvent, self).__init__()
        self.upi_type = func.__module__
        self.upi_func = func.__name__
        self.args = args
        self.interval = interval
        self.iface = iface


class PktEvent(Event):
    def __init__(self, iface):
        super(PktEvent, self).__init__()
        self.iface = iface
