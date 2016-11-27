"""

 Summary:
    Contains the AUnit, CommentUnit, HeaderUnit and UnknownSection 
    classes.
    The AUnit is an abstract base class for all types of Isis unit read
    in through the ISIS data file. All section types that are built should
    inherit from the AUnit baseclass.

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

import hashlib
import uuid
import random
import copy
# from abc import ABCMeta, abstractmethod

from ship.fmp.datunits import ROW_DATA_TYPES as rdt
from ship.datastructures import DATA_TYPES as dt
from ship.fmp.headdata import HeadDataItem

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""

    
class AUnit(object): 
    """Abstract base class for all Dat file units.
    
    This class must be inherited by all classes representing an isis
    data file unit (such as River, Junction, Culvert, etc).
    
    Every subclass should override the readUnitData() and getData() methods to 
    ensure they are specific to the setup of the individual units variables.
    If they are not overridden this class will simply take the data and store it
    as read and provide it back in the same state.
    
    All calls from the client to these classes should create the object and then
    call the readUnitData() method with the raw data.
    
    There is an UknownSection class at the bottom of this file that can be used 
    for all parts of the isis dat file that have not had a class defined. It just
    calls the basic read-in read-out methods from this class and understands nothing
    about the structure of the file section it is holding.     
    
    See Also:
        UnknownSection
    """
#     __metaclass__ = ABCMeta
        
    
    def __init__(self, **kwargs):
        """Constructor
        
        Set the defaults for all unit specific variables.
        These should be set by each unit at some point in the setup process.
        E.g. RiverUnit would set type and UNIT_CATEGORY at __init__() while name
        and data_objects are set in the readUnitData() method.
        Both of these are called at or immediately after initialisation.
        """
        
        self._name = 'unknown'                   # Unit label
        self._name_ds = 'unknown'                # Unit downstream label
        
        self._data = None                       
        """This is used for catch-all data storage.
        
        Used in units such as UnknownSection.
        Classes that override the readUnitData() and getData() methods are
        likely to ignore this variable and use row_collection and head_data instead.
        """
        
        self._unit_type = 'Unknown'
        """The type of ISIS unit - e.g. 'River'"""

        self._unit_category = 'Unknown'
        """The ISIS unit category - e.g. for type 'Usbpr' it would be 'Bridge'"""
        
        self.row_data = {} 
        """Collection containing all of the ADataRow objects.
        
        This is the main collection for row data in any unit that contains it.
        In a RiverUnit, for example, this will hold the RowDataObject's 
        containing the CHAINAGE, ELEVATION, etc.
        """
        self.head_data = {}
        """Dictionary containing set values that are always present in the file.
        
        In a RiverUnit this includes values like slope and distance. I.e.
        values that appear in set locations, usually at the top of the unit
        data in the .dat file.
        """
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
    
    @property
    def name_ds(self):
        return self._name_ds
    
    @name_ds.setter
    def name_ds(self, value):
        self._name_ds = value
        
    @property
    def has_ics(self):
        if not self.icLabels():
            return False
        else:
            return True
    
    @property
    def has_row_data(self):
        if not self.row_data:
            return False
        else:
            return True
    
    @property
    def unit_type(self):
        return self._unit_type
 
    @property
    def unit_category(self):
        return self._unit_category

    
    def icLabels(self):
        """Returns the initial_conditions values for this object.
        
        This method should be overriden by all classes that contain intial
        conditions.
        
        For example a BridgeUnit type will have two initial conditions labels;
        the upstream and downstream label names.
        
        By default this will return an empty list.
        
        Return:
            list - of intial condition label names.
        """
        return [] 
        
    def copy(self):
        """Returns a copy of this unit with it's own memory allocation."""
        object_copy = copy.deepcopy(self)
        return object_copy
    
    
    def rowDataObject(self, key, rowdata_key='main'):
        """Returns the row data object as a list.
 
        This will return the row_collection data object referenced by the key
        provided in list form.
 
        If you intend to update the values you should use getRowDataObject
        instead as the data provided will be mutable and therefore reflected in
        the values held by the row_collection. If you just want a quick way to
        loop through the values in one of the data objects  and only intend to
        read the data then use this.
         
        Args:
            key (int): the key for the data object requested. It is best to use 
               the class constants (i.e. RiverUnit.CHAINAGE) for this.
            rowdata_key(str): key to a RowDataCollection in row_data.
         
        Returns:
            List containing the data in the DataObject that the key points
                 to. Returns false if there is no row collection.
         
        Raises:
            KeyError: If key or rowdata_key don't exist.
        """
        if not self.has_row_data: return None
        return self.row_data[rowdata_key].dataObject(key)
    

    def row(self, index, rowdata_key='main'):
        """Get the data vals in a particular row by index.
         
        Args:
            index(int): the index of the row to return.
             
        Return:
            dict - containing the values for the requested row.
        """
        if not self.has_row_data: return None
        return self.row_data[rowdata_key].rowAsDict(index)
    
     
    def getData(self): 
        """Getter for the unit data.
  
        Return the file geometry data formatted ready for saving in the style
        of an ISIS .dat file
          
        Note:
            This method should be overriden by the sub class to restore the 
            data to the format required by the dat file.
          
        Returns:
            List of strings - formatted for writing to .dat file.
        """
        raise NotImplementedError
    

    def readUnitData(self, data, file_line, **kwargs):
        """Reads the unit data supplied to the object.
        
        This method is called by the IsisUnitFactory class when constructing the
        Isis  unit based on the data passed in from the dat file.
        The default hook just copies all the data parsed in the buildUnit() 
        method of the factory and aves it to the given unit. This is exactly
        what happens for the UnknownUnit class that just maintains a copy of the
        unit data exactly as it was read in.
        
        Args:
            data (list): raw data for the section as supplied to the class.

        Note:
            When a class inherits from AUnit it should override this method 
            with unit specific load behaviour. This is likely to include: 
            populate unit specific header value dictionary and in some units 
            creating row data object.
        
        See Also: 
            RiverSection for an example of overriding this method with a 
                concrete class. 
              
        """ 
        self.head_data['all'] = data
        
    
    def deleteRow(self, index, rowdata_key='main'):
        """Removes a data row from the RowDataCollection.
        """
        if index < 0 or index >= self.row_data[rowdata_key].numberOfRows():
            raise IndexError ('Given index is outside bounds of row_data[rowdata_key] data')
        
        self.row_data[rowdata_key].deleteRow(index)
        
    
    def updateRow(self, row_vals, index, rowdata_key='main'):
        """
        """
        if index >= self.row_data[rowdata_key].numberOfRows():
            raise IndexError ('Given index is outside bounds of row_collection data')
        
        # Call the row collection add row method to add the new row.
        self.row_data[rowdata_key].updateRow(row_vals=row_vals, index=index)
            
    
    def addRow(self, row_vals, rowdata_key='main', index=None):
        """Add a new data row to one of the row data collections.
        
        Provides the basics of a function for adding additional row dat to one
        of the RowDataCollection's held by an AUnit type.
        
        Checks that key required variables: ROW_DATA_TYPES.CHAINAGE amd 
        ROW_DATA_TYPES.ELEVATION are in the kwargs and that inserting chainge in
        the specified location is not negative, unless check_negatie == False.
        
        It then passes the kwargs directly to the RowDataCollection's
        addNewRow function. It is the concrete class implementations 
        respnsobility to ensure that these are the expected values for it's
        row collection and to set any defaults. If they are not as expected by
        the RowDataObjectCollection a ValueError will be raised.
        
        Args:
            row_vals(dict): Named arguments required for adding a row to the 
                collection. These will be as stipulated by the way that a 
                concrete implementation of this class setup the collection.
            rowdata_key='main'(str): the name of the RowDataCollection
                held by this to add the new row to. If None it is the
                self.row_collection. Otherwise it is the name of one of the
                entries in the self.additional_row_collections dictionary.
            index=None(int): the index in the RowDataObjectCollection to insert
                the row into. If None it will be appended to the end.
        """
        # If index is >= record length it gets set to None and is appended
        if index is not None and index >= self.row_data[rowdata_key].numberOfRows():
            index = None
        
        if index is None:
            index = self.row_data[rowdata_key].numberOfRows()
        
        self.row_data[rowdata_key].addRow(row_vals, index)
        
    
    def checkIncreases(self, data_obj, value, index):
        """Checks that: prev_value < value < next_value.
        
        If the given value is not greater than the previous value and less 
        than the next value it will return False.
        
        If an index greater than the number of rows in the row_data it will
        check that it's greater than previous value and return True if it is.
        
        Note:
            the ARowDataObject class accepts a callback function called
            update_callback which is called whenever an item is added or
            updated. That is how this method is generally used.

        Args:
            data_obj(RowDataObject): containing the values to check against.
            value(float | int): the value to check.
            index=None(int): index to check ajacent values against. If None
                it will assume the index is the last on in the list.
        
        Returns:
            False if not prev_value < value < next_value. Otherwise True.
        """
        details = self._getAdjacentDataObjDetails(data_obj, value, index)
        if details['prev_value']:
            if not value >= details['prev_value']:
                raise ValueError('CHAINAGE must be > prev index and < next index.')
        if details['next_value']:
            if not value <= details['next_value']:
                raise ValueError('CHAINAGE must be > prev index and < next index.')
    
    
    def _getAdjacentDataObjDetails(self, data_obj, value, index):
        """Safely check the status of adjacent values in an ADataRowObject.
        
        Fetches values for previous and next indexes in the data_obj if they
        exist.
        
        Note value in return 'index' key will be the given index unless it was
        None, in which case it will be the maximum index.
        
        All other values will be set to None if they do not exist.
        
        Args:
            data_obj(RowDataObject): containing the values to check against.
            value(float | int): the value to check.
            index=None(int): index to check ajacent values against. If None
                it will assume the index is the last on in the list.
        
        Return:
            dict - containing previous and next values and indexes, as well as
                the given index checked for None.
        
        """
        prev_value = None
        next_value = None
        prev_index = None
        next_index = None
        if index is None:
            index = data_obj._max

        if index < 0:
            raise ValueError('Index must be > 0')
        if index > 0: 
            prev_index = index - 1
            prev_value = data_obj[prev_index]
        if index < data_obj._max: 
            next_index = index + 1
            next_value = data_obj[next_index]

        retvals = {'index': index,
                   'prev_value': prev_value, 'prev_index': prev_index, 
                   'next_value': next_value, 'next_index': next_index}
        return retvals


    
