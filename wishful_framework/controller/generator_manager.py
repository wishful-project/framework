import logging
import Queue
from wishful_framework import TimeEvent, PktEvent, MovAvgFilter, PeakDetector, Match, Action, Permanance

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


class LocalGeneratorDescriptor(object):
    def __init__(self, genManager, genId, event, filters=[], match=None):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))
        self.id = genId
        self.genManager = genManager
        self.event = event
        self.filters = filters
        self.match = match

        self._stop = False
        self.sampleQueue = Queue.Queue()

    def __iter__(self):
        return self

    # Python 3 compatibility
    def __next__(self):
        return self.next()

    def next(self):
        if not self._stop:
            try:
                return self.sampleQueue.get()
            except Exception as e:
                raise e
        else:
            raise StopIteration()

    def receive_sample(self, sample):
        self.sampleQueue.put(sample)

    def stop(self):
        self._stop = True
        return self.genManager.stop(self.id)


class LocalGeneratorManager(object):
    def __init__(self, controller):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))

        self.controller = controller
        self.generatorIdGen = 0
        self.generators = []

    def generate_new_generator_id(self):
        self.generatorIdGen = self.generatorIdGen + 1
        return self.generatorIdGen

    def _receive(self, msg):
        node_uuid = msg["node_uuid"]
        generator_id = msg["rule_id"]
        sample = msg["msg"]

        myGenerator = None
        for generator in self.generators:
            if generator_id == generator.id:
                myGenerator = generator
                break

        if myGenerator:
            myGenerator.receive_sample(sample)


    def start(self, event, pktMatch=None, selector=None, filters=[], match=None):
        self.log.debug("Adding new rule to node".format())

        generator = {"event":event, "pktMatch":pktMatch, "selector":selector, "filters":filters, 
                "match":match, "action":None, "permanence":Permanance.PERSISTENT, "notify_ctrl":True, "generator":True}

        generator_id = self.controller.blocking(True).mgmt.add_rule(generator)
        descriptor = LocalGeneratorDescriptor(self, generator_id, event, filters, match)
        self.generators.append(descriptor)

        return descriptor


    def stop(self, generatorId):
        self.log.debug("Stop generator with id: {}".format(generatorId))

        myGenerator = None
        for generator in self.generators:
            if generatorId == generator.id:
                myGenerator = generator
                break

        if myGenerator:
            self.generators.remove(myGenerator)
            del myGenerator

        retVal = self.controller.blocking(True).mgmt.delete_rule(generatorId)
        return retVal