"""

 Summary:
    Contains the AIsisUnit, CommentUnit, HeaderUnit and UnknownSection 
    classes.
    The AIsisUnit is an abstract base class for all types of Isis unit read
    in through the ISIS data file. All section types that are built should
    inherit from the AIsisUnit baseclass.

 Author:  
     Duncan Runnacles

 Created:  
     01 Apr 2016

 Copyright:  
     Duncan Runnacles 2016

 TODO:

 Updates:

"""

import hashlib
import random
import copy
from abc import ABCMeta, abstractmethod

from ship.isis.datunits import ROW_DATA_TYPES as rdt

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class AIsisUnit( object ): 
    """Abstract base class for all Dat file units.
    
    This class must be inherited by all classes representing an isis
    data file unit (such as River, Juntion, Culvert, etc).
    
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
    __metaclass__ = ABCMeta
        
    
    def __init__(self):
        """Constructor
        """
        # Set the defaults for all unit specific variables.
        # These should be set by each unit at some point in the setup process.
        # E.g. RiverUnit would set type and category at __init__() while name
        # and data_objects are set in the readUnitData() method.
        # Both of these are called at or immediately after initialisation.
        
        self._name = 'Unknown'                   # Unit name
        
        # This is used for catch-all data storage, such as in the UnknownSection.
        # Classes that override the readUnitData() and getData() methods are
        # likely to ignore this variable and use row_collection and head_data instead.
        
        self._data = None                       # The unit geometry data
        self.unit_type = 'Unknown'              # The type of unit
        self.unit_category = 'Unknown'          # The category of unit
        
        # Needed when loading file. Does it have rows like river geometry or 
        # just a header?
        self.has_datarows = False      
        
        # Total number of row collections held by this file. If set to zero it
        # means the same as has_datarows = False. Set to one as default because
        # zero is dealt with by has_datarows and if that is set to True then
        # there must be at least 1 row_collection.
        self.no_of_collections = 1                           
        self.row_collection = None              # Collection containing all the 
                                                # row data objects
        # Other row data objects
        # If this is used it should be instanciated as an OrderedDict
        self.additional_row_collections = None  
                      
        self.head_data = None                   # Dictionary of unit header values.
        
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
        try:
            self.head_data['section_label'] = value
        except KeyError:
            return
    
    
    def getUnitVars(self): 
        """Getter for the unit variables needed for loading this Unit. 

        The IsisUnitFactory will call this to work out how to load the data
        from the .dat file.
        
        Returns:
            Dict - containing the data needed to read the Unit.
        
        Raises:
            ValueError: if the self.unit_vars variables has not been set
                by the concrete implementation of this class.
        """
        if self.unit_vars == None:
            logger.warning('No unit load variables set for %s' % (self.unit_type))
            raise ValueError ('No unit load variables set for %s' % (self.unit_type))
        return self.unit_vars
        

    # TODO: These are superflous methods. Need removing.
    def getName( self ): 
        """Getter for the name of the unit
        
        Warning:
            This is unecessary method and is deprecated. Please use the
            variable directly.
        
        Returns:
            str - The name of the unit
        """
        return self._name
        

    def getUnitType( self ):
        """Getter for the type of the unit.
        
        Warning:
            This is unecessary method and is deprecated. Please use the
            variable directly.
        
        Returns:
            str - The type of the unit
        """
        return self.unit_type
    

    def getUnitCategory(self):
        """Getter for the category of unit
        
        Warning:
            This is unecessary method and is deprecated. Please use the
            variable directly.
        
        Returns:
            str - The unit category
        """
        return self.unit_category
    
    
    def getDeepCopy(self):
        """Returns a copy of this unit with it's own memory allocation."""
        object_copy = copy.deepcopy(self)
        return object_copy
    
    
    def getRowDataObject(self, key, collection_key='main', copy=False):
        """Getter for the data series in the data_object dictionary.

        Depending on the data that the subclass contains this could be 
        anything... a dictionary a string a integer. It is up to the client 
        and the subclass to ensure that this is clear.
        
        Args:
            key (str): The key for the data_object requested.
            collection_key='main' (str): the key for the row_collection to 
                return. Most objects will only contain a single row_collection,
                like the RiverUnit, but some like bridges have opening data and
                orifice data rows as well. See individual AIsisUnit 
                implemenations for more details on what they contain.
        
        Returns:
            DataObject requested by client or False if unit has no rows.
        
        Raises:
            KeyError: If key does not exist. 
        """
        if not self.has_datarows:
            return False
        try:
            return self.row_collection.getDataObject(key)
        except KeyError:
            logger.warning('Key %s does not exist in collection' % (key))
            raise KeyError ('Key %s does not exist in collection' % (key))
    
    
    def getRowDataAsList(self, key, collection_key='main'):
        """Returns the row data object as a list.

        This will return the row_collection data object referenced by the key
        provided in list form.

        If you intend to update the values you should use getRowDataObject
        instead as the data provided will be mutable and therefore reflected in
        the values held by the row_collection. If you just want a quick way to
        loop through the values in one of the data objects  and only intend to
        read the data then use this.
        
        Args:
            key (str): the key for the data object requested. It is best to use 
               the class constants (i.e. RiverUnit.CHAINAGE) for this.
        
        Returns:
            List containing the data in the DataObject that the key points
                 to. Returns false if there is no row collection.
        
        Raises:
            KeyError: If key does not exist.
        """
        if not self.has_datarows:
            return False
        try:
            data_col = self.row_collection.getDataObject(key)
            vals = []
            for i in range(0, data_col.record_length):
                vals.append(data_col.getValue(i))
            return vals
        except KeyError:
            logger.warning('Key %s does not exist in collection' % (key))
            raise KeyError ('Key %s does not exist in collection' % (key))
    
    
    def getHeadData(self):
        """Returns the header data from this unit.

        This includes the details outlined at the top of the unit such as the
        unit name, labels, global variables, etc.
        for some units, such as HeaderUnit or Junctions this is all of the 
        data. Other units, such as the RiverUnit also have RowDataObjects.
        
        Returns:
            The header data for this unit or None if it hasn't been initialised.
        """
        return self.head_data


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
        return self.data
    

    def readUnitData(self, data, file_line=None):
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
            When a class inherits from AIsisUnit it should override this method 
            with unit specific load behaviour. This is likely to include: 
            populate unit specific header value dictionary and in some units 
            creating row data object.
        
        See Also: 
            RiverSection for an example of overriding this method with a 
                concrete class. 
              
        """ 
        self.data = data
        
    
    def updateDataRow(self, row_vals, index=None, collection_name=None,
                                                check_negative=True):
        """
        """
        if index >= self.row_collection.getNumberOfRows():
            raise IndexError ('Given index is outside bounds of row_collection data')
        
        # Check that there won't be a negative change in chainage across row.
        c = row_vals.get(rdt.CHAINAGE)
        if check_negative and not c is None:
            if self._checkChainageIncreaseNotNegative(index, 
                                        row_vals.get(rdt.CHAINAGE)) == False:
                logger.error('Chainage increase is negative')
                raise ValueError ('Chainage increase is negative')
        
        # Call the row collection add row method to add the new row.
        if collection_name is None:
            self.row_collection.updateRow(values_dict=row_vals, index=index)
        
        else:
            self.additional_row_collections[collection_name].updateRow(
                                        values_dict=row_vals, index=index)
            
    
    def addDataRow(self, row_vals, collection_name=None, index=None, 
                                                check_negative=True):
        """Add a new data row to one of the row data collections.
        
        Provides the basics of a function for adding additional row dat to one
        of the RowDataObjectCollection's held by an AIsisUnit type.
        
        Checks that key required variables: ROW_DATA_TYPES.CHAINAGE amd 
        ROW_DATA_TYPES.ELEVATION are in the kwargs and that inserting chainge in
        the specified location is not negative, unless check_negatie == False.
        
        It then passes the kwargs directly to the RowDataObjectCollection's
        addNewRow function. It is the concrete class implementations 
        respnsobility to ensure that these are the expected values for it's
        row collection and to set any defaults. If they are not as expected by
        the RowDataObjectCollection a ValueError will be raised.
        
        Args:
            row_vals(dict): Named arguments required for adding a row to the 
                collection. These will be as stipulated by the way that a 
                concrete implementation of this class setup the collection.
            collection_name=None(str): the name of the RowDataObjectCollection
                held by this to add the new row to. If None it is the
                self.row_collection. Otherwise it is the name of one of the
                entries in the self.additional_row_collections dictionary.
            index=None(int): the index in the RowDataObjectCollection to insert
                the row into. If None it will be appended to the end.
            check_negative=True(Bool): If True the value of CHAINAGE will be
                checked to see if it is less than the previous entry in the
                row collection. If it is a ValueError will be raised.
            
        """
        if not rdt.CHAINAGE in row_vals.keys() or not rdt.ELEVATION in row_vals.keys():
            logger.error('Required values of CHAINAGE and ELEVATION not given')
            raise  AttributeError ('Required values of CHAINAGE and ELEVATION not given') 
        
        chainage = row_vals.get(rdt.CHAINAGE)

        # If index is >= record length it gets set to None and is appended
        if index >= self.row_collection.getNumberOfRows():
            index = None
            
        # Check that there won't be a negative change in chainage across row.
        if check_negative and not self.row_collection.getNumberOfRows() == 0:
            if self._checkChainageIncreaseNotNegative(index, chainage) == False:
                logger.error('Chainage increase is negative')
                raise ValueError ('Chainage increase is negative')

        # Call the row collection add row method to add the new row.
#         try:
        if collection_name is None:
            self.row_collection.addNewRow(values_dict=row_vals, index=index)
        
        else:
            self.additional_row_collections[collection_name].addNewRow(
                                        values_dict=row_vals, index=index)
    
    
    def _checkChainageIncreaseNotNegative(self, index, chainageValue, 
                                                    collection_name=None):
        """Checks that new chainage value is not not higher than the next one.

        If the given chainage value for the given index is higher than the
        value in the following row ISIS will give a negative chainage error.

        It will return true if the value is the last in the row.
        
        Args:
            index (int): The index that the value is to be added at.
            chainageValue (float): The chainage value to be added.
        
        Returns:
           False if greater or True if less.
        """
        # If it's being added on the end only check the greater than bit
        if index == None:
            if collection_name is None:
                length = self.row_collection.getNumberOfRows()
                if length > 0:
                    if self.row_collection.getDataValue(rdt.CHAINAGE, length - 1) >= chainageValue:
                        return False
            else:
                length = self.additional_row_collections[collection_name].getNumberOfRows()
                if length > 0:
                    if self.additional_row_collections[collection_name].getDataValue(
                                        rdt.CHAINAGE, length - 1) >= chainageValue:
                        return False
            return True
        
        # Otherwise need to check that it's less than the next one too
        elif not index == 0:
            if collection_name is None:
                logger.debug('Previous index chainage:\t' + 
                    str(self.row_collection.getDataValue(rdt.CHAINAGE, index-1)))
                length = self.row_collection.getNumberOfRows()
                if length > 0:
                    temp = self.row_collection.getDataValue(rdt.CHAINAGE, index-1)
                    if self.row_collection.getDataValue(
                                    rdt.CHAINAGE, index - 1) >= chainageValue:
                        return False
                
                temp2 = self.row_collection.getDataValue(rdt.CHAINAGE, index)
                if self.row_collection.getDataValue(
                                rdt.CHAINAGE, index) <= chainageValue:
                    return False
                return True
            else:
                logger.debug('Previous index chainage:\t' + 
                    self.additional_row_collections[collection_name].getDataValue(
                                                        rdt.CHAINAGE, index-1))
                length = self.row_collection.getNumberOfRows()
                if length > 0:
                    if self.additional_row_collections[collection_name].getDataValue(
                                        rdt.CHAINAGE, index - 1) >= chainageValue:
                        return False
                if self.additional_row_collections[collection_name].getDataValue(
                                rdt.CHAINAGE, index) <= chainageValue:
                    return False
                return True
        
        # Only check if it's greater than the next value
        else:
            if collection_name is None:
                if self.row_collection.getDataValue(
                                rdt.CHAINAGE, index) <= chainageValue:
                    return False
            else:
                if self.additional_row_collections[collection_name].getDataValue(
                                rdt.CHAINAGE, index) <= chainageValue:
                    return False
            return True
            
        return True


    
class UnknownSection(AIsisUnit):
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
     
    def __init__ (self): 
        """Constructor.
        """
        AIsisUnit.__init__(self) 
        self.unit_type = 'Unknown'
        self.unit_category = 'Unknown'
        self._name = 'Unknown_' + str(hashlib.md5(str(random.randint(-500, 500)).encode()).hexdigest())
    


class CommentUnit(AIsisUnit):
    """Holds the data in COMMENT sections of the .dat file.
    
    This is very similar to the UnknownSection in that all it does is grab the
    data between the comment tags and save it. It then prints out the same data
    in the same format with the COMMENT tags around it.
    """
    # Class constants
    UNIT_TYPE = 'Comment'
    CATEGORY = 'Meta'
    FILE_KEY = 'COMMENT'
       

    def __init__(self):
        """Constructor.
        """
        AIsisUnit.__init__(self) 
        self.unit_type = 'Comment'
        self.unit_category = 'Meta'
        self._name = 'Comment_' + str(hashlib.md5(str(random.randint(-500, 500)).encode()).hexdigest())
        self.has_datarows = True
        self.data = []
    
        
    def readUnitData(self, data, file_line):
        """
        """
        self.no_of_rows = int(data[file_line+1].strip())
        for i in range(2, 2 + self.no_of_rows):
            self.data.append(data[file_line + i].strip())

        return file_line + self.no_of_rows
    
    def getData(self):
        """
        """
        output = []
        output.append('{:<10}'.format('COMMENT'))
        output.append('{:>10}'.format(self.no_of_rows))
        for d in self.data:
            output.append(d)
        
        if len(output) > self.no_of_rows + 1:
            output = output[:self.no_of_rows + 1]
        
        return output


class HeaderUnit(AIsisUnit):
    """This class deals with the data file values at the top of the file.
    
    
    These contain the global variables for the model such as water temperature,
    key matrix coefficients and the total number of nodes.
    
    There is only ever one of these units in every dat file - at the very top -
    so it seems convenient to put it in this module.
    """
    # Class constants
    UNIT_TYPE = 'Header'
    CATEGORY = 'Meta'
    FILE_KEY = 'HEADER'
    

    def __init__(self):
        """Constructor.
        """
        AIsisUnit.__init__(self)
        self.unit_type = 'Header'
        self.unit_category = 'Meta'
        self._name = 'Header'
        self.has_datarows = False
            
    
    def readUnitData(self, unit_data, file_line): 
        """Reads the given data into the object.
        
        Args:
            unit_data (list): The raw file data to be processed.
        """
        self.head_data = {'Name': unit_data[0].strip(), 
                             'Revision': unit_data[1].strip(), 
                             'node_count': unit_data[2][:10].strip(), 
                             'Fr_lower': unit_data[2][10:20].strip(), 
                             'Fr_Upper': unit_data[2][20:30].strip(),
                             'Min_depth': unit_data[2][30:40].strip(), 
                             'Direct_method': unit_data[2][40:50].strip(),
                             'Unknown': unit_data[2][50:60].strip(), 
                             'Water_temp': unit_data[3][:10].strip(),
                             'Flow': unit_data[3][10:20].strip(), 
                             'Head': unit_data[3][20:30].strip(), 
                             'Math_damp': unit_data[3][30:40].strip(),
                             'Pivot': unit_data[3][40:50].strip(),
                             'Relax': unit_data[3][50:60].strip(), 
                             'Dummy': unit_data[3][60:70].strip(),
                             'Roughness': unit_data[5].strip()
                             }
        self.node_count = int(self.head_data['node_count'])
        
        return file_line + 7
        
        
    def getData(self):
        """ Getter for the formatted data to write back to the .dat file.
        
        Returns:
            List - data formatted for writing to the new dat file.
        """
        out_data = []
        
        out_data.append(self.head_data['Name'])
        out_data.append(self.head_data['Revision'])
        out_data.append('{:>10}'.format(self.head_data['node_count']) +
                        '{:>10}'.format(self.head_data['Fr_lower']) +
                        '{:>10}'.format(self.head_data['Fr_Upper']) +
                        '{:>10}'.format(self.head_data['Min_depth']) +
                        '{:>10}'.format(self.head_data['Direct_method']) +
                        '{:>10}'.format(self.head_data['Unknown'])
                        )
        out_data.append('{:>10}'.format(self.head_data['Water_temp']) +
                        '{:>10}'.format(self.head_data['Flow']) +
                        '{:>10}'.format(self.head_data['Head']) +
                        '{:>10}'.format(self.head_data['Math_damp']) +
                        '{:>10}'.format(self.head_data['Pivot']) +
                        '{:>10}'.format(self.head_data['Relax']) +
                        '{:>10}'.format(self.head_data['Dummy'])
                        )
        out_data.append('RAD FILE')
        out_data.append(self.head_data['Roughness'])
        out_data.append('END GENERAL')
                        
        return out_data
        
        