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
from __future__ import unicode_literals

from ship.isis.datunits.isisunit import AIsisUnit
from ship.isis.datunits import ROW_DATA_TYPES as rdt
from ship.data_structures import dataobject as do
from ship.data_structures.rowdatacollection import RowDataCollection 
from ship.isis.headdata import HeadDataItem
from ship.data_structures import DATA_TYPES as dt

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
    UNIT_TYPE = 'spill'
    UNIT_CATEGORY = 'spill'
    FILE_KEY = 'SPILL'
    FILE_KEY2 = None


    def __init__(self): 
        """Constructor.
        
        Args:
            fileOrder (int): The location of this unit in the file.
        """
        AIsisUnit.__init__(self)

        self._name = 'Spl'
        self._name_ds = 'SplDS'
        self.head_data = {
            'comment': HeadDataItem('', '', 0, 1, dtype=dt.STRING),
            'weir_coef': HeadDataItem(1.700, '{:>10}', 1, 0, dtype=dt.FLOAT, dps=3),
            'modular_limit': HeadDataItem(0.700, '{:>10}', 1, 2, dtype=dt.FLOAT, dps=3),
        }

        self._unit_type = SpillUnit.UNIT_TYPE
        self._unit_category = SpillUnit.UNIT_CATEGORY
        
        dobjs = [
            do.FloatData(0, rdt.CHAINAGE, format_str='{:>10}', no_of_dps=3, update_callback=self.checkIncreases),
            do.FloatData(1, rdt.ELEVATION, format_str='{:>10}', no_of_dps=3),
            do.FloatData(2, rdt.EASTING, format_str='{:>10}', no_of_dps=2, default=0.00),
            do.FloatData(3, rdt.NORTHING, format_str='{:>10}', no_of_dps=2, default=0.00),
        ]
        self.row_data['main'] = RowDataCollection.bulkInitCollection(dobjs)


    def icLabels(self):
        return [self._name, self._name_ds]

    
    def readUnitData(self, unit_data, file_line):
        """Reads the unit data into the geometry objects.
        
        Args:
            unit_data (list): The part of the isis dat file pertaining to 
                this section 
        
        See Also:
            AIsisUnit - readUnitData()
        """
        file_line = self._readHeadData(unit_data, file_line)
        file_line = self._readRowData(unit_data, file_line)
        return file_line - 1

    def _readHeadData(self, unit_data, file_line):            
        """Reads the data in the file header section into the class.
        
        Args:
            unit_data (list): contains data for this unit.
        """
        self.head_data['comment'].value = unit_data[file_line][5:].strip()
        self._name = unit_data[file_line + 1][:12].strip()
        self._name_ds = unit_data[file_line + 1][12:24].strip()
        self.head_data['weir_coef'].value = unit_data[file_line + 2][:10].strip()
        self.head_data['modular_limit'].value = unit_data[file_line + 2][10:20].strip()
        return file_line + 3


    def _readRowData(self, unit_data, file_line):
        """Reads the units rows into the row collection.

        This is all the geometry data that occurs after the no of rows variable in
        the Spill Units of the dat file.
        
        Args:
            unit_data: the data pertaining to this unit.
        """ 
        self.unit_length = int(unit_data[file_line].strip())
        file_line += 1
        out_line = file_line + self.unit_length
        try:
            # Load the geometry data
            for i in range(file_line, out_line):
                
                # Put the values into the respective data objects            
                # This is done based on the column widths set in the Dat file
                # for the spill section.
                self.row_data['main'].addValue(rdt.CHAINAGE, unit_data[i][0:10].strip())
                self.row_data['main'].addValue(rdt.ELEVATION, unit_data[i][10:20].strip())
                
                # In some edge cases there are no values set in the file for the
                # easting and northing, so use defaults. this actually checks 
                # that they are both there, e starts at 21, n starts at 31
                if not len(unit_data[i]) > 31:
                    self.row_data['main'].addValue(rdt.EASTING)
                    self.row_data['main'].addValue(rdt.NORTHING)
                else:
                    self.row_data['main'].addValue(rdt.EASTING, unit_data[i][20:30].strip())
                    self.row_data['main'].addValue(rdt.NORTHING, unit_data[i][30:40].strip())
                
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
        num_rows = self.row_data['main'].numberOfRows()
        out_data = self._getHeadData(num_rows)
        out_data.extend(self._getRowData(num_rows)) 
        
        return out_data
  
  
    def _getRowData(self, num_rows):
        """Get the data in the row collection.
        
        For all the rows in the spill geometry section get the data from
        the rowdatacollection class.
        
        Returns:
            list containing the formatted unit rows.
        """
        out_data = []
        for i in range(0, num_rows): 
            out_data.append(self.row_data['main'].getPrintableRow(i))
        
        return out_data
   
  
    def _getHeadData(self, num_rows):
        """Get the header data formatted for printing out.
        
        Returns:
            list - contining the formatted head data.
        """
        out = []
        out.append('SPILL ' + self.head_data['comment'].value)
        out.append('{:<12}'.format(self._name) + '{:<12}'.format(self._name_ds))
        out.append(self.head_data['weir_coef'].format() + self.head_data['modular_limit'].format())
        out.append('{:>10}'.format(num_rows))
        return out
        
#     def addDataRow(self, chainage, elevation, index=None, easting = 0.00, northing = 0.00): 
    def addDataRow(self, row_vals, rowdata_key='main', index=None):
        """Adds a new row to the spill unit.

        Ensures that certain requirements of the data rows, such as the 
        chainage needing to increase for each row down are met, then call the 
        addNewRow() method in the row_collection.
        
        Args:
            row_vals(Dict): keys must be datunits.ROW_DATA_TYPES with a legal
                value assigned for the DataType. Chainage and Elevation MUST
                be included.
            index=None(int): the row to insert into. The existing row at the
                given index will be moved up by one.

        Returns:
            False if the addNewRow() method is unsuccessful.
        
        Raises:
            IndexError: If the index does not exist.
            ValueError: If the given value is not accepted by the DataObjects. 
            
        See Also:
            ADataObject and subclasses for information on the parameters.
        """
        keys = row_vals.keys()
        if not rdt.CHAINAGE in keys or not rdt.ELEVATION in keys:
            raise AttributeError('row_vals must include CHAINAGE and ELEVATION.')
        
        # Call superclass method to add the new row
        AIsisUnit.addRow(self, row_vals, index=index)
        
    
        