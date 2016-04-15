"""

 Summary:
    Contains the RowDataCollection object. This is an object used to hold
    all of the data for a specific row of a unit in an ISIS dat file.
    It acts a collection pattern to make accessing and updating the contents
    of a row simpler.

 Author:  
     Duncan Runnacles

 Created:  
     01 Apr 2016

 Copyright: 
     Duncan Runnacles 2016

 TODO:

 Updates:

"""

import copy

import logging
logger = logging.getLogger(__name__)

from ship.data_structures.dataobject import *
"""logging references with a __name__ set to this module."""


class RowDataCollection(object):
    """Composite/Facade for the ADataRowObject classes.
    
    AIsisUnit classes should instantiate this class in order to manage all the
    ADataRowObject classes used to hold the units row data.
    There are several convenience methods to retrieve and safely update the
    contents.
    
    Note:
        There are many references to a 'key' variable in this class to decipher
        which object in the collection to access/update/etc. This is one of
        the ROW_DATA_TYPES enum values in the datunits package.
    
    See Also:
        ROW_DATA_TYPE - in :class:'datunits <ship.isis.datunits>' module.
    
    TODO:
          Need to find a way to safely add values to the collection while making
          sure that all the data objects stay in sync (i.e. have the same number
          of rows), otherwise it will be chaos. At the moment this is tricky
          because we need to add individual values at the start. Possibly stop 
          client from using any get methods etc unless all the data objects have
          the same number of rows. For the time being there is a convenience
          method checkRowsInSync() that can be called to verify that all of the
          data objects in this collection have the same length.
    """
    
    
    def __init__(self):
        """Create a reference to the collection list."""
        self._collection = []
        self._min_collection = 0
        self._current_collection = 0
        self._max = len(self._collection)
        self._min = 0
        self._current = 0
    
    
    def __iter__(self):
        """Return an iterator for the units list"""
        return iter(self._collection)
    
    
    def __next__(self):
        """Iterate to the next unit"""
        if self._current > self._max or self._current < self._min:
            raise StopIteration
        else:
            self._current += 1
            return self._collection[self._current] 
    
    
    def __getitem__(self, key):
        """Gets a value from _collection using index notation.
        
        Returns:
            contents of the _collection element at index.
        """
        return self._collection[key]
    

    def initCollection(self, obj_type, vars):
        """Setup a new data object and add it to the collection.
        
        Args:
            obj_type (str): The type of ADataRowObject to create. This should 
                be a DataTypes enum from the ADataObject module.
            vars (list): The variables specific to the ADataRowObject that is 
                going to be instantiated.
                
        See Also: 
            ADataRowObject (and subclasses), DataTypes - all in ADataObject 
            module.
        """  
        row_data =  RowDataFactory(obj_type, vars)
        self._collection.append(row_data)
        self._max = len(self._collection)
        
        
    def addValue(self, key, value=None):
        """Add a new value to the data object in the collection as referenced by
        the key provided.
        
        Args:
            key (int): Name of the data object to add the given value to.
            value: Optional - The value to add to the collection. If no value
                is supplied a default will be used.
        
        Raises:
             KeyError: If the name key doesn't exist in the collection.  

        TODO:
            Check what other errors are thrown by the data object and make 
            sure that they are dealt with/passed on from here.
        """
        # Find the collection by the key and add the value to it.
        for c in self._collection:
            if c.data_type == key:
                c.addValue(value)
                break
        else:
            raise KeyError ('Key %s does not exist in collection' % (key))
    
    
    def setValue(self, key, value, index):
        """Set the value to the data object in the collection.
        
        Args:
            key (int): the type data object to add the given value to.
            value: The value to add to the collection.
            index (int): the index to set the value at.
        
        Raises:
            KeyError: If the name key doesn't exist in the collection.  
            ValueError: If the value is not appropriate for the data type
        """
        # Find the collection by the key and add the value to it.
        for c in self._collection:
            if c.data_type == key:
                
                try:
                    c.setValue(value, index)
                    break
                except ValueError:
                    raise 
        else:
            raise KeyError ('Key %s does not exist in collection' % (key))
        
    
    def getPrintableRow(self, index):
        """ Get the row data in printable form.
        
        Retrieves all of the values in this RowDataObjectCollection at the
        given index and returns the row. The order is based on the row_pos 
        variable provided in the initCollection() method.
        
        Args:
            index (int): the row collection index to access.
            
        Returns:
            string formatted for printing to .DAT file.
        """
        out_str = ''
        # Sort the collection by the row_pos variable in the ADataRowObjects
        # and loop through the collection getting a printable value.
        self._collection.sort(key=lambda x: x.row_pos)
        for i, obj in enumerate(self._collection):
            out_str += obj.getPrintableValue(index)
                
        return out_str
    
        
    def updateRow(self, values_dict, index):
        """Add a new row to the units data rows.
        
        Creates a new row from the values in the supplied value dict at the location
        given by the index.
        If the index is None then the value will be appended to the end of the row
        rather than inserted.
        
        Note: 
            If there is any problem while updating the values in the row all 
            datarow objects will be returned to the state they were in before 
            the operation. This ensures that they don't get out of sync if an 
            error is found halfway through adding the different values. This is 
            done by creating a deep copy of the object prior to updating.

        Args:
            values_dict (dict): Contains the names of the data objects of
                collection as keys and the new row values as values.
            index (int): The index at which to insert the row.
        
        Raises:
            KeyError: If any of the keys don't exist.
            IndexError: If the index doesn't exist.
        """
        new_keys = sorted(list(values_dict))
        cur_keys = sorted(self.getCollectionTypes())
        if not new_keys == cur_keys:
            raise KeyError
        if index > self.getNumberOfRows():
            raise IndexError
        
        try:
            # Need to make a deep copy of the data_object so we can reset them back
            # to the same place if there's a problem. That way we don't get the lists
            # in the different objects out of sync.
            temp_list = self._deepCopyDataObjects(self._collection) 
            
            for obj in self._collection:
                obj.setValue(values_dict[obj.data_type], index)
            
        except (IndexError, ValueError, Exception):
            self._resetDataObject(temp_list)
        finally:
            for o in temp_list:
                del o
            del temp_list
     
        
    def addNewRow(self, values_dict, index):
        """Add a new row to the units data rows.
        
        Creates a new row from the values in the supplied value dict at the location
        given by the index.
        If the index is None then the value will be appended to the end of the row
        rather than inserted.
        
        Note: 
            If there is any problem while adding the new row all datarow objects
            will be returned to the state they were in before the operation.
            This ensures that they don't get out of sync if an error is found
            halfway through adding the different values. This is done by 
            creating a deep copy of the object prior to updating.

        Args:
            values_dict (dict): Contains the names of the data objects of
                collection as keys and the new row values as values.
            index (int): The index at which to insert the row.
        
        Raises:
            KeyError: If any of the keys don't exist.
            IndexError: If the index doesn't exist.
        """
        new_keys = sorted(list(values_dict))
        cur_keys = sorted(self.getCollectionTypes())
        if not new_keys == cur_keys:
            raise KeyError
        if index > self.getNumberOfRows():
            raise IndexError
        
        try:
            # Need to make a deep copy of the data_object so we can reset them back
            # to the same place if there's a problem. That way we don't get the lists
            # in the different objects out of sync.
            temp_list = self._deepCopyDataObjects(self._collection) 
            
            for obj in self._collection:
                obj.addValue(values_dict[obj.data_type], index)
            
        except (IndexError, ValueError, Exception):
            self._resetDataObject(temp_list)
            raise 
        finally:
            for o in temp_list:
                del o
            del temp_list
        
        
    def getCollectionTypes(self): 
        """Get a list of the types (names) of all the objects in the collection.
        
        The list returned will contain all of the names used in this 
        row collection. e.g. 'chainage', 'elevation' etc.
        
        Returns:
            keys (list): containing the names of the data objects.
        """
        keys = []
        for obj in self._collection:
            keys.append(obj.data_type)
            
        return keys
    
    
    def getDataObject(self, name_key):
        """Return the ADataRowObject instance requested.
        
        Args:
            name_key (str): The key to use to retrieve the object 
                (e.g. 'chainage'). This is usually a class declared constant 
                e.g. RiverUnit.CHAINAGE.
        
        Returns:
            ADataRowObject or False if the key doesn't match any in the 
            collection.
            
        
        Note: 
            Returns a shallow copy of the collection. Any changes to the
            values will remain within the main list. If you want to be 
            able to change it without affecting the main copy use
            getDataObjectCopy().
        """
        for obj in self._collection:
            if obj.data_type == name_key:
                return obj
        else:
            raise KeyError ('name_key %s was not found in collection' % (name_key))
    
    
    def getRowDataAsList(self, key=None):
        """Returns the row data object as a list.

        This will return the row_collection data object referenced by the key
        provided in list form.

        If you intend to update the values you should use getRowDataObject
        instead as the data provided will be mutable and therefore reflected in
        the values held by the row_collection. If you just want a quick way to
        loop through the values in one of the data objects  and only intend to
        read the data then use this.
        
        Args:
            key=None (str): the key for the data object requested. It is best 
                to use  the class constants (i.e. RiverUnit.CHAINAGE) for this.
                If None then all rows are returned.
        
        Returns:
            List containing the data in the DataObject that the key points
                 to. Returns false if there is no row collection.
        
        Raises:
            KeyError: If key does not exist.
        """
        if key is None:
            outlist = []
            for c in self._collection:
                innerlist = []
                for i in range(0, c.record_length):
                    innerlist.append(c.getValue(i))
                outlist.append(innerlist)
            return outlist
                
        try:
            data_col = self.getDataObject(key)
            if data_col == False: raise KeyError ('Key %s does not exist in collection' % (key))
            
            vals = []
            for i in range(0, data_col.record_length):
                vals.append(data_col.getValue(i))
            return vals
        except KeyError:
            raise 
        
    
    def getDataObjectCopy(self, name_key):
        """Return the ADataRowObject instance requested.

        Same as the getDataObject() method except it makes a deep copy of the
        data object before returning it so that any changes will local to the
        returned copy only and not to the main reference.
        
        Args:
            name_key (str): The key to use to retrieve the object 
                (e.g. 'chainage'). This is usually a class declared constant 
                e.g. RiverUnit.CHAINAGE.
        
        Returns:
            ADataRowObject or False if the key doesn't match any in the 
            collection.
        """
        for obj in self._collection:
            if obj.data_type == name_key:
                obj_copy = self._deepCopyDataObjects(obj)
                return obj_copy
        else:
            raise KeyError ('name_key %s was not found in collection' % (name_key))
            
    
    def getDataValue(self, name_key, index):
        """Get the value of a data object in the collection.
        
        Args:
            name_key (str): The name of the data object to get the value from.
            index: int - the row index to get the value from or False if the key
               doesn't exist in the collection.
        
        Returns:
            The requested value or False if the key or index do not exist.
        """
        if index > self.getNumberOfRows():
            raise IndexError ('Index %s is greater than number of values in collection' % (index))

        for obj in self._collection:
            if obj.data_type == name_key:
                return obj.getValue(index)
        else:
            raise KeyError ('name_key %s was not found in collection' % (name_key))
        
    
    def deleteDataObject(self, name_key):
        """Delete the ADataRowObject instance requested.
        
        Args:
            name_key (str): The key to use to retrieve the object 
                (i.e. 'chainage')
        
        Returns:
            True if the object was successfully deleted; False if not.
        """
        for obj in self._collection:
            if obj.data_type == name_key:
                self._collection.remove(obj)
                self._max = len(self._collection)
                return True
        else:
            return False
              
    
    def getNumberOfRows(self):
        """Return the number of rows held in the collection
        
        Returns:
            int - number of rows in this collection.
        """
        return self._collection[0].record_length
    
    
    def checkRowsInSync(self):
        """Checks that the data objects in the collection are in sync.
        
        All the rows should be the same length. If they aren't then there's 
        a problem and it will corrupt any output .dat file.
        
        Warning:
            It isn't actually that hard to corrupt the collection at the 
            moment. It's ok if the DataObject classes are only accessed through
            here. If they are accessed independently of this class and not
            carefully checked they could fall out of sync.
        
        Returns:
            True if all data collections have the same length, otherwise
                 False. 
        """
        lengths = []
        for obj in self._collection:
            lengths.append(obj.record_length)
        
        return lengths[1:] == lengths[:-1]
    

    def _resetDataObject(self, temp_list):
        """Reset the data_objects list to its previous state.
        
        This method is called when there is a problem with updating the data_objects
        list. It returns the self owned versions to their original state.
        
        Args:
            temp_list: The versions to return the objects to.
        """
        self._collection = temp_list

        for o in temp_list:
            del o
        del temp_list
               
                
    def _deepCopyDataObjects(self, obj): 
        """Create a deep copy of the data_objects
        
        """
        object_copy = copy.deepcopy(obj)
        return object_copy
    
    
    
    