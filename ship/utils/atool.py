"""

 Summary:
    Contains the ATool class an interface that all tools (i.e. file loaders, 
    etc) should inherit.

    This was a integral part of these tools when they were written in Java
    as they allowed the user interface to communicate with the tools through
    an observer. In Python it's not needed because of the signal slot
    mechanism making everything a lot easier.

    The interface is kept partly because it may still be useful and partly
    because I'm sure there will be a need to have all similar tools grouped
    at some point.

 Author:  
     Duncan Runnacles

  Created:  
     01 Apr 2016

 Copyright:  
     Duncan Runnacles 2016

 TODO:

 Updates:

"""


from abc import ABCMeta, abstractmethod

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class ATool(object):
    """Abstract base class for all tools.

    Any class that functions as a tool for processing the files etc should
    implement this.

    Note:
        This is not currently used in any part of the software at the moment.
        It was needed in the original Java implementation in order to allow
        tools to talk to the Gui through an aobserver interface.

        It is here in case it's needed but it is probably unnecessary because
        of the signal-slot mechanism of the Qt library which makes this kind
        of thing very simple.

        Re-visit whether an Observer pattern is required once we have some
        threading setup. Although Qt does that all so well I very much 
        doubt that this interface is required.
    """

    __metaclass__ = ABCMeta

    def init(self, observer=None):
        """Constructor.

        Takes in an instance of an observer to register it. 

        Args:
            observer(object): the class that want to be notified.
        """
        # A collection of the Observer object passed to the
        # concrete class.
        self.observers = []
        self.registerObserver(observer)

    def registerObserver(self, observer):
        """Add an observer to the collection of observers in the list.

        Args:
            observer(object): object to add to the observer list 
        """
        self.observers.append(observer)

    def unregisterObserver(self, o):
        """Remove an observer from the list of observers.

        Args:
            o (object): an object that no longer wants to be notified. 
        """
        self.observers.remove(o)

    def notifyObserversProgress(self, progress):
        """Notify all the current observers of a progress update"""
        for o in self.observers:
            o.updateObserver(progress)

    def updateObserversTotal(self, progress):
        """Notify all of the current observers of what we expect the total
        progress to be.

        Args:
            progress (int): The total progress expected.
        """
        for o in self.observers:
            o.updateObserverTotal(progress)

    def notifyObserversProgressName(self, name):
        """Notify all Observers of the name of the current progress.

        This name may also be a description. It is used to display on the 
        user interface to tell users what is happening when this tools is
        called.

        Args:
            name (str): the name of the progress.
        """
        for o in self.observers:
            o.updateObserverProcessName(name)
