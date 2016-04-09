"""

 Summary:  
    Contains the ADataObject class and all of its subclasses. These are 
    used to hold the values in the ISIS data file.

    A RowDataFactory is included in this module. It's used to build the type
    of ADataObject specified by the type read in from the data file.

 Author:  
     Duncan Runnacles
     
 Created:  
     01 Apr 2016
     
 Copyright:  
     Duncan Runnacles 2016

 TODO:
     The way that the RowDataFactory works to create ADataRowObject class
     types is poorly designed and naive at the moment. It needs to designed
     better to take advantage of polymorphism.

 Updates:

"""


from abc import ABCMeta, abstractmethod

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class DataTypes(object):
    """Enum class for the different ADataRowObject Types available
    
    This can be used by any caller of RowDataFactory to specify the type of
    row data required.
    """

    STRING_DATA, INT_DATA, FLOAT_DATA, CONSTANT_DATA, SYMBOL_DATA = range(5)


def RowDataFactory(obj_type, vars):
    """Factory for creating instances of ADataRowObject types.

    Calls the appropriate __init__() of the DataRowObject as
    defined by the data_type variable. Caller should use the enum class 
    DataTypes to do this..


    Args:
        obj_type (DataTypes): The DataType that should be created: STRING_DATA,
           FLOAT_DATA, CONSTANT_DATA, SYMBOL_DATA. See Also the classes in this 
           module for details on implementation.
        vars (list): The obj_type specific variables that are needed. Further
            details in 'Note' below. 
    
    Returns:
        ADataRowObject: As defined by the obj_type variable provided. 
    
    Raises:
        IndexError: If the factory cannot access the variables needed
               to instanciate the class.
        NotImplementedError: If the given obj_type is not recognised.

    Note: The object specified variables are further defined in the 
        ADataRowObject subclasses - StringDataRowObject, FloatDataRowObject, 
        ConstantDataRowObject, and SymbolDataRowObject.
        
    TODO:
          Need some type checking here to make sure that the vars handed
          in match the requirements for the individual ob_types.  
          
    """    
    try: 
        if obj_type == DataTypes.STRING_DATA:
            # Hand in the data_type[0], format_str[1], default[2], row_pos[3]
            obj_data = StringDataRowObject(vars[0], vars[1], vars[2], vars[3])

        elif obj_type == DataTypes.INT_DATA:
            # Hand in the data_type[0], format_str[1], default[2], row_pos[3]
            obj_data = IntDataRowObject(vars[0], vars[1], vars[2], vars[3])
        
        elif obj_type == DataTypes.FLOAT_DATA:
            # data_type[0], format_str[1], default[2], row_pos[3], no_of_dps[4]
            obj_data = FloatDataRowObject(vars[0], vars[1], vars[2], vars[3], vars[4])
        
        elif obj_type == DataTypes.CONSTANT_DATA:
            # data_type[0], format_str[1], default[2], row_pos[3], legal_values[4]
            obj_data = ConstantDataRowObject(vars[0], vars[1], vars[2], vars[3], vars[4])
            
        elif obj_type == DataTypes.SYMBOL_DATA:
            # data_type[0], format_str[1], default[2], row_pos[3], symbol[4]
            obj_data = SymbolDataRowObject(vars[0], vars[1], vars[2], vars[3], vars[4])
            
        else:
            logger.error('RowDataFactory - type is not recognised.')
            raise NotImplementedError ('RowDataFactory type is not recognised.')
        
        return obj_data
        
    except IndexError:
        logger.error('RowDataFactory - required index does not exist')
        raise
    
    return False


class ADataRowObject(object):
    """Abstract class for all data objects used in an AIsisUnit class.
    
    Note:
        It is unlikley that you want to call a class of this type directly.
        The RowDataFactory will perform checks required when constructing one
        of these objects. It should be used instead.
    """
    
    __metaclass__ = ABCMeta
    
    
    def __init__(self, data_type, format_str, default, row_pos, data_collection = None):
        """Constructor
        
        Args:
            data_type (int): The type of collection it will hold (see the enum 
            list in the DataType class.
            format_str (str): Represents the format that should be used to
                   print out the values kept in this data collection. This 
                   should be in the form '{:<10}' = 10 spaces formatted left. 
                   With the required spaces need to correctly format the value 
                   in the file.
            default: The default value that the collection should use -
                Can be None if defaults are not allowed or '~' if the default 
                should remove the formatting and apply an empty string.
            data_collection (list): Optional. An existing data collection in 
                list form. Used to set the initial state of this collection.  
        """
        self.data_type = data_type
        self.record_length = 0
        self.format_str = format_str 
        self.row_pos = row_pos
        self.default = default
        self.has_changed = False
        
        if data_collection == None: 
            self.data_collection = []
        else:
            self.data_collection = data_collection
    
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
    

    def __setitem__(self, key, value):
        """Sets a value using index notation
        
        Calls the setValue() function to do the hard work.
        
        Args:
            key (int): index to update.
            value: the value to add to the data_collection.
        """
        self.setValue(value, key)
    
 
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
                raise ('DataObject addValue() index out of bounds')

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
                raise ('DataObject setValue() index out of bounds')
        
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
            self.data_collection.remove(index)
        except IndexError:
            logger.error('DataObject deleteValue() index out of bounds')
            raise ('DataObject deleteValue() index out of bounds')
        
        self.has_changed = True
        self.record_length -= 1
        self._max = len(self.data_collection)
   
   
    def getDataCollection(self):
        return self.data_collection
    

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
        


