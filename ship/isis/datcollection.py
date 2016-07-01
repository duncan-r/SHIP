"""

 Summary:
    Contains the convenience collection pattern UnitCollection.
    This is used to hold all of the isisunit objects loaded from the dat
    file.
    Provides convenience methods for retrieving units and getting key 
    meta-data on the units held in this collection.

 Author:  
     Duncan Runnacles

 Created:  
     01 Apr 2016

 Copyright:  
     Duncan Runnacles 2016

 TODO:

 Updates:


"""


import os

from ship.isis.datunits.isisunit import AIsisUnit
from ship.utils import filetools as ft

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class DatCollection(object):
    """Collection of isisunit type classes.
    
    This is a sort of composite/facade for all of the isisunit concrete 
    classes loaded.

    Each unit that is loaded is added to this class. They can then be accessed
    through the convenience methods outlined here.
    """
    FULL_PATH, DIRECTORY, FILENAME, FILENAME_AND_EXTENSION = range(4)
    
    def __init__(self, path_holder):
        """Constructor.

        Setup the list that will hold the units.
        
        Args:
            path_holder (PathHolder): object containing the references to the
                file path details of the .dat file.
        
        See Also:
            PathHolder class.
        """
        self.units = []
        self.path_holder = path_holder
        self._min = 0
        self._max = len(self.units)
        self._current = 0
    
    
    def __iter__(self):
        """Return an iterator for the units list"""
        return iter(self.units)
    
    
    def __next__(self):
        """Iterate to the next unit"""
        if self._current > self._max or self._current < self._min:
            raise StopIteration
        else:
            self._current += 1
            return self.units[self._current]
    
    
    def __getitem__(self, key):
        """Gets a value from units using index notation.
        
        Returns:
            contents of the units element at index.
        """
        return self.units[key]
    

    def __setitem__(self, key, value):
        """Sets a value using index notation
        
        Calls the setValue() function to do the hard work.
        
        Args:
            key (int): index to update.
            value: the value to add to the units.
        """
        self.units[key] = value


    def addUnit(self, isisUnit, index=None):
        """Adds a new isisunit type to the collection.
        
        Be aware that you will almost always want to provide an index. At the
        moment when no index is provided the unit will be appended to the end
        of the units list. This works fine when loading a dat file, but once
        the dat file is loaded any new units will be appended to the end (i.e.
        after the initial conditions etc). This behaviour may be improved later,
        but for now, unless you are building a dat file from scratch, always
        provide an index.
        
        Args:
            isisUnit (AIsisInit): The instance to add to the collection. 
            index=None(int): Index to insert the unit at.
        
        Raises:
            AttributeError: When a non-isisunit type is given.
            IndexError: If the given index doesn't exist. 
        """
        if not isinstance(isisUnit, AIsisUnit):
            raise AttributeError ('Given isisunit is not of type AIsisUnit')
        
        if index == None:
            self.units.append(isisUnit)
        else:
            if index < len(self.units):
                self.units.insert(index, isisUnit)
            else:
                raise IndexError

        self._max = len(self.units)

    
    def removeUnit(self, name_key):
        """Remove one of the units previously added to the list.
        
        Args:
            name_key (str): The unique name of the unit to remove. 
        
        Raises:
            KeyError: if the name doesn't exist. 
        """
        for u in self.units:
            if name_key == u.name:
                self.units.remove(u)
                self._max = len(self.units)
                return True
            else:
                return False
    
    
    def getIndex(self, unit, unit_type=None):
        """Get the index a particular AIsisUnit in the collection.
        
        Either the unit itself or its name can be provided as the argument.
        
        If a name is supplied a unit_type should also be given. This is because 
        some units can have the same name (e.g. river and refh) and it is not
        possible to know which one to return with the name alone. If no unit_type
        is given the first unit with the matching name will be returned.
        
        Args:
            unit(AIsisUnit or str): the AIsisUnit or the name of the AIsisUnit
                to find the index for.
            unit_type=None(str): the unit_type member of the AIsisUnit (e.g. 
                for a USBPR bridge the category == Bridge and unit_type == 'Usbpr').
        
        Return:
            int - the index of the given unit, or -1 if it could not be found.
        """
        index = -1
        if isinstance(unit, AIsisUnit):
            index = self.units.index(unit)
        elif isinstance(unit, basestring):
            for i, u in enumerate(self.units):
                if u.name == unit:
                    if unit_type == u.unit_type:
                        index = i
                        break
                    elif unit_type is None:
                        index = i
                        break
        else:
            index = -1
        
        return index
        
        
    def getPrintableContents(self):
        """Get the formatted contents of each isisunit in the collection.
        
        Iterates through each of the units in the collection and
        calls their getData() method.
        
        Returns:
            List containing all lines for each unit formatted for printing
                out to the dat file.
        """
        out_data = []
        logger.debug('Returning printable unit data')

        # For each unit call the isisunit object and ask it
        # for its .DAT file formatted text to save to file
        for u in self.units:
            logger.debug('Section Type: ' + u.getUnitType())
            out_data.extend(u.getData())
        
        return out_data
    
    
    def write(self, filepath=None):
        """Write the contents of this file to disk.
        
        Writes out to file in the format required for reading by ISIS/FMP.
        
        Note:
            If a filepath is not provided and the settings in this objects
            PathHolder class have not been updated you will write over the
            file that was loaded.
        
        Args:
            filepath=None(str): if a filename is provided it the file will be
                written to that location. If not, the current settings in this
                object path_holder object will be used.
        
        Raises:
            IOError - If unable to write to file.
        """
        if filepath is None:
            filepath = self.path_holder.getAbsolutePath()
            
        contents = self.getPrintableContents()
        ft.writeFile(contents, filepath)
        
    
    def getUnitsByCategory(self, category_key):
        """Return all the units in the requested category.
        
        Iterate through the collection and get all of the different categories
        within the model.
        
        Categories are defined by the AIsisUnits. For example:
        USBPR and Arch bridge units are different, but both will be 
        categorised as 'bridge'.
        
        Args:
            category_key (str): The unit_category variable defined in the unit. 
        
        Returns:
            List containing all the specified category of unit in the model or
                False if there are none of the category in the 
                collection.
        """
        types = [] 
        for u in self.units:
            if u.unit_category == category_key:
                types.append(u)
        
        return types
    
    
    def getUnitsByType(self, type_key):
        """Return all of the units of the requested type.
        
        Iterate through the collection and get all of the different unit types 
        within the model.
        
        Types are set by the isisunit subclasses. They differentiate the
        from categories by providing further definition. For example:
        USBPR and ARCH bridges would both be returned in the same category,
        but on ARCH bridges would be return using the ArchBridgeUnit.TYPE.
        
        Note:
            Use the class constants in the isisunit classes as the type key
        
        See Also:
            isisunit.
        
        Return:
            List of the specified unit type.
        """
        types = [] 
        for u in self.units:
            if u.unit_type == type_key:
                types.append(u)
        
        return types
    
    
    def getAllUnits(self): 
        """Get all of the isisunit in the collection
        
        Warning:
            Don't use this it is being deprecated and will probably be 
                removed in a later release.
                
        Returns:
            list of isisunit objects
            
        TODO:
            Remove this function it can be accessed through the variables or
            by setting up a property if needed.
        """
        return self.units
    
    
    def getUnit(self, key, unit_type=None):
        """Fetch a unit from the collection by name.
        
        Each isisunit in the collection is guaranteed to have a unique id.
        You can access the unit if you know it's ID. The ID is the 
        AIsisUnit.name variable.
        
        Sometimes different units can have the same name (e.g. RefhUnit and
        RiverUnit). This function will always return the first unit it finds.
        To avoid this you can specifiy an AIsisUnit.UNIT_TYPE to retrieve::
            >>> getUnit(river.name, river.UNIT_TYPE)

        Args:
            name_key (str): name of the unit.
            unit_type=None(str): the AIsisUnit.TYPE to find.
        
        Returns:
            isisunit object corresponding to the given name, or False
                if the name doesn't exist.
        """
        for u in self.units:
            if u.name == key:
                if unit_type == None:
                    return u
                elif not u.UNIT_TYPE == unit_type:
                    continue
                else:
                    return u
        else:
            return False
        
    
    def setUnit(self, unit, unit_type=None):
        """Replace the contents of a certain unit with the given one.
        
        Each isisunit has a .name variable. The name of the unit will be 
        checked against the collection. If the name is found within the
        collection that unit will be replaced with the given one. If no
        matching name is found it will return False.
        
        Sometimes different units can have the same name (e.g. RefhUnit and
        RiverUnit). This function will always set the first unit it finds.
        To avoid this you can specifiy an AIsisUnit.UNIT_TYPE to retrieve::
            >>> getUnit(river.name, river.UNIT_TYPE)

        Args:
            name_key (str): name of the unit.
            unit_type=None(str): the AIsisUnit.TYPE to find.
        
        Returns:
            True if the unit was successfully updated. False if the unit does 
            not have a name variable set. False if the unit name doesn't match 
            any in the collection.
        """
        try:
            name = unit.name
        except NameError:
            logger.error('Provided AIsisUnit does not have a name variable - Data Corruption!')
            raise
        
        for i, u in enumerate(self.units, 0):
            if u.name == unit.name:
                self.units[i] = unit
                return True
        
        return False
        
        
    def getNoOfUnits(self): 
        """The number of units currently held in the collection.
        
        Returns:
            Int Units in the collection.
        """
        return len(self.units)
    
   
   
    