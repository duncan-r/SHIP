"""

 Summary:  
    Contains the ADataObject class and all of its subclasses.
    
    These classes can be used to hold used by the :class:'<RowDataCollection>'.
    They provide a range of methods for easily acessing, amending and retrieving
    values to print to file. Classes include support for:  
        # Numeric data.  
        # String data.  
        # Symbol data.  
        # Constant data (a tuple of legal values).


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


from abc import ABCMeta, abstractmethod

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class ADataRowObject(object):
    """Abstract class for all data objects used in an AIsisUnit class.
    
    Note:
        It is unlikley that you want to call a class of this type directly.
        The RowDataFactory will perform checks required when constructing one
        of these objects. It should be used instead.
    """
    
    __metaclass__ = ABCMeta
    
    
#     def __init__(self, row_pos, datatype, format_str, default):
    def __init__(self, row_pos, datatype, format_str, **kwargs):
        """Constructor
        
        Args:
            row_pos(int): the position in the datarow held by this object.
            datatype (int): The type of collection it will hold (see the enum 
                list in the isis.datunits.ROW_DATA_TYPES.
            format_str (str): Represents the format that should be used to
                print out the values kept in this data collection. This 
                should be in the form '{:<10}' = 10 spaces formatted left. 
                With the required spaces need to correctly format the value 
                in the file.
            **kwargs:
                default: The default value that the collection should use -
                    Can be None if defaults are not allowed or '~' if the default 
                    should remove the formatting and apply an empty string.
                update_callback: a callback function that should be run everytime
                    a value is updated (added or set). For example to check
                    that chainage is increasing.
                    When called it will provide the following arguments:
                    (self, value, index).
        """
        self.data_type = datatype
        self.record_length = 0
        self.format_str = format_str 
        self.row_pos = row_pos
        self.default = kwargs.get('default', None)
        self.update_callback = kwargs.get('update_callback', None)
        self.has_changed = False
        
        self.data_collection = []
            
        self._min = 0
        self._max = len(self.data_collection)
        self._current = 0
    
    
    def __iter__(self):
        """Return an iterator for the data_collection list"""
        return iter(self.data_collection)
    
    
    def __next__(self):
        """Iterate to the next item in data_collection list"""
        if self._current > self._max or self._current < self._min:
            raise StopIteration
        else:
            self._current += 1
            return self.data_collection[self._current]
        

    def __getitem__(self, key):
        """Gets a value from data_collection using index notation.
        
        Returns:
            contents of the data_collection element at index.
        """
        return self.data_collection[key]
    

    def __setitem__(self, index, value):
        """Sets a value using index notation
        
        Calls the setValue() function to do the hard work.
        
        Args:
            index (int): index to update.
            value: the value to add to the data_collection.
        """
        self.setValue(value, index)
    
 
    def getValue(self, index):
        """Getter for retrieving the value at the supplied index.
        
        Args:
            index (int): The index of the required value.
        
        Returns:
            The value at the supplied index.
        """
        return self.data_collection[index]
 
    
    def getPrintableValue(self, index):
        """Getter for the formatted printable value at the supplied index.

        If the default value given == '~' then all formatting should be removed
        from the value if it is empty. Otherwise we call the subclass 
        formatPrintString() method.
        
        Args:
            index (int): The index of the required value.
        
        Returns:
            String containing the .DAT file print formatted value as defined 
                by the format_print_string variables set when the object was
                initialised.
        
        Raises:
             IndexError: If the given index doesn't exist. 
        """
        try:
            out_value = self.data_collection[index]
            
            if self.default == '~' and out_value == '':
                out_value = ''
            
            elif out_value == '':
                out_value = self.format_str.format('')
                return out_value            
                
            elif self.format_str == None:
                return str(out_value)
                        
            else:
                out_value = self.formatPrintString(out_value)
        except IndexError:
            logger.error('DataObject addValue() index out of bounds')
            raise
        
        return out_value
    
    
    def addValue(self, value=None, index=None):
        """Adds a value to the data_collection.
        
        This values will either be appended or put at a specific index if 
        one is provided. 
        
        Arguments:
            value: Optional - The value to be added. If no value is 
                provided the default value will be used.
            index (int): Optional - The index at which to add the value. If no
                value is given it will be appended to the end.
        
        Raises:
            IndexError: If index does not exist. 
        """
        if value == None: value = self.default

        if self.update_callback is not None:
            self.update_callback(self, value, index)
        
        length = len(self.data_collection)
        if index == None or index == length:
            self.data_collection.append(value)
        elif index > length:
            raise IndexError
        else:
            try:
                self.data_collection.insert(index, value)
            except IndexError:
                logger.error('DataObject addValue() index out of bounds')
                raise IndexError ('DataObject addValue() index out of bounds')

        self.has_changed = True
        self.record_length += 1
        self._max = len(self.data_collection)
           

    def setValue(self, value, index):
        """Changes the value at the given index
        
        Args:
            value: The new value to set. 
            index (int): The index of the value to be changed
        
        Raises:
            IndexError: If index does not exist. 
        """
        if self.update_callback is not None:
            self.update_callback(self, value, index)

        length = len(self.data_collection)
        if index == None or index == length:
            self.data_collection.append(value)
        elif index > length:
            raise IndexError
        else:
            try:
                self.data_collection[index] = value
            except IndexError:
                logger.error('DataObject setValue() index out of bounds')
                raise IndexError ('DataObject setValue() index out of bounds')
        
        self.has_changed = True

    
    def deleteValue(self, index):
        """Delete value at supplied position in unit.
        
        Args:
            index (int): index of value to be removed.
        
        Raises:
            IndexError: If index does not exist. 
     
        TODO:
            Bit dodgy to be honest as people could start deleting random 
            parts of one data_object without the other ones which would cock 
            things right up.
        """
        try:
            del self.data_collection[index]
        except IndexError:
            logger.error('DataObject deleteValue() index out of bounds')
            raise IndexError ('DataObject deleteValue() index out of bounds')
        
        self.has_changed = True
        self.record_length -= 1
        self._max = len(self.data_collection)
   
   
    def getDataCollection(self):
        return self.data_collection
    
    
    def checkDefault(self, value):
        if self.default == '~' and value == self.default:
            return True
        else:
            return False


    @abstractmethod
    def formatPrintString(self, value):
        """Abstract method for formatting the value to be printed.
        
        Formats the value as defined by format_string when the object was
        instantiated. This should be the format required when printing to 
        the .DAT file.
        
        Note:
            This class must be overridden by the concrete class with behaviour
            specific to formatting the particular value type.
        
        Args:
            value: The value to format.
        
        Returns:
            The formatted value.
        """
        pass
        


class IntData(ADataRowObject):
    """Concrete implememtation of the ADataRowObject for integer values.
    
    See Also:
        ADataRowObject
    """
    
#     def __init__(self, row_pos, datatype, format_str='{}', default=None):
    def __init__(self, row_pos, datatype, format_str='{}', **kwargs):
        """Constructor.
        
        Args:
            row_pos(int): the position in the datarow held by this object.
            datatype (int): The type of collection it will hold (see the enum 
                list in the isis.datunits.ROW_DATA_TYPES.
            format_str={} (str): Represents the format that should be used to
                print out the values kept in this data collection. This 
                should be in the form '{:<10}' = 10 spaces formatted left. 
                With the required spaces need to correctly format the value 
                in the file.
            **kwargs:
                default=None: The default value that the collection should use -
                    Can be None if defaults are not allowed or '~' if the default 
                    should remove the formatting and apply an empty string.
        """
        ADataRowObject.__init__(self, row_pos, datatype, format_str, **kwargs)
         
        
    def addValue(self, value=None, index = None):
        """Adds a value to the collection.
        
        See Also:
            ADataRowObject: addValue()
        """
        if not value == None:
            try:
                value = int(value)
            except ValueError:
                logger.error('Attempted to add invalid value to IntDataObject')
                raise ValueError ('Attempted to add invalid value to IntDataObject')
        
        ADataRowObject.addValue(self, value, index)
    

    def setValue(self, value, index):
        """Changes the value at the given index
        
        See Also:
            ADataRowObject: setValue()
        """
        try:
            value = int(value)
        except ValueError:
            logger.error('Attempted to add invalid value to IntDataObject')
            raise ValueError ('Attempted to add invalid value to IntDataObject')
        
        ADataRowObject.setValue(self, value, index)
            

    def formatPrintString(self, value):
        """Method for formatting the value to be printed in the .DAT file.
        
        Note:
            Overriddes superclass.

        Args:
            value (int): The value to format.
        
        Returns:
            String formatted value.
        """
        if self.checkDefault(value):
            value = ''
        else:
            integer_format = '%0d'
            value =  integer_format % int(value)
            value = self.format_str.format(value) 
        return value



class FloatData(ADataRowObject):
    """Overrides the value return methods from ADataObject to return a 
    float value instead of a string.
    """
    
#     def __init__(self, row_pos, datatype, format_str='{}', default=None, no_of_dps=0):
    def __init__(self, row_pos, datatype, format_str='{}', **kwargs): #default=None, no_of_dps=0):
        """Constructor.
        
        Args:
            row_pos(int): the position in the datarow held by this object.
            datatype (int): The type of collection it will hold (see the enum 
                list in the isis.datunits.ROW_DATA_TYPES.
            format_str={} (str): Represents the format that should be used to
                print out the values kept in this data collection. This 
                should be in the form '{:<10}' = 10 spaces formatted left. 
                With the required spaces need to correctly format the value 
                in the file.
            **kwargs:
                default=None: The default value that the collection should use -
                    Can be None if defaults are not allowed or '~' if the default 
                    should remove the formatting and apply an empty string.
                no_of_dps: int of the number of decimal places that this value
                       should be represented with when printed to file. 
        """
        self.no_of_dps = kwargs.get('no_of_dps', 0)
        ADataRowObject.__init__(self, row_pos, datatype, format_str, **kwargs)
         
        
    def addValue(self, value=None, index = None):
        """Adds a value to the collection.
        
        See Also:
            ADataRowObject: addValue()
        """
        if not value == None:
            try:
                value = float(value)
            except ValueError:
                logger.error('Attempted to add invalid value to FloatDataObject')
                raise ValueError ('Attempted to add invalid value to FloatDataObject')
        
        ADataRowObject.addValue(self, value, index)
    

    def setValue(self, value, index):
        """Changes the value at the given index
        
        See Also:
            ADataRowObject: setValue()
        """
        try:
            value = float(value)
        except ValueError:
            logger.error('Attempted to add invalid value to FloatDataObject')
            raise ValueError ('Attempted to add invalid value to FloatDataObject')
        
        ADataRowObject.setValue(self, value, index)
            

    def formatPrintString(self, value):
        """Method for formatting the value to be printed in the .DAT file.
        
        Note:
            Overriddes superclass.

        Args:
            value (int): The value to format.
        
        Returns:
            String formatted value.
        """
        if self.checkDefault(value):
            value = ''
        else:
            decimal_format = '%0.' + str(self.no_of_dps) + 'f'
            value =  decimal_format % float(value)
            value = self.format_str.format(value) 
        return value



class StringData(ADataRowObject):
    """Overrides the value return methods from ADataObject to return a 
    str value. 
    """
    
    def __init__(self, row_pos, datatype, format_str='{}', **kwargs):
        """Constructor.

        Args:
            row_pos(int): the position in the datarow held by this object.
            datatype (int): The type of collection it will hold (see the enum 
                list in the isis.datunits.ROW_DATA_TYPES.
            format_str={} (str): Represents the format that should be used to
                print out the values kept in this data collection. This 
                should be in the form '{:<10}' = 10 spaces formatted left. 
                With the required spaces need to correctly format the value 
                in the file.
            **kwargs:
                default=None: The default value that the collection should use -
                    Can be None if defaults are not allowed or '~' if the default 
                    should remove the formatting and apply an empty string.
        """
        ADataRowObject.__init__(self, row_pos, datatype, format_str, **kwargs)

        
    def addValue(self, value=None, index = None):
        """Adds a value to the collection.
        
        See Also:
            ADataRowObject: addValue()
        """
        if not value == None:
            try:
                value = str(value)
            except ValueError:
                logger.error('Attempted to add invalid value to StringDataObject')
                raise ValueError ('Attempted to add invalid value to StringDataObject')
            
            # Strip any whitespace off
            value = value.strip()
            
        # Call the superclass part of the method to add it.
        ADataRowObject.addValue(self, value, index)


    def setValue(self, value, index):
        """Changes the value at the given index
        
        See Also:
            ADataRowObject: setValue()
        """
        try:
            value = str(value)
        except ValueError:
            logger.error('Attempted to add invalid value to StringDataObject')
            raise ValueError('Attempted to add invalid value to StringDataObject')
        
        # Get rid of any whitespace
        value = value.strip()
        # Call the superclass to set the value
        ADataRowObject.setValue(self, value, index)


    def formatPrintString(self, value):
        """Method for formatting the value to be printed in the .DAT file.
        
        Note:
            Overriddes superclass.

        Args:
            value (int): The value to format.
        
        Returns:
            String formatted value.
        """
        if self.checkDefault(value):
            value = ''
        else:
            value = self.format_str.format(value) 
        return value



class ConstantData(ADataRowObject):
    """Overrides the value return methods from ADataObject to return a 
    str value from a list of predefined constants.
    """
    
    def __init__(self, row_pos, datatype, legal_values, format_str='{}', **kwargs):
        """Constructor.

        Args:
            row_pos(int): the position in the datarow held by this object.
            datatype (int): The type of collection it will hold (see the enum 
                list in the isis.datunits.ROW_DATA_TYPES.
            legal_values(tuple): contains the possible values that this 
                collection can have.
            format_str={} (str): Represents the format that should be used to
                print out the values kept in this data collection. This 
                should be in the form '{:<10}' = 10 spaces formatted left. 
                With the required spaces need to correctly format the value 
                in the file.
            **kwargs:
                default=None: The default value that the collection should use -
                    Can be None if defaults are not allowed or '~' if the default 
                    should remove the formatting and apply an empty string.
        
        Raises:
            AttributeError: if legal_values in not a valid tuple.
        """
        if not isinstance(legal_values, tuple):
            raise AttributeError ('legal_values is not a tuple')
        self.legal_values = legal_values
        ADataRowObject.__init__(self, row_pos, datatype, format_str, **kwargs)
         
        
    def addValue(self, value=None, index = None):
        """Adds a value to the collection.
        
        See Also:
            ADataRowObject: addValue()
        """
        if not value == None:
            if not value in self.legal_values:
                value = False
            
        # Call the superclass part of the method to add it.
        ADataRowObject.addValue(self, value, index)


    def setValue(self, value, index):
        """Changes the value at the given index
        
        See Also:
            ADataRowObject: setValue()
        """
        if not value in self.legal_values:
            value = False
        
        # Call the superclass to set the value
        ADataRowObject.setValue(self, value, index)


    def formatPrintString(self, value):
        """Method for formatting the value to be printed in the .DAT file.
        
        Note:
            Overriddes superclass.

        Args:
            value (int): The value to format.
        
        Returns:
            String formatted value.
        """
        if value == False:
            value = ''

        if self.checkDefault(value):
            value = ''
        else:
            value = self.format_str.format(value) 
        return value



class SymbolData(ADataRowObject):
    """Overrides the value return methods from ADataObject to return a 
    float value instead of a string.
    """
    
    def __init__(self, row_pos, datatype, symbol, format_str='{}', **kwargs):
        """Constructor.

        Args:
            row_pos(int): the position in the datarow held by this object.
            datatype (int): The type of collection it will hold (see the enum 
                list in the isis.datunits.ROW_DATA_TYPES.
            symbol(str): The symbol that should should be used to represent the 
               presence of this value in the file.
            legal_values(tuple): contains the possible values that this 
                collection can have.
            format_str={} (str): Represents the format that should be used to
                print out the values kept in this data collection. This 
                should be in the form '{:<10}' = 10 spaces formatted left. 
                With the required spaces need to correctly format the value 
                in the file.
            **kwargs:
                default=None: The default value that the collection should use -
                    Can be None if defaults are not allowed or '~' if the default 
                    should remove the formatting and apply an empty string.
        
        Raises:
            AttributeError: if legal_values in not a valid tuple.
        """
        self.symbol = symbol
        self.bool_type = bool # Used to test if a value is of type bool or not
        ADataRowObject.__init__(self, row_pos, datatype, format_str, **kwargs)
         
        
    def addValue(self, value=None, index = None):
        """Adds a value to the collection.
        
        See Also:
            ADataRowObject: addValue()
        """
        if not value == None:
            if value == self.symbol:
                value = True
            elif value == '':
                value = False 
                
            # Make sure that we are adding a bool type
            if not isinstance(value, self.bool_type):
                logger.error('Attempted to add invalid value to SymbolDataObject')
                raise ValueError ('Attempted to add invalid value to SymbolDataObject')
             
        # Call superclass to add the value
        ADataRowObject.addValue(self, value, index)
        
        
    def setValue(self, value, index):
        """Changes the value at the given index
        
        See Also:
            ADataRowObject: setValue()
        """
        if value == self.symbol:
            value = True
        elif value == '':
            value = False 
            
        # Make sure that we are adding a bool type
        if not isinstance(value, self.bool_type):
            logger.error('Attempted to add invalid value to SymbolDataObject')
            raise ValueError ('Attempted to add invalid value to SymbolDataObject')
        
        # Call the superclass to set the value
        ADataRowObject.setValue(self, value, index)


    def formatPrintString(self, value):
        """Method for formatting the value to be printed in the .DAT file.
        
        Note:
            Overriddes superclass.

        Args:
            value (int): The value to format.
        
        Returns:
            String formatted value.
        """
        if value == True:
            value = self.symbol
        else:
            value = ''

        if self.checkDefault(value):
            value = ''
        else:
            value = self.format_str.format(value) 
        return value
        