class IntDataRowObject(ADataRowObject):
    """Concrete implememtation of the ADataRowObject for integer values.
    
    See Also:
        ADataRowObject
    """
    
    def __init__(self, data_type, format_str, default, row_pos, data_collection = None):
        """Constructor.
        
        Args:
            data_type (str): Identifies this DataRowObject.
            format_str (str): Represnets the format that should be used to
               print out the values kept in this data collection. This 
               should be in the form '{:<10}' = 10 spaces formatted left. 
               With the required spaces need to correctly format the value 
               in the file.
            default: The default value that the collection should use - Can be
               None if defaults are not allowed.
            row_pos (int): The position in the row that the values in this
               collection exist.
            data_collection (list): A complete data collection if already built.    
        
        """
        ADataRowObject.__init__(self, data_type, format_str, default, row_pos, data_collection)
         
        
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
                raise ('Attempted to add invalid value to IntDataObject')
        
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
            raise ('Attempted to add invalid value to IntDataObject')
        
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
        integer_format = '%0d'
        value =  integer_format % int(value)
        value = self.format_str.format(value) 
        return value



class FloatDataRowObject(ADataRowObject):
    """Overrides the value return methods from ADataObject to return a 
    float value instead of a string.
    """
    
    def __init__(self, data_type, format_str, default, row_pos, no_of_dps, data_collection = None):
        """Constructor.
        
        Args:
            data_type (str): Identifies this DataRowObject.
            format_str (str): Represnets the format that should be used to
               print out the values kept in this data collection. This 
               should be in the form '{:<10}' = 10 spaces formatted left. 
               With the required spaces need to correctly format the value 
               in the file.
            default: The default value that the collection should use - Can be
               None if defaults are not allowed.
            row_pos (int): The position in the row that the values in this
               collection exist.
            no_of_dps: int of the number of decimal places that this value
                   should be represented with when printed to file. 
            data_collection (list): A complete data collection if already built.  
        
        """
        self.no_of_dps = no_of_dps
        ADataRowObject.__init__(self, data_type, format_str, default, row_pos, data_collection)
         
        
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
        decimal_format = '%0.' + str(self.no_of_dps) + 'f'
        value =  decimal_format % float(value)
        value = self.format_str.format(value) 
        return value



class StringDataRowObject(ADataRowObject):
    """Overrides the value return methods from ADataObject to return a 
    str value. 
    """
    
    def __init__(self, data_type, format_str, default, row_pos, data_collection = None):
        """Constructor.
        Args:
            data_typei (str): Used to identify this DataRowObject.
            format_str (str): Representing the format that should be used to
                print out the values kept in this data collection. This should be
                in the form '{:<10}' = 10 spaces formatted left. With the required
                spaces need to correctly format the value in the file.
            default (str): The default value that the collection should use - Can be
                None if defaults are not allowed.
            row_pos (int): The position in the row that the values in this
                collection.
            data_collection (list): A complete data collection if already built.    
        """
        ADataRowObject.__init__(self, data_type, format_str, default, row_pos, data_collection)
         
        
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
                raise ('Attempted to add invalid value to StringDataObject')
            
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
            raise ('Attempted to add invalid value to StringDataObject')
        
        # Get rid of any whitespace
        value = value.strip()
        # Call the superclass to set the value
        ADataRowObject.addValue(self, value, index)


    def formatPrintString(self, value):
        """Method for formatting the value to be printed in the .DAT file.
        
        Note:
            Overriddes superclass.

        Args:
            value (int): The value to format.
        
        Returns:
            String formatted value.
        """
        value = self.format_str.format(value) 
        return value



class ConstantDataRowObject(ADataRowObject):
    """Overrides the value return methods from ADataObject to return a 
    str value from a list of predefined constants.
    """
    
    def __init__(self, data_type, format_str, default, row_pos, legal_values, data_collection = None):
        """Constructor.
        Args:
            data_typei (str): Used to identify this DataRowObject.
            format_str (str): Representing the format that should be used to
                print out the values kept in this data collection. This should be
                in the form '{:<10}' = 10 spaces formatted left. With the required
                spaces need to correctly format the value in the file.
            default (str): The default value that the collection should use - Can be
                None if defaults are not allowed.
            row_pos (int): The position in the row that the values in this
                collection.
            legal_values(tuple): contains the possible values that this 
                collection can have.
            data_collection (list): A complete data collection if already built.    
        
        Raises:
            AttributeError: if legal_values in not a valid tuple.
        """
        if not isinstance(legal_values, tuple):
            raise AttributeError ('legal_values is not a tuple')
        self.legal_values = legal_values
        ADataRowObject.__init__(self, data_type, format_str, default, row_pos, data_collection)
         
        
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
        value = self.format_str.format(value) 
        return value



class SymbolDataRowObject(ADataRowObject):
    """Overrides the value return methods from ADataObject to return a 
    float value instead of a string.
    """
    
    def __init__(self, data_type, format_str, default, row_pos, symbol, data_collection = None):
        """Constructor.
        Args:
            data_typei (str): Used to identify this DataRowObject.
            format_str (str): Representing the format that should be used to
                print out the values kept in this data collection. This should be
                in the form '{:<10}' = 10 spaces formatted left. With the required
                spaces need to correctly format the value in the file.
            default (str): The default value that the collection should use - Can be
                None if defaults are not allowed.
            row_pos (int): The position in the row that the values in this
                collection.
            symbol(str): The symbol that should should be used to represent the 
               presence of this value in the file.
            data_collection (list): A complete data collection if already built.    
        
        Raises:
            AttributeError: if legal_values in not a valid tuple.
        """
        self.symbol = symbol
        self.bool_type = bool # Used to test if a value is of type bool or not
        ADataRowObject.__init__(self, data_type, format_str, default, row_pos, data_collection)
         
        
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
        value = self.format_str.format(value) 
        return value
        