class UnknownUnit(AUnit):
    """ Catch all section for unknown parts of the .dat file.
    
    This can be used for all sections of the isis dat file that have not had
    a unit class constructed.

    It has no knowledge of the file section that it contains and will store it 
    without altering it's state and return it in exactly the same format that it
    received it.

    This class is designed to be a fall-back class for any parts of the dat file
    for which it is deemed unnecessary to deal with more carefully.

    It has a 'Section' suffix rather that 'Unit' which is the naming convention
    for the other unit objects because it is not necessarily a single unit. It
    could be many different units. 
    
    It is created whenever the DatLoader finds
    parts of the dat file that it doesn't Know how to load (i.e. there is no
    *Unit defined for it. It will then put all the dat file data in one of these
    until it reaches a part of the file that it does recognise.
    """
    FILE_KEY = 'UNKNOWN'
    FILE_KEY2 = None
     
    def __init__ (self, **kwargs): 
        """Constructor.
        """
        AUnit.__init__(self, **kwargs) 
        self._unit_type = 'unknown'
        self._unit_category = 'unknown'
        self._name = 'unknown_' + str(hashlib.md5(str(random.randint(-500, 500)).encode()).hexdigest()) # str(uuid.uuid4())
    

    def getData(self):
        return self.head_data['all']
    

    def readUnitData(self, data):
        self.head_data['all'] = data


