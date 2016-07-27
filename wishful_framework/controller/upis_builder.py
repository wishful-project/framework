import sys
import wishful_upis
import decorator
from types import FunctionType

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


@decorator.decorator
def _add_function(fn, *args, **kwargs):
    def wrapped(self, *args, **kwargs):
        # send function to controller
        return self._ctrl.exec_cmd(upi_type=self._msg_type,
                                   fname=fn.__name__, args=args, kwargs=kwargs)
    return wrapped(*args, **kwargs)


def functions_in_class(module):
    md = module.__dict__
    return [
        md[c] for c in md if (
            isinstance(md[c], FunctionType)
        )
    ]

def classes_in_module(module):
    md = module.__dict__
    return [
        md[c] for c in md if (
            isinstance(md[c], type)
        )
    ]

def iface_func(self, iface):
    self._ctrl.iface(iface)
    return self


class UpiBuilder(object):
    def __init__(self, ctrl):
        self._ctrl = ctrl

    def create_upi(self, upiClass, upiType):
        setattr(upiClass, "_ctrl", None)
        setattr(upiClass, "_msg_type", None)
        upiClass.iface = iface_func

        # flatten UPIs, i.e. wifiRadioUpis -> radioUpis
        # TODO: remove it in some point in future, when people will agree on new sytnax
        classList = classes_in_module(sys.modules[upiClass.__module__])
        print("classlist ", classList)
        for c in classList:
            if c.__name__ == upiClass.__name__:
                continue
            funcs = functions_in_class(c)
            print("class name ", c.__name__)
            for f in funcs:
                print("function: ",f.__name__)
                setattr(upiClass, f.__name__, f)

        # decorate all UPI functions in UPI class to exec_command
        upiList = functions_in_class(upiClass)
        for upi in upiList:
            upi = _add_function(upi)
            setattr(upiClass, upi.__name__, upi)

        upiObj = upiClass()
        upiObj._ctrl = self._ctrl
        upiObj._msg_type = upiType
        return upiObj
