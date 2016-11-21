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

from __future__ import unicode_literals

import os
from datetime import datetime

from ship.isis.datunits.isisunit import AIsisUnit
from ship.utils import filetools as ft
from ship.isis.datunits import ROW_DATA_TYPES as rdt
from ship.isis.datunits.isisunit import CommentUnit
from ship.isis import isisunitfactory as iuf

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
        self._ic_index  = -999 # DON'T MESS WITH THIS!
        self._gis_index = -999 # DON'T MESS WITH THIS!
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


    def addUnit(self, unit, index=None, **kwargs):#update_node_count=True, ics={}):
        """Adds a new isisunit type to the collection.
        
        If the index value provided is greater than the index of the 
        InitialConditions unit the unit will be added before the IC unit. This
        is the last slot in the ordering of the units in the dat file.

        Accepts ``**kwargs``:

            update_node_count(bool): if True will update the node count
                value at the top of the .dat file. You probably want to do this.
                if missing it will default to True
            ics(dict): inital conditions to add for the unit being put in the
                collection. If missing the default values will be applied.
                These will only be applied if the unit supports initial conditions.
        
        Args:
            unit (AIsisInit): The instance to add to the collection. 
            index=None(int): Index to insert the unit at.
        
        Raises:
            AttributeError: When a non-isisunit type is given.
        """
        if not isinstance(unit, AIsisUnit):
            raise AttributeError ('Given unit is not of type AIsisUnit')
        
        update_node_count = kwargs.get('update_node_count', True)
        ics = kwargs.get('ics', {})
        
        '''
            Treat initial_conditions, gis_info and header a little differently.
            They are always at the top and bottom af the file.
        '''
        if unit._unit_type == 'header' or unit._unit_type == 'gis_info' or \
                                          unit._unit_type == 'initial_conditions':
            if unit._unit_type == 'header':
                if self.units and self.units[0]._unit_type == 'header':
                    self.units[0] = unit
                else:
                    self.units.insert(0, unit)
            
            elif unit._unit_type == 'gis_info':
                if self._gis_index == -999:
                    self.units.append(unit)
                    self._gis_index = len(self.units) -1
                else:
                    self.units[self._gis_index] = unit

            else:
                # If it already exists in the collection
                if self._ic_index != -999:
                    self.units[self._ic_index] = unit
                else:
                    # If gis_info unit exists put it before that, otherwise it
                    # goes on the end
                    if self._gis_index == -999:
                        self.units.append(unit)
                        self._ic_index = len(self.units) -1
                    else:
                        self.units.insert(self._gis_index, unit)
                        self._ic_index = self._gis_index - 1

            self._max = len(self.units)
            return
    
        '''
            All the others.
        '''
        if index is None: index = len(self.units)

        # Check if we need to go in front of ic and gis end of file units
        if self._ic_index != -999 and index > self._ic_index:
            index = self._ic_index
        elif self._gis_index != -999 and index > self._gis_index:
            index = self._gis_index
        elif index > len(self.units):
            self.units.append(unit)
            index = None
        
        if index is not None:
            self.units.insert(index, unit)
            if self._ic_index != -999: self._ic_index += 1
            if self._gis_index != -999: self._gis_index += 1
        
        self._max = len(self.units)
        
        if not self._ic_index == -999 and update_node_count and unit.has_ics:
            header = self.units[0]
            temp = unit.icLabels()
            for name in unit.icLabels():
                ics[rdt.LABEL] = unit._name
                node_count = self.units[self._ic_index].addRow(ics, unit._unit_type)
                header.head_data['node_count'].value = node_count
            
    
#     def removeUnit(self, name_key, unit_type, update_node_count=True):
    def removeUnit(self, unit, unit_type=None, **kwargs):
        """Remove one of the units previously added to the list.

        Accepts ``**kwargs``:

            update_node_count(bool): if True will update the node count
                value at the top of the .dat file. You probably want to do this.
                if missing it will default to True
        
        Args:
            unit(str | AIsisUnit): Can either be the AIsisUnit.name or the
                AIsisUnit.
            unit_type=None(str): If unit is a name str this must be provided to 
                ensure that the correct unit is removed. E.g. a RiverUnit and 
                an RefhUnit can both have the same AIsisUnit.name value, but 
                different .unit_type's.
                If unit is an AIsisUnit this will be ignored.

        Raises:
            KeyError: if the name doesn't exist. 
        """
        update_node_count = kwargs.get('update_node_count', True)
        if isinstance(unit, AIsisUnit):
            index = self.index(unit, unit_type)
        else:
            index = self.index(unit)
            
        if index != -1:
            name = self.units[index]._name
            name_ds = self.units[index]._name_ds
            utype = self.units[index]._unit_type
            
            if update_node_count:
                ic = self.unit('initial_conditions')
                header = self.unit('header')
                for l in self.units[index].icLabels():
                    try:
                        ic.deleteRowByName(l, utype)
                    except KeyError:
                        logger.warning('No intitial conditions found for initial conditions label: ' + name)

            header.head_data['node_count'].value = ic.node_count
            del self.units[index]
            self._max = len(self.units)
            return True

        else:
            return False
                
                
