"""

 Summary:
    Contains the HtbdyUnit class.
    This holds all of the data read in from the HTBDY units in the dat file.
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


class HtbdyUnit (AIsisUnit): 
    """Concrete implementation of AIsisUnit storing Isis HTBDY Unit data.

    Contains a reference to a rowdatacollection for storing and
    accessing all the row data. i.e. the stage-time data for the section.
    Methods for accessing the data in these objects and adding removing rows
    are available.
    
    See Also:
        AIsisUnit
    """
    UNIT_TYPE = 'Htbdy'
    CATEGORY = 'Boundary DS'
    FILE_KEY = 'HTBDY'


    def __init__(self): 
        """Constructor.
        
        Args:
            fileOrder (int): The location of this unit in the file.
        """
        AIsisUnit.__init__(self)

        # Fill in the header values these contain the data at the top of the
        # section, such as the unit name and labels.
        self.head_data = {'section_label': 'Htbdy', 'extending_method': 'EXTEND',
                          'interpolation': 'LINEAR', 'comment': '', 
                          'time_units': 'SECONDS', 'rowcount': 0} 

        self.unit_type = HtbdyUnit.UNIT_TYPE
        self.unit_category = HtbdyUnit.CATEGORY
        self.has_datarows = True
        self.has_ics = False
        self.unit_length = 0
        
        # Add the new row data types to the object collection
        # All of them must have type, output format, default value and position
        # in the row as the first variables in vars.
        # The others are DataType specific.
        self.row_collection = RowDataCollection()
        self.row_collection.initCollection(do.FloatData(0, rdt.ELEVATION, format_str='{:>10}', no_of_dps=3))
        self.row_collection.initCollection(do.FloatData(1, rdt.TIME, format_str='{:>10}', no_of_dps=3))

    
    def readUnitData(self, unit_data, file_line):
        """Reads the unit data into the geometry objects.
        
        Args:
            unit_data (list): The part of the isis dat file pertaining to 
                this section 
        
        See Also:
            AIsisUnit - readUnitData()
        """
        file_line = self._readHeadData(unit_data, file_line)
        self._name = self.head_data['section_label']
        file_line = self._readRowData(unit_data, file_line)
        self.head_data['rowcount'] = self.row_collection.getNumberOfRows()
        return file_line - 1

    def _readHeadData(self, unit_data, file_line):            
        """Reads the data in the file header section into the class.
        
        Args:
            unit_data (list): contains data for this unit.
        """
        self.head_data['comment'] = unit_data[file_line][5:].strip()
        self._name = self.head_data['section_label'] = unit_data[file_line + 1][:12].strip()
        self.unit_length = int(unit_data[file_line + 2][:10].strip())
        self.head_data['time_units'] = unit_data[file_line + 2][20:30].strip()
        self.head_data['extending_method'] = unit_data[file_line + 2][30:40].strip()
        self.head_data['interpolation'] = unit_data[file_line + 2][40:50].strip()
        return file_line + 3


    def _readRowData(self, unit_data, file_line):
        """Reads the units rows into the row collection.

        This is all the geometry data that occurs after the no of rows variable in
        the Spill Units of the dat file.
        
        Args:
            unit_data: the data pertaining to this unit.
        """ 
        out_line = file_line + self.unit_length
        try:
            # Load the geometry data
            for i in range(file_line, out_line):
                
                # Put the values into the respective data objects            
                # This is done based on the column widths set in the Dat file
                # for the spill section.
                self.row_collection.addValue(rdt.ELEVATION, unit_data[i][0:10].strip())
                self.row_collection.addValue(rdt.TIME, unit_data[i][10:20].strip())
                
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
        out_data.append('HTBDY ' + self.head_data['comment'])
        
        # Get the row with the section name and spill info from the formatter
        out_data.append('{:<12}'.format(self.head_data['section_label']))
        
        out_data.append('{:>10}'.format(self.head_data['rowcount']) + 
                        '{:>10}'.format(self.head_data['time_units']) +
                        '{:>10}'.format(self.head_data['extending_method']) +
                        '{:>10}'.format(self.head_data['interpolation'])
                        )
        
        return out_data
   
        
    def addDataRow(self, elevation, time=None, index=None): 
        """
        
        Args:
            elevation (float): elevation in datum.
            time=None(float): timestep value. if None it will be set to be the
                same increment as the previous.
            index=None(int): the position to insert the new row. If no value is 
                given it will be appended to the end of the data_object
        
        Raises:
            IndexError: If the index does not exist.
            ValueError: If the given value is not accepted by the DataObjects. 
            
        See Also:
            ADataObject and subclasses for information on the parameters.
        """
        if not index is None and index < 0:
            raise IndexError('Index value cannot be less than zero')
        if index == 1 and time is None:
            raise ValueError('Cannot determine timestep with only 1 previous value')
        
        # If it's the same as the record length then we can set index to None
        # type and it will be appended instead of inserted.
        num_rows = self.row_collection.getNumberOfRows()
        orig_index = index
        if index is None or index >= num_rows:
            index = num_rows
        else:
            t0 = self.row_collection.getDataValue(rdt.TIME, index)
            if not time is None and time < t0:
                raise ValueError('Time values must increase')
        
        if time is None:
            t1 = self.row_collection.getDataValue(rdt.TIME, index-1)
            t2 = self.row_collection.getDataValue(rdt.TIME, index-2)
            time = t1 + (t1 - t2)
        
        if orig_index is None:
            self.row_collection.addValue(rdt.TIME, time)
            self.row_collection.addValue(rdt.ELEVATION, elevation)
        else:
            self.row_collection.setValue(rdt.TIME, time, index)
            self.row_collection.setValue(rdt.ELEVATION, elevation, index)
        self.unit_length += 1
    
        