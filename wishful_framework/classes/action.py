import logging

__author__ = "Piotr Gawlowicz, Anatolij Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, zubow}@tkn.tu-berlin.de"


class Action(object):
    def __init__(self, func, args=()):       
        self.upi_type = func.__module__
        self.upi_func = func.__name__
        self.args = args