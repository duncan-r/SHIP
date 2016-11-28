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
from __future__ import unicode_literals

import copy

import logging
logger = logging.getLogger(__name__)

from ship.datastructures.dataobject import *
"""logging references with a __name__ set to this module."""


class RowDataCollection(object):
    """Composite/Facade for the ADataRowObject classes.
    
    AUnit classes should instantiate this class in order to manage all the
    ADataRowObject classes used to hold the units row data.
    There are several convenience methods to retrieve and safely update the
    contents.
    
    Note:
        There are many references to a 'key' variable in this class to decipher
        which object in the collection to access/update/etc. This is one of
        the ROW_DATA_TYPES enum values in the datunits package.
    
    See Also:
        ROW_DATA_TYPE - in :class:'datunits <ship.fmp.datunits>' module.
    
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
    
    
    def __init__(self, **kwargs):
        """Create a reference to the collection list."""
        self._collection = []
        self._min_collection = 0
        self._current_collection = 0
        self._updateCallback = kwargs.get('update_callback', None)
        self.has_dummy = False

    
    @classmethod
    def bulkInitCollection(cls, dataobjects, **kwargs):
        rc = cls(**kwargs)
        for d in dataobjects:
            rc._collection.append(d)
            rc._max = len(rc._collection)
        return rc
    
    @property
    def row_count(self):
        return self.numberOfRows()
    

#     def initCollection(self, dataobject):
    def addToCollection(self, dataobject, index=None):
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
        if index is None:
            self._collection.append(dataobject)
        else:
            try:
                self._collection.insert(dataobject)
            except IndexError:
                raise('Index %s does not exist in collection' % index)
        self._max = len(self._collection)
    
    
    def indexOfDataObject(self, key):
        """Get the index of the DataObject with data_type equal to key.
        """
        for i, c in enumerate(self._collection):
            if c.data_type == key:
                return i
    
    def iterateRows(self, key=None):
        """Returns a generator for iterating through the rows in the collection.
        
        If no key is given it will return a list containing all of the values
        in the row.
        
        Args:
            key=None(int): ROW_DATA_TYPE to return. If None all values in the
                row will be returned as a list.
                
        Return:
            list if key == None, a single value otherwise.
        """
        if key is None:
            for i in range(0, self.row_count):
                yield [o.getValue(i) for o in self._collection]
        else:
            index = self.indexOfDataObject(key)
            for i in range(0, self.row_count):
                yield self._collection[index].getValue(i)
        
    
    def rowAsDict(self, index):
        """Get the data vals in a particular row by index.
        
        Args:
            index(int): the index of the row to return.
            
        Return:
            dict - containing the values for the requested row.
        """
        output = {}
        for obj in self._collection:
            output[obj.data_type] = obj.getValue(index)
        
        return output


    def rowAsList(self, index):
        """Get the data vals in a particular row by index.
        
        Args:
            index(int): the index of the row to return.
            
        Return:
            dict - containing the values for the requested row.
        """
        output = []
        for obj in self._collection:
            output.append(obj.getValue(index))
        
        return output
        
    
    def dataObject(self, name_key):
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
    

    def DataObjectAsList(self, key):
        """Returns a DataObject as a list.

        This will return the row_collection DataObject referenced by the key
        provided (as a ROW_DATA_TYPES) in list form.

        If you intend to update the values you should use getRowDataObject
        instead as the data provided will be mutable and therefore reflected in
        the values held by the row_collection. If you just want a quick way to
        loop through the values in one of the data objects  and only intend to
        read the data then use this.
        
        Args:
            key(str): the key for the data object requested. It is best 
                to use  the class constants (i.e. RiverUnit.CHAINAGE) for this.
        
        Returns:
            List containing the data in the DataObject that the key points
                 to. Returns false if there is no row collection.
        
        Raises:
            KeyError: If key does not exist.
        """                
        try:
            data_col = self.dataObject(key)
            if data_col == False: raise KeyError ('Key %s does not exist in collection' % (key))
            
            vals = []
            for i in data_col:
                vals.append(i)
            return vals
        except KeyError:
            raise

    
    def toList(self):
        """Returns the row data a list.
        
        Collects the row data in each of the ADataObjects in this collection
        into a list. Then adds them to a list based on the order of this 
        collection. I.e. each inner list is the data pertaining to a single 
        ADataObject.
        
        Example:
            [
                [0.0, 1.5, 3.0],
                [32.5, 31.0, 31.5],
                [0.03, 0.03, 0.03]
            ]
        
        Returns:
            List - containing lists of the data in the DataObjects in this
                collection.

        Raises:
            KeyError: If key does not exist.
        """
        outlist = []
        for c in self._collection:
            innerlist = []
            for i in c:
                innerlist.append(i)
            outlist.append(innerlist)
        return outlist
                
    
    def toDict(self):
        """Returns the row data object as a dict.

        Provides a dict where keys are the datunits.ROW_DATA_TYPES and the
        values are lists of the values for that type in sequence.

        If you intend to update the values you should use getRowDataObject
        instead as the data provided will be mutable and therefore reflected in
        the values held by the collection. If you just want to read the data 
        then use this.
        
        Returns:
            dict - containing lists of values by ROW_DATA_TYPE.
        """
        vals = {}
        for c in self._collection:
            inner = []
            for i in c:
                inner.append(i)
            vals[c.data_type] = inner
        return vals
    
    
    def dataValue(self, key, index):
        """Get the value in a DataObject at index.
        
        Args:
            key(int): ROW_DATA_TYPES for the DataObject.
            index(int): the row to return the value from.
            
        Return:
            The value in the DataObject at given index.
        
        Raises:
            KeyError - if key does not exist in collection.
            IndexError - if index does not exist in DataObject.
        """
        for c in self._collection:
            if c.data_type == key:
                val = c.getValue(index)
                return val
        else:
            raise KeyError('DataObject %s does not exist in collection' % key)

        
    def _addValue(self, key, value=None):
        """Add a new value to the data object in the collection as referenced by
        the key provided.
        
        Note:
            You almost certainly don't want to be using this. It's used internally
            to add values to ADataObject's. If you need to add data use the
            addRow() method.
        
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

        # Do this after so it's not removed when something goes wrong
        if self.has_dummy:
            self.deleteRow(0)
            self.has_dummy = False
        
    
    def _setValue(self, key, value, index):
        """Set the value to the data object in the collection.

        Note:
            You almost certainly don't want to be using this. It's used internally
            to set alues to ADataObject's. If you need to add data use the
            updateRow() method. It will check consitency across the collection.
        
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
        
        Retrieves all of the values in this RowDataObjectCollection in the 
        order that it exists in the list.        

        Args:
            index (int): the row collection index to access.
            
        Returns:
            string formatted for printing to .DAT file.
        """
        out_str = ''
        for i, obj in enumerate(self._collection):
            out_str += obj.getPrintableValue(index)
                
        return out_str
    
        
    def updateRow(self, row_vals, index):
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
            row_vals (dict): Contains the names of the data objects of
                collection as keys and the new row values as values.
            index (int): The index at which to insert the row.
        
        Raises:
            KeyError: If any of the keys don't exist.
            IndexError: If the index doesn't exist.
        """
        if index > self.row_count:
            raise IndexError

        dataobj_keys = self.collectionTypes()
        vkeys = row_vals.keys()
        for k in vkeys:
            if not k in dataobj_keys:
                raise KeyError('ROW_DATA_TYPE ' + str(k) + 'is not in collection')
        
        try:
            # Need to make a deep copy of the data_object so we can reset them back
            # to the same place if there's a problem. That way we don't get the lists
            # in the different objects out of sync.
            temp_list = self._deepCopyDataObjects(self._collection) 
            
            for key, val in row_vals.items():
                self._setValue(key, val, index)
            
        except (IndexError, ValueError, Exception) as err:
            self._resetDataObject(temp_list)
            raise err
        finally:
            for o in temp_list:
                del o
            del temp_list
     
        
    def addRow(self, row_vals, index=None):
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
            row_vals (dict): Contains the names of the data objects of
                collection as keys and the new row values as values.
            index (int): The index at which to insert the row. If None it will
                be appended to end of the collection.
        
        Raises:
            KeyError: If any of the keys don't exist.
            IndexError: If the index doesn't exist.
        """
        if index is not None and index > self.row_count:
            raise IndexError
        
        dataobj_keys = self.collectionTypes()
        vkeys = row_vals.keys()
        for k in vkeys:
            if not k in dataobj_keys:
                raise KeyError('ROW_DATA_TYPE ' + str(k) + 'is not in collection')

        
        temp_list = None
        try:
            # Need to make a deep copy of the data_object so we can reset them back
            # to the same place if there's a problem. That way we don't get the lists
            # in the different objects out of sync.
            temp_list = self._deepCopyDataObjects(self._collection) 
            
            for obj in self._collection:
                if not obj.data_type in vkeys:
                    if obj.default is not None:
                        obj.addValue(obj.default, index)
                    else:
                        raise ValueError
                else:
                    obj.addValue(row_vals[obj.data_type], index)
            
            if not self.checkRowsInSync():
                raise RuntimeError
            
        except (IndexError, ValueError, Exception):
            self._resetDataObject(temp_list)
            raise 
        except RuntimeError as err:
            logger.error('Collection not in sync!')
            logger.exception(err)
            self._resetDataObject(temp_list)
            logger.error('Collection reset to previous state')
            raise
        finally:
            if temp_list is not None:
                for o in temp_list:
                    del o
                del temp_list

        # Do this after so it's not removed if something goes wrong
        if self.has_dummy:
            self.deleteRow(0)
            self.has_dummy = False
    
    
    def deleteRow(self, index):
        """Delete a row from the collection.
        
        Args:
            index(int): the index to delete the values for.
        
        Raise:
            IndexError: if index is out of the bounds of the collection.
        """
        if index < 0 or index > self.row_count:
            raise IndexError
        
        try:
            # Need to make a deep copy of the data_object so we can reset them back
            # to the same place if there's a problem. That way we don't get the lists
            # in the different objects out of sync.
            temp_list = self._deepCopyDataObjects(self._collection) 
            
            for obj in self._collection:
                obj.deleteValue(index)
            
        except (IndexError, ValueError, Exception):
            self._resetDataObject(temp_list)
            raise 
        finally:
            for o in temp_list:
                del o
            del temp_list
        
        
    def collectionTypes(self): 
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
                
    
    def dataObjectCopy(self, name_key):
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
        
    
    def setDummyRow(self, row_vals):
        """Sets a special 'dummy row' as a placeholder until actual values.
        
        Sometimes it can be useful to have placeholder values in a collection.
        This is particularly true for FMP units that will cause errors in
        FMP if there is no data in the rows. 
        
        This method will add the dummy row data and set the self.has_dummy
        flag to True. When actual row data is added to the collection it will
        check the flag and delete the row if it's True.
        """
        self.addRow(row_vals)
        if self.has_dummy:
            self.deleteRow(0)
        self.has_dummy = True
               
    
    def numberOfRows(self):
        """Return the number of rows held in the collection
        
        Returns:
            int - number of rows in this collection.
        """
        if not self.checkRowsInSync():
            raise RuntimeError('RowCollection objects are not in sync')

        return len(self._collection[0])
    
    
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
    
    
    
    