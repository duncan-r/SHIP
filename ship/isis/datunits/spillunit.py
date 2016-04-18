"""

 Summary:
    Contains the SpillUnit class.
    This holds all of the data read in from the spill units in the dat file.
    Can be called to load in the data and read and update the contents 
    held in the object.

 Author:  
     Duncan R.

  Created:  
     01 Apr 2016

 Copyright:  
     Duncan Runnacles 2016

 TODO:

 Updates:

"""

from ship.isis.datunits.isisunit import AIsisUnit
from ship.isis.datunits import ROW_DATA_TYPES as rdt
from ship.data_structures import dataobject as do
from ship.data_structures.rowdatacollection import RowDataCollection 

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class SpillUnit (AIsisUnit): 
    """Concrete implementation of AIsisUnit storing Isis Spill Unit data.

    Contains a reference to a rowdatacollection for storing and
    accessing all the row data. i.e. the geometry data for the section,
    containing the chainage, elevation, etc values.
    Methods for accessing the data in these objects and adding removing rows
    are available.
    
    See Also:
        AIsisUnit
    """
    
    # Name constants the values dictionary
    CHAINAGE = 'chainage'
    ELEVATION = 'elevation'
    EASTING = 'easting'
    NORTHING = 'northing'
    
    UNIT_TYPE = 'Spill'
    CATEGORY = 'Spill'
    FILE_KEY = 'SPILL'


    def __init__(self, file_order): 
        """Constructor.
        
        Args:
            fileOrder (int): The location of this unit in the file.
        """
        AIsisUnit.__init__(self, file_order)

        # Fill in the header values these contain the data at the top of the
        # section, such as the unit name and labels.
        self.head_data = {'section_label': '', 'spill_ds': '', 'coeff': 0, 
                          'modular_limit': 0, 'comment': '', 'rowcount': 0} 

        self.unit_type = SpillUnit.UNIT_TYPE
        self.unit_category = SpillUnit.CATEGORY
        self.has_datarows = True
        self.unit_length = 0

    
    def readUnitData(self, unit_data, file_line):
        """Reads the unit data into the geometry objects.
        
        Args:
            unit_data (list): The part of the isis dat file pertaining to 
                this section 
        
        See Also:
            AIsisUnit - readUnitData()
        """
        file_line = self._readHeadData(unit_data, file_line)
        self.name = self.head_data['section_label']
        file_line = self._readRowData(unit_data, file_line)
        self.head_data['rowcount'] = self.row_collection.getNumberOfRows()
        return file_line - 1

    def _readHeadData(self, unit_data, file_line):            
        """Reads the data in the file header section into the class.
        
        Args:
            unit_data (list): contains data for this unit.
        """
        self.head_data['comment'] = unit_data[file_line][5:].strip()
        self.name = self.head_data['section_label'] = unit_data[file_line + 1][:12].strip()
        self.head_data['spill_ds'] = unit_data[file_line + 1][12:24].strip()
        self.head_data['coeff'] = unit_data[file_line + 2][:10].strip()
        self.head_data['modular_limit'] = unit_data[file_line + 2][10:20].strip()
        self.unit_length = int(unit_data[file_line + 3].strip())
        return file_line + 4


    def _readRowData(self, unit_data, file_line):
        """Reads the units rows into the row collection.

        This is all the geometry data that occurs after the no of rows variable in
        the Spill Units of the dat file.
        
        Args:
            unit_data: the data pertaining to this unit.
        """ 
        # Add the new row data types to the object collection
        # All of them must have type, output format, default value and position
        # in the row as the first variables in vars.
        # The others are DataType specific.
        self.row_collection = RowDataCollection()
        self.row_collection.initCollection(do.FloatData(0, rdt.CHAINAGE, format_str='{:>10}', no_of_dps=3))
        self.row_collection.initCollection(do.FloatData(1, rdt.ELEVATION, format_str='{:>10}', no_of_dps=3))
        self.row_collection.initCollection(do.FloatData(2, rdt.EASTING, format_str='{:>10}', no_of_dps=2, default=0.0))
        self.row_collection.initCollection(do.FloatData(3, rdt.NORTHING, format_str='{:>10}', no_of_dps=2, default=0.0))

        out_line = file_line + self.unit_length
        try:
            # Load the geometry data
            for i in range(file_line, out_line):
                
                # Put the values into the respective data objects            
                # This is done based on the column widths set in the Dat file
                # for the spill section.
                self.row_collection.addValue(rdt.CHAINAGE, unit_data[i][0:10].strip())
                self.row_collection.addValue(rdt.ELEVATION, unit_data[i][10:20].strip())
                
                # In some edge cases there are no values set in the file for the
                # easting and northing, so use defaults.
                if not len(unit_data[i]) > 21:
                    self.row_collection.addValue(rdt.EASTING)
                    self.row_collection.addValue(rdt.NORTHING)
                else:
                    self.row_collection.addValue(rdt.EASTING, unit_data[i][20:30].strip())
                    self.row_collection.addValue(rdt.NORTHING, unit_data[i][30:40].strip())
                
        except NotImplementedError:
            logger.ERROR('Unable to read Unit Data(dataRowObject creation) - NotImplementedError')
            raise
            
        return out_line
    

    def getData(self): 
        """Retrieve the data in this unit.

        The String[] returned is formatted for printing in the fashion
        of the .dat file.
        
        Returns:
            list of output data formated the same as in the .DAT file.
        """
        out_data = self._getHeadData()
        out_data.extend(self._getRowData()) 
        
        return out_data
  
  
    def _getRowData(self):
        """Get the data in the row collection.
        
        For all the rows in the spill geometry section get the data from
        the rowdatacollection class.
        
        Returns:
            list containing the formatted unit rows.
        """
        out_data = []
        for i in range(0, self.row_collection.getNumberOfRows()): 
            out_data.append(self.row_collection.getPrintableRow(i))
        
        return out_data
   
  
    def _getHeadData(self):
        """Get the header data formatted for printing out.
        
        Returns:
            list - contining the formatted head data.
        """
        out_data = []
        self.head_data['rowcount'] = self.unit_length
        out_data.append('SPILL ' + self.head_data['comment'])
        
        # Get the row with the section name and spill info from the formatter
        out_data.append('{:<12}'.format(self.head_data['section_label']) + 
                        '{:<12}'.format(self.head_data['spill_ds'])
                        )
        
        out_data.append('{:>10}'.format(self.head_data['coeff']) + 
                        '{:>10}'.format(self.head_data['modular_limit'])
                        )
        out_data.append('{:>10}'.format(self.head_data['rowcount']))
        
        return out_data
   
        
    def addDataRow(self, chainage, elevation, index=None, easting = 0.00, 
                                                        northing = 0.00): 
        """Adds a new row to the bridge unit.

        Ensures that certain requirements of the data rows, such as the 
        chainage needing to increase for each row down are met, then call the 
        addNewRow() method in the row_collection.
        
        Args:
            chainage (float): chainage value. Must not be less than the
                previous chaninage in the collection.
            elevation (float): elevation in datum.
            index (int): stating the position to insert the new row - Optional. 
                If no value is given it will be appended to the end of the 
                data_object
            
            The other values are all optional and will be set to defaults if
            not given.

        Returns:
            False if the addNewRow() method is unsuccessful.
        
        Raises:
            IndexError: If the index does not exist.
            ValueError: If the given value is not accepted by the DataObjects. 
            
        See Also:
            ADataObject and subclasses for information on the parameters.
        """
        
        # If it greater than the record length then raise an index error
        if index > self.row_collection.getNumberOfRows():
            raise IndexError ('Given index out of bounds of row_collection')
        # If it's the same as the record length then we can set index to None
        # type and it will be appended instead of inserted.
        if index == self.row_collection.getNumberOfRows():
            index = None
        # Check that there won't be a negative change in chainage across row.
        if self._checkChainageIncreaseNotNegative(index, chainage) == False:
            raise ValueError ('Chainage increase cannot be negative')

        # Call the row collection add row method to add the new row.
        self.row_collection.addNewRow(values_dict={'chainage': chainage, 
                'elevation': elevation, 'easting': easting, 
                'northing': northing}, index=index)
    
    
    def _checkChainageIncreaseNotNegative(self, index, chainageValue):
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
        if index == None:
            return True
        
        if not index == 0:
            if self.row_collection.getDataValue('chainage', index - 1) >= chainageValue:
                return False
        
        if self.row_collection.getDataValue('chainage', index) <= chainageValue:
            return False
            
        return True
        
        