class CommentUnit(AUnit):
    """Holds the data in COMMENT sections of the .dat file.
    
    This is very similar to the UnknownSection in that all it does is grab the
    data between the comment tags and save it. It then prints out the same data
    in the same format with the COMMENT tags around it.
    """
    # Class constants
    UNIT_TYPE = 'comment'
    UNIT_CATEGORY = 'meta'
    FILE_KEY = 'COMMENT'
    FILE_KEY2 = None
       

    def __init__(self, **kwargs):
        """Constructor.
        """
        AUnit.__init__(self, **kwargs) 
        
        text = kwargs.get('text', '')
        self._unit_type = CommentUnit.UNIT_TYPE
        self._unit_category = CommentUnit.UNIT_CATEGORY
        self._name = 'comment_' + str(hashlib.md5(str(random.randint(-500, 500)).encode()).hexdigest()) # str(uuid.uuid4())
        self.has_datarows = True
        self.data = []
        if not text.strip() == '': self.addCommentText(text)
        
    
    def addCommentText(self, text):
        text = text.split('\n')
        self.no_of_rows = int(len(self.data) + len(text))
        for t in text:
            self.data.append(t.strip())
     
    def readUnitData(self, data, file_line):
        """
        """
        file_line += 1
        line = data[file_line]
        self.no_of_rows = int(data[file_line].strip())
        file_line += 1
        for i in range(file_line, file_line + self.no_of_rows):
            self.data.append(data[file_line].strip())
            file_line += 1

        return file_line -1 
    
    def getData(self):
        """
        """
        output = []
        output.append('{:<10}'.format('COMMENT'))
        output.append('{:>10}'.format(self.no_of_rows))
        for d in self.data:
            output.append(d)
        
        if len(output) > self.no_of_rows + 2:
            output = output[:self.no_of_rows + 2]
        
        return output


