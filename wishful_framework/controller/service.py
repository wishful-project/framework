import logging

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


class ServiceDescriptor(object):
    def __init__(self, ctx):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))
        self._ctx = ctx
        self._cb = None

    def set_callback(self, callback):
        self._cb = callback

    def start(self, duration=None, callback=None):
        self.log.info("Start Service: {}".format(self._ctx._upi))

    def stop(self):
        self.log.info("Stop Service: {}".format(self._ctx._upi))
