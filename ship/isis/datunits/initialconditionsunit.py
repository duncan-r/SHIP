"""

 Summary:
    Contains the InitialConditionsUnit class.
    This is a holder for all of the data in the initial conditions section
    of the dat file.

 Author:  
     Duncan Runnacles

 Created:  
     01 Apr 2016

 Copyright:  
     Duncan Runnacles 2016

 TODO:
    Not fully implemented at the moment - see class TODO comment for details.

 Updates:

"""


from ship.isis.datunits.isisunit import AIsisUnit
from ship.data_structures.rowdatacollection import RowDataCollection
from ship.data_structures import dataobject as do
from ship.isis.datunits import ROW_DATA_TYPES as rdt

import logging
logger = logging.getLogger(__name__)

class InitialConditionsUnit (AIsisUnit):
    """isisunit for storing the initial conditions.

    Stores the initial conditions data; near the end of the .dat file.
    """
    
    # Class constants
    UNIT_TYPE = 'Initial Conditions'
    CATEGORY = 'Initial Conditions'
    FILE_KEY = 'INITIAL'
    

    def __init__(self, node_count):
        """Constructor

        Args:
            node_count (int): The number of nodes in the model. We need this to 
                know how many lines there are to read from the contents list.
            fileOrder (int): The location of the initial conditions in the 
                .DAT file. This will always be at the end but before the 
                GISINFO if there is any.
        """
        AIsisUnit.__init__(self)
        self.unit_type = "Initial Conditions"
        self.unit_category = "Initial Conditions"
        self._name = "Initial Conditions"
        self.has_datarows = True
        self.has_ics = False
        self.node_count = node_count
        
        self.row_collection = RowDataCollection()
        self.row_collection.initCollection(do.StringData(0, rdt.LABEL, format_str='{:<12}'))
        self.row_collection.initCollection(do.StringData(1, rdt.QMARK, format_str='{:>2}', default='y'))
        self.row_collection.initCollection(do.FloatData(2, rdt.FLOW, format_str='{:>10}', no_of_dps=3))
        self.row_collection.initCollection(do.FloatData(3, rdt.STAGE, format_str='{:>10}', no_of_dps=3))
        self.row_collection.initCollection(do.FloatData(4, rdt.FROUDE_NO, format_str='{:>10}', no_of_dps=3))
        self.row_collection.initCollection(do.FloatData(5, rdt.VELOCITY, format_str='{:>10}', no_of_dps=3))
        self.row_collection.initCollection(do.FloatData(6, rdt.UMODE, format_str='{:>10}', no_of_dps=3))
        self.row_collection.initCollection(do.FloatData(7, rdt.USTATE, format_str='{:>10}', no_of_dps=3))
        self.row_collection.initCollection(do.FloatData(8, rdt.ELEVATION, format_str='{:>10}', no_of_dps=3))
    
    
    def readUnitData(self, unit_data, file_line):
        """
        """
        i = file_line
        out_line = file_line + self.node_count + 2
        for i in range(file_line, out_line):
            if i < file_line + 2: continue  # Skip the first couple of header lines
            
            self.row_collection.addValue(rdt.LABEL, unit_data[i][0:12].strip())
            self.row_collection.addValue(rdt.QMARK, unit_data[i][12:14].strip())
            self.row_collection.addValue(rdt.FLOW, unit_data[i][14:24].strip())
            self.row_collection.addValue(rdt.STAGE, unit_data[i][24:34].strip())
            self.row_collection.addValue(rdt.FROUDE_NO, unit_data[i][34:44].strip())
            self.row_collection.addValue(rdt.VELOCITY, unit_data[i][44:54].strip())
            self.row_collection.addValue(rdt.UMODE, unit_data[i][54:64].strip())
            self.row_collection.addValue(rdt.USTATE, unit_data[i][64:74].strip())
            self.row_collection.addValue(rdt.ELEVATION, unit_data[i][74:84].strip())
            
        return out_line - 1
       
    
    def getData(self):
        """
        """
        out_data = []
        out_data.append('INITIAL CONDITIONS')
        out_data.append(' label   ?      flow     stage froude no  velocity     umode    ustate         z')
        for i in range(0, self.row_collection.getNumberOfRows()): 
            out_data.append(self.row_collection.getPrintableRow(i))
        
        return out_data
    
    
    
    def updateDataRow(self, row_vals, index):
        """Updates the row at the given index in the row_collection.
        
        Changes the state of the values in the initial conditions list of 
        the .dat file at the given index.

        Args:
            row_vals(Dict): keys must be datunits.ROW_DATA_TYPES with a legal
                value assigned for the DataType. Chainage and Elevation MUST
                be included.
            index: the row to update. 

        Raises:
            IndexError: If the index does not exist.
            ValueError: If the given value is not accepted by the DataObject's. 
            
        See Also:
            ADataObject and subclasses for information on the parameters.
        """
        
        # Call superclass method to add the new row
        AIsisUnit.updateDataRow(self, row_vals=row_vals, index=index)
        

    def updateDataRowByName(self, row_vals, name):
        """Updates the row for the entry with the give name.
        
        Changes the state of the values in the initial conditions list for the
        the .dat file for the unit with the given name.

        Args:
            row_vals(Dict): keys must be datunits.ROW_DATA_TYPES with a legal
                value assigned for the DataType. Chainage and Elevation MUST
                be included.
            name: the name of the unit who's ic's should be updated.

        Raises:
            IndexError: If the index does not exist.
            ValueError: If the given value is not accepted by the DataObject's. 
            AttributeError: If the given name doesn't exists in the collection.
            
        See Also:
            ADataObject and subclasses for information on the parameters.
        """
        index = 0
        labels = self.row_collection.getRowDataAsList(rdt.LABEL)
        index = labels.index(name)
        if index == -1:
            raise AttributeError
        
        # Call superclass method to add the new row
        AIsisUnit.updateDataRow(self, row_vals=row_vals, index=index)
    

    def addDataRow(self, row_vals): 
        """Adds a new row to the InitialCondition units row_collection.
        
        The new row will be added at the given index. If no index is given it
        will be appended to the end of the collection.
        
        If no LABEL value is given a AttributeError will be raised as it 
        cannot have a default value. All other values can be ommitted. If they 
        are they will be given defaults.
        
        Examples:
            >>> import ship.isis.datunits.ROW_DATA_TYPES as rdt
            >>> ics.addDataRow({rdt.LABEL:UNITNAME, rdt.STAGE:10.2}, index=4)

        Args:
            row_vals(Dict): keys must be datunits.ROW_DATA_TYPES with a legal
                value assigned for the DataType. Chainage and Elevation MUST
                be included.

        Raises:
            AttributeError: If LABEL is not given.
            IndexError: If the index does not exist.
            ValueError: If the given value is not accepted by the DataObject's. 
            
        See Also:
            ADataObject and subclasses for information on the parameters.
        """
        if not rdt.LABEL in row_vals.keys(): 
            logger.error('Required values of LABEL not given')
            raise  AttributeError ("Required value 'LABEL' not given") 
        
        # Don't add the same ic's in twice
        labels = self.row_collection.getRowDataAsList(rdt.LABEL)
        if row_vals[rdt.LABEL] in labels:
            return

        # Setup default values for arguments that aren't given
        kw={}
        kw[rdt.LABEL] = row_vals.get(rdt.LABEL)
        kw[rdt.QMARK] = row_vals.get(rdt.QMARK, 'y')
        kw[rdt.FLOW] = row_vals.get(rdt.FLOW, 0.000)
        kw[rdt.STAGE] = row_vals.get(rdt.STAGE, 0.000)
        kw[rdt.FROUDE_NO] = row_vals.get(rdt.FROUDE_NO, 0.000)
        kw[rdt.VELOCITY] = row_vals.get(rdt.VELOCITY, 0.000)
        kw[rdt.UMODE] = row_vals.get(rdt.UMODE, 0.000)
        kw[rdt.USTATE] = row_vals.get(rdt.USTATE, 0.000)
        kw[rdt.ELEVATION] = row_vals.get(rdt.ELEVATION, 0.000)

        # Call superclass method to add the new row
        AIsisUnit.addDataRow(self, index=None, row_vals=kw, check_negative=False)
        self.node_count += 1
    

    def deleteDataRowByName(self, section_name):
        """Delete one of the RowDataCollection objects in the row_collection.
        
        This calls the AIsisUnit deleteDataRow method, but obtains the index
        of the row to be deleted from the name first.
        
        Args:
            section_name(str): the name of the AIsisUnit to be removed from
                the initial conditions.
        
        Raises:
            KeyError - if section_name does not exist.
        """
        labels = self.row_collection.getRowDataAsList(rdt.LABEL)
        index = labels.index(section_name)
        
        if index == -1:
            raise KeyError('Name does not exist in initial conditions: ' + str(section_name))
        
        self.deleteDataRow(index)
        self.node_count -= 1
    
    
    def getRowByName(self, section_name):
        """Get the data vals in a particular row by name.
        
        This is the same functionality as the AIsisUnit's getRow(int) method
        which returns a row in the RowDataCollection by the index value given.
        In this case it will find the index based on the section label and 
        return the same dictionary of row values.
        
        Args:
            section_name(str): the name of the AIsisUnit to be removed from
                the initial conditions.
            
        Return:
            dict - containing the values for the requested row.
        """
        labels = self.row_collection.getRowDataAsList(rdt.LABEL)
        index = labels.index(section_name)
        
        if index == -1:
            raise AttributeError('Name does not exist in initial conditions: ' + str(section_name))
        
        return self.getRow(index)

        
        
        
        
    