#         
#         for u in self.units:
#             if u.name == name_key:
#                 if not u.UNIT_TYPE == unit_type:
#                     continue
#                 else:
#                     self.units.remove(u)
#                     self._max = len(self.units)
#                     if update_node_count:
#                         ic = self.getUnit('Initial Conditions')
#                         try:
#                             ic.deleteRowByName(u.name)
#                         except KeyError:
#                             logger.warning('No initial conditions found for unit %' % u.name)
#                         header = self.getUnit('Header')
#                         self.node_count = header.head_data['node_count'] = int(header.head_data['node_count']) - 1
#                     return True
#         
#         return False
    
    
#     def getIndex(self, unit, unit_type=None):
    def index(self, unit, unit_type=None):
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
                for a USBPR bridge the unit_category == Bridge and unit_type == 'Usbpr').
        
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
            logger.debug('Section Type: ' + u._unit_type)
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
        
    
#     def getUnitsByCategory(self, unit_keys):
    def unitsByCategory(self, unit_keys):
        """Return all the units in the requested unit(s).
        
        Iterate through the collection and get all of the different categories
        within the model.
        
        Categories are defined by the AIsisUnits. For example:
        USBPR and Arch bridge units are different, but both will be 
        categorised as 'bridge'.
        
        Args:
            unit_keys (str | []): The unit variables defined in 
                the unit. Can be either a string representing a single CATEGORY 
                of AIsisUnit or a list of strings for multiple types. 
        
        Returns:
            List containing all the specified CATEGORY of unit in the model or
                False if there are none of the CATEGORY in the 
                collection.
        """
        if isinstance(unit_keys, basestring):
            unit_keys = [unit_keys]

        types = [] 
        for u in self.units:
            if u.unit_category in unit_keys:
                types.append(u)
        
        return types
    
    
#     def getUnitsByType(self, type_keys):
    def unitsByType(self, type_keys):
        """Return all of the units of the requested type.
        
        Iterate through the collection and get all of the different unit types 
        within the model.
        
        Types are set by the isisunit subclasses. They differentiate the
        from categories by providing further definition. For example:
        USBPR and ARCH bridges would both be returned in the same UNIT_CATEGORY,
        but on ARCH bridges would be return using the ArchBridgeUnit.TYPE.
        
        Note:
            Use the class constants in the isisunit classes as the type key
        
        See Also:
            isisunit.

        Args:
            type_keys (str | []): The unit_type variables defined in 
                the unit. Can be either a string representing a single type 
                of AIsisUnit or a list of strings for multiple types. 
        
        Return:
            List of the specified unit type.
        """
        if isinstance(type_keys, basestring):
            type_keys = [type_keys]

        types = [] 
        for u in self.units:
            if u.unit_type in type_keys:
                types.append(u)
        
        return types
    
    
#     def getAllUnits(self):
    def allUnits(self): 
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
    
    
#     def getUnit(self, key, unit_type=None):
    def unit(self, key, unit_type=None):
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
        # Do a quick lookup on these as we know roughly where they are
        if key == 'initial_conditions':
            if self.units and self.units[-1]._unit_type == 'initial_conditions':
                return self.units[-1]
            elif len(self.units) > 1 and self.units[-2]._unit_type == 'initial_conditions':
                return self.units[-2]
            else:
                return False
        if key == 'header':
            if self.units and self.units[0]._unit_type == 'header':
                return self.units[0]
            else:
                return False
            
        for u in self.units:
            if u.name == key:
                if unit_type == None:
                    return u
                elif not u.unit_type == unit_type:
                    continue
                else:
                    return u
        else:
            return False
        
    
#     def setUnit(self, unit, unit_type=None):
    def setUnit(self, unit, unit_type):
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
            unit_type(str): the AIsisUnit.TYPE to find.
        
        Returns:
            True if the unit was successfully updated. False if the unit does 
            not have a name variable set. False if the unit name doesn't match 
            any in the collection.
        """
        try:
            name = unit._name
            utype = unit._unit_type
        except (NameError, AttributeError) as err:
            logger.error('Provided AIsisUnit does not have a name and/or unit_type variable - Data Corruption!')
            logger.exception(err)
            raise
        
        index = self.index(unit._name, unit._unit_type)
        self.units[index] = unit
        
        for i, u in enumerate(self.units, 0):
            if u.name == unit.name:
                self.units[i] = unit
                return True
        
        return False
        
        
#     def getNoOfUnits(self): 
    def noOfUnits(self): 
        """The number of units currently held in the collection.
        
        Returns:
            Int Units in the collection.
        """
        return len(self.units)
    

    @classmethod
    def initialisedDat(cls, dat_path, units=[]):
        """Create a new ISIS .dat file with basic header info and no units.
        
        Creates the equivelant of generating a new .dat unit in the software. The
        DatCollection returned can then be manipulated in the same way that any
        other one loaded from file would be.
        
        A single comment unit will be be added to the file stating that it was
        created by the SHIP library at timestamp.
        
        Args:
            dat_path(str): the path to set for the newly created .dat file.
            
        Return:
            DatCollection - setup as an empty ISIS .dat file.
        """
        contents = [
                '',
                '#REVISION#1',
                '         0     0.750     0.900     0.100     0.001        12SI',
                '    10.000     0.010     0.010     0.700     0.100     0.700     0.000',
                'RAD FILE',
                '',
                'END GENERAL'
                'INITIAL CONDITIONS',
                ' label   ?      flow     stage froude no  velocity     umode    ustate         z',
        ]

        path_holder = ft.PathHolder(dat_path)
        dat = cls(path_holder)
        factory = iuf.IsisUnitFactory()
        file_line, hunit = factory.createUnit(contents, 0, 'header', 0)
        file_line, icunit = factory.createUnit(contents, file_line, 'initialconditions', 1)
        cunit = CommentUnit('Created by SHIP library on %s' % datetime.now().strftime('%Y-%M-%d %H:%M'))
        dat.addUnit(hunit, update_node_count=False)
        dat.addUnit(cunit, update_node_count=False)
        dat.addUnit(icunit, update_node_count=False)
        for u in units:
            dat.addUnit(u)
        return dat
   
    