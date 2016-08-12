import logging

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


class EventDescriptor(object):
    def __init__(self, ctx):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))
        self._ctx = ctx
        self._cb = None

    def set_callback(self, callback):
        self._cb = callback

    def subscribe(self, duration=None, callback=None):
        self.log.info("Subscribe for Event: {}".format(self._ctx._upi))

    def unsubscribe(self):
        self.log.info("Unsubscribe from Event: {}".format(self._ctx._upi))
