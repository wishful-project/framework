import logging
import threading
import collections
import inspect

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


def on_event(ev_cls, dispatchers=None):
    def _set_ev_cls_dec(handler):
        if 'callers' not in dir(handler):
            handler.callers = {}
        for e in _listify(ev_cls):
            handler.callers[e] = e.__module__
        return handler
    return _set_ev_cls_dec


def _listify(may_list):
    if may_list is None:
        may_list = []
    if not isinstance(may_list, list):
        may_list = [may_list]
    return may_list


def _is_method(f):
    return inspect.isfunction(f) or inspect.ismethod(f)


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


class on_first_call_to_module(object):
    def __init__(self):
        self.onFirstCallToModule = True

    def __call__(self, f):
        f._onFirstCallToModule = self.onFirstCallToModule
        return f


class before_call(object):
    def __init__(self, function):
        self.beforeCall = function.__name__

    def __call__(self, f):
        f._beforeCall = self.beforeCall
        return f


class after_call(object):
    def __init__(self, function):
        self.afterCall = function.__name__

    def __call__(self, f):
        f._afterCall = self.afterCall
        return f


def on_function(upiFunc):
    def _set_ev_cls_dec(handler):
        if '_upiFunc_' not in dir(handler):
            handler._upiFunc_ = None
        handler._upiFunc_ = upiFunc.__module__ + "." + upiFunc.__name__
        return handler
    return _set_ev_cls_dec

bind_function = on_function


def bind_event_start(upiFunc):
    def _set_ev_cls_dec(handler):
        if '_event_start_' not in dir(handler):
            handler._upiFunc_ = None
        handler._upiFunc_ = upiFunc.__module__ + "." + upiFunc.__name__
        return handler
    return _set_ev_cls_dec


def bind_event_stop(upiFunc):
    def _set_ev_cls_dec(handler):
        if '_event_stop_' not in dir(handler):
            handler._upiFunc_ = None
        handler._upiFunc_ = upiFunc.__module__ + "." + upiFunc.__name__
        return handler
    return _set_ev_cls_dec


def bind_service_start(upiFunc):
    def _set_ev_cls_dec(handler):
        if '_service_start_' not in dir(handler):
            handler._upiFunc_ = None
        handler._upiFunc_ = upiFunc.__module__ + "." + upiFunc.__name__
        return handler
    return _set_ev_cls_dec


def bind_service_stop(upiFunc):
    def _set_ev_cls_dec(handler):
        if '_service_stop_' not in dir(handler):
            handler._upiFunc_ = None
        handler._upiFunc_ = upiFunc.__module__ + "." + upiFunc.__name__
        return handler
    return _set_ev_cls_dec


def build_module(module_class):
    original_methods = module_class.__dict__.copy()
    for name, method in original_methods.items():
        if hasattr(method, '_upi_fname'):
            # add UPI alias for the function
            for falias in method._upi_fname - set(original_methods):
                setattr(module_class, falias, method)
    return module_class


class WishfulModule(object):
    def __init__(self):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))

        self.id = None
        self.name = self.__class__.__name__
        self.agent = None
        self.moduleManager = None
        self.device = None  # used for filtering of commands
        self.deviceId = None  # used for filtering of commands
        self.attributes = []
        self.functions = []
        self.events = []
        self.services = []
        self.firstCallToModule = False

    def set_device(self, dev):
        self.device = dev

    def get_device(self):
        return self.device

    def set_module_manager(self, mm):
        self.moduleManager = mm

    def send_event(self, event):
        self.moduleManager.send_event(event)

    def set_agent(self, agent):
        self.agent = agent

    def set_controller(self, controller):
        self.controller = controller

    def get_attributes(self):
        return self.attributes

    def get_functions(self):
        return self.functions

    def get_events(self):
        return self.events

    def get_services(self):
        return self.services

    def execute_function(self, func):
        create_new_thread = hasattr(func, '_create_new_thread')
        if create_new_thread:
            self.threads = threading.Thread(target=func,
                                            name="upi_func_execution_{}"
                                            .format(func.__name__))
            self.threads.setDaemon(True)
            self.threads.start()
        else:
            func()

    def start_event_thread(self,):
        pass

    def stop_event_thread(self,):
        pass

    def start_service_thread(self,):
        pass

    def stop_service_thread(self,):
        pass

    def start(self):
        # discover all functions that have to be executed on start
        funcs = [method for method in dir(self) if isinstance(getattr(
            self, method), collections.Callable) and hasattr(
            getattr(self, method), '_onStart')]
        for fname in funcs:
            f = getattr(self, fname)
            self.execute_function(f)

    def exit(self):
        # discover all functions that have to be executed on exit
        funcs = [method for method in dir(self) if isinstance(getattr(
            self, method), collections.Callable) and hasattr(
            getattr(self, method), '_onExit')]
        for fname in funcs:
            f = getattr(self, fname)
            self.execute_function(f)

    def connected(self):
        # discover all functions that have to be executed on connected
        funcs = [method for method in dir(self) if isinstance(getattr(
            self, method), collections.Callable) and hasattr(
            getattr(self, method), '_onConnected')]
        for fname in funcs:
            f = getattr(self, fname)
            self.execute_function(f)

    def disconnected(self):
        # discover all functions that have to be executed on disconnected
        funcs = [method for method in dir(self) if isinstance(getattr(
            self, method), collections.Callable) and hasattr(
            getattr(self, method), '_onDisconnected')]
        for fname in funcs:
            f = getattr(self, fname)
            self.execute_function(f)

    def first_call_to_module(self):
        # discover all functions that have to be executed before first UPI
        # function call to module
        funcs = [method for method in dir(self) if isinstance(getattr(
            self, method), collections.Callable) and hasattr(
            getattr(self, method), '_onFirstCallToModule')]
        for fname in funcs:
            f = getattr(self, fname)
            self.execute_function(f)


class ControllerModule(WishfulModule):
    def __init__(self, controller):
        super(ControllerModule, self).__init__()
        self.controller = controller


class AgentModule(WishfulModule):
    def __init__(self):
        super(AgentModule, self).__init__()