class HeaderUnit(AUnit):
    """This class deals with the data file values at the top of the file.
    
    
    These contain the global variables for the model such as water temperature,
    key matrix coefficients and the total number of nodes.
    
    There is only ever one of these units in every dat file - at the very top -
    so it seems convenient to put it in this module.
    """
    # Class constants
    UNIT_TYPE = 'header'
    UNIT_CATEGORY = 'meta'
    FILE_KEY = 'HEADER'
    FILE_KEY2 = None
    

    def __init__(self, **kwargs):
        """Constructor.
        """
        AUnit.__init__(self, **kwargs)
        self._unit_type = HeaderUnit.UNIT_TYPE
        self._unit_category = HeaderUnit.UNIT_CATEGORY
        self._name = 'header'
        self.head_data = {
            'name': HeadDataItem('', '', 0, 0, dtype=dt.STRING),
            'revision': HeadDataItem('1', '{:>10}', 1, 0, dtype=dt.STRING),
            'node_count': HeadDataItem(0, '{:>10}', 2, 0, dtype=dt.INT),
            'fr_lower': HeadDataItem(0.750, '{:>10}', 2, 1, dtype=dt.FLOAT, dps=3),
            'fr_upper': HeadDataItem(0.900, '{:>10}', 2, 2, dtype=dt.FLOAT, dps=3),
            'min_depth': HeadDataItem(0.100, '{:>10}', 2, 3, dtype=dt.FLOAT, dps=3),
            'direct_method': HeadDataItem(0.001, '{:>10}', 2, 4, dtype=dt.FLOAT, dps=3),
            'unknown': HeadDataItem('12SI', '{:>10}', 2, 5, dtype=dt.STRING), 
            'water_temp': HeadDataItem(10.000, '{:>10}', 3, 0, dtype=dt.FLOAT, dps=3),
            'flow': HeadDataItem(0.010, '{:>10}', 3, 1, dtype=dt.FLOAT, dps=3),
            'head': HeadDataItem(0.010, '{:>10}', 3, 2, dtype=dt.FLOAT, dps=3),
            'math_damp': HeadDataItem(0.700, '{:>10}', 3, 3, dtype=dt.FLOAT, dps=3),
            'pivot': HeadDataItem(0.100, '{:>10}', 3, 4, dtype=dt.FLOAT, dps=3),
            'relax': HeadDataItem(0.700, '{:>10}', 3, 5, dtype=dt.FLOAT, dps=3),
            'dummy': HeadDataItem(0.000, '{:>10}', 3, 6, dtype=dt.FLOAT, dps=3), 
            'roughness': HeadDataItem('', '{:>10}', 5, 0, dtype=dt.STRING), 
        }
            
    
    def readUnitData(self, unit_data, file_line): 
        """Reads the given data into the object.
        
        Args:
            unit_data (list): The raw file data to be processed.
        """
        self.head_data = {
            'name': HeadDataItem(unit_data[0].strip(), '', 0, 0, dtype=dt.STRING),
            'revision': HeadDataItem(unit_data[1].strip(), '{:>10}', 1, 0, dtype=dt.STRING),
            'node_count': HeadDataItem(unit_data[2][:10].strip(), '{:>10}', 2, 0, dtype=dt.INT),
            'fr_lower': HeadDataItem(unit_data[2][10:20].strip(), '{:>10}', 2, 1, dtype=dt.FLOAT, dps=3),
            'fr_upper': HeadDataItem(unit_data[2][20:30].strip(), '{:>10}', 2, 2, dtype=dt.FLOAT, dps=3),
            'min_depth': HeadDataItem(unit_data[2][30:40].strip(), '{:>10}', 2, 3, dtype=dt.FLOAT, dps=3),
            'direct_method': HeadDataItem(unit_data[2][40:50].strip(), '{:>10}', 2, 4, dtype=dt.FLOAT, dps=3),
            'unknown': HeadDataItem(unit_data[2][50:60].strip(), '{:>10}', 2, 5, dtype=dt.STRING), 
            'water_temp': HeadDataItem(unit_data[3][:10].strip(), '{:>10}', 3, 0, dtype=dt.FLOAT, dps=3),
            'flow': HeadDataItem(unit_data[3][10:20].strip(), '{:>10}', 3, 1, dtype=dt.FLOAT, dps=3),
            'head': HeadDataItem(unit_data[3][20:30].strip(), '{:>10}', 3, 2, dtype=dt.FLOAT, dps=3),
            'math_damp': HeadDataItem(unit_data[3][30:40].strip(), '{:>10}', 3, 3, dtype=dt.FLOAT, dps=3),
            'pivot': HeadDataItem(unit_data[3][40:50].strip(), '{:>10}', 3, 4, dtype=dt.FLOAT, dps=3),
            'relax': HeadDataItem(unit_data[3][50:60].strip(), '{:>10}', 3, 5, dtype=dt.FLOAT, dps=3),
            'dummy': HeadDataItem(unit_data[3][60:70].strip(), '{:>10}', 3, 6, dtype=dt.FLOAT, dps=3), 
            'roughness': HeadDataItem(unit_data[5].strip(), '{:>10}', 5, 0, dtype=dt.STRING), 
        }
        
        return file_line + 7
        
        
    def getData(self):
        """ Getter for the formatted data to write back to the .dat file.
        
        Returns:
            List - data formatted for writing to the new dat file.
        """
        out = []
        key_order = ['name', 'revision', 'node_count', 'fr_lower', 'fr_upper', 'min_depth',
                     'direct_method', 'unknown', 'water_temp', 'flow', 'head',
                     'math_damp', 'pivot', 'relax', 'dummy']
        for k in key_order:
            out.append(self.head_data[k].format(True))
        out = ''.join(out).split('\n')
        
        out.append('RAD FILE')
        out.append(self.head_data['roughness'].format())
        out.append('END GENERAL')
                        
        return out
        