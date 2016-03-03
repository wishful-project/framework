import logging
import zmq
import random
import sys
import time
import threading
import wishful_framework as msgs

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


class discover_controller(object):
    def __init__(self, ):
        self.discover_controller = True

    def __call__(self, f):
        f._discover_controller = self.discover_controller
        return f

class run_in_thread(object):
    def __init__(self, ):
        self.create_new_thread = True

    def __call__(self, f):
        f._create_new_thread = self.create_new_thread
        return f


class on_start(object):
    def __init__(self, ):
        self.onStart = True

    def __call__(self, f):
        f._onStart = self.onStart
        return f


class on_exit(object):
    def __init__(self):
        self.onExit = True

    def __call__(self, f):
        f._onExit = self.onExit
        return f


class on_connected(object):
    def __init__(self):
        self.onConnected = True

    def __call__(self, f):
        f._onConnected = self.onConnected
        return f


class on_disconnected(object):
    def __init__(self):
        self.onDisconnected = True

    def __call__(self, f):
        f._onDisconnected = self.onDisconnected
        return f


class bind_function(object):
    def __init__(self, upiFunc):
        fname = upiFunc.__name__
        self.upi_fname = set([fname])

    def __call__(self, f):
        f._upi_fname = self.upi_fname
        return f

def build_module(module_class):
    original_methods = module_class.__dict__.copy()
    for name, method in original_methods.iteritems():
        if hasattr(method, '_upi_fname'):
            #add UPI alias for the function
            for falias in method._upi_fname - set(original_methods):
                setattr(module_class, falias, method)
    return module_class


class WishfulModule(object):
    def __init__(self):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))

        self.id = None
        self.name = self.__class__.__name__
        self.capabilities = []

        #discover UPI function implementation and create upi_capabilities list
        func_name = [method for method in dir(self) if callable(getattr(self, method)) and hasattr(getattr(self, method), '_upi_fname')]
        self.upi_callbacks = {list(getattr(self, method)._upi_fname)[0] : method for method in func_name}
        self.upis_capabilities = self.upi_callbacks.keys()
        
        #interface to be used in UPI functions, it is set before function call
        self.interface = None


    def get_capabilities(self):
        return self.upis_capabilities


    def set_controller(self):
        #discover controller discovery function
        pass


    def get_controller(self):
        #discover controller discovery function
        funcs = [method for method in dir(self) if callable(getattr(self, method)) and hasattr(getattr(self, method), '_discover_controller')]
        fname = funcs[0]
        func = getattr(self, fname)
        if func:
            return func()
        else:
            return


    def execute_function(self, func):
        create_new_thread = hasattr(func, '_create_new_thread')
        if create_new_thread:
            self.threads = threading.Thread(target=func)
            self.threads.setDaemon(True)
            self.threads.start()
        else:
            func()


    def start(self):
        #discover all functions that have to be executen on start
        funcs = [method for method in dir(self) if callable(getattr(self, method)) and hasattr(getattr(self, method), '_onStart')]
        for fname in funcs:
            f = getattr(self, fname)
            self.execute_function(f)


    def exit(self):
        #discover all functions that have to be executen on exit
        funcs = [method for method in dir(self) if callable(getattr(self, method)) and hasattr(getattr(self, method), '_onExit')]
        for fname in funcs:
            f = getattr(self, fname)
            self.execute_function(f)


    def connected(self):
        #discover all functions that have to be executen on connected
        funcs = [method for method in dir(self) if callable(getattr(self, method)) and hasattr(getattr(self, method), '_onConnected')]
        for fname in funcs:
            f = getattr(self, fname)
            self.execute_function(f)


    def disconnected(self):
        #discover all functions that have to be executen on disconnected
        funcs = [method for method in dir(self) if callable(getattr(self, method)) and hasattr(getattr(self, method), '_onDisconnected')]
        for fname in funcs:
            f = getattr(self, fname)
            self.execute_function(f)