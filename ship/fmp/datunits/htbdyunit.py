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
from __future__ import unicode_literals

from ship.fmp.datunits.isisunit import AUnit
from ship.fmp.datunits import ROW_DATA_TYPES as rdt
from ship.data_structures import dataobject as do
from ship.data_structures.rowdatacollection import RowDataCollection 
from ship.utils import utilfunctions as uf
from ship.fmp.headdata import HeadDataItem
from ship.data_structures import DATA_TYPES as dt

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class HtbdyUnit (AUnit): 
    """Concrete implementation of AUnit storing Isis HTBDY Unit data.

    Contains a reference to a rowdatacollection for storing and
    accessing all the row data. i.e. the stage-time data for the section.
    Methods for accessing the data in these objects and adding removing rows
    are available.
    
    See Also:
        AUnit
    """
    UNIT_TYPE = 'htbdy'
    UNIT_CATEGORY = 'boundary_ds'
    FILE_KEY = 'HTBDY'
    FILE_KEY2 = None


    def __init__(self, **kwargs): 
        """Constructor.
        
        Args:
            fileOrder (int): The location of this unit in the file.
        """
        AUnit.__init__(self, **kwargs)
        
        self._unit_type = HtbdyUnit.UNIT_TYPE
        self._unit_category = HtbdyUnit.UNIT_CATEGORY
        self._name = 'Htbd'
        
        time_units = (
            'SECONDS', 'MINUTES', 'HOURS', 'DAYS', 'WEEKS', 'FORTNIGHTS',
            'LUNAR MONTHS', 'MONTHS', 'QUARTERS', 'YEARS', 'DECADES', 'USER SET',
        )
        self.head_data = {
            'comment': HeadDataItem('', '', 0, 1, dtype=dt.STRING),
            'multiplier': HeadDataItem(1.000, '{:>10}', 0, 1, dtype=dt.FLOAT, dps=3),
            'time_units': HeadDataItem('HOURS', '{:>10}', 2, 0, dtype=dt.CONSTANT, choices=time_units),
            'extending_method': HeadDataItem('EXTEND', '{:>10}', 2, 0, dtype=dt.CONSTANT, choices=('EXTEND', 'NOEXTEND', 'REPEAT')),
            'interpolation': HeadDataItem('LINEAR', '{:>10}', 2, 0, dtype=dt.CONSTANT, choices=('LINEAR', 'SPLINE')),
        }
        
        dobjs = [
            do.FloatData(0, rdt.ELEVATION, format_str='{:>10}', no_of_dps=3),
            do.FloatData(1, rdt.TIME, format_str='{:>10}', no_of_dps=3, update_callback=self.checkIncreases),
        ]
        self.row_data['main'] = RowDataCollection.bulkInitCollection(dobjs)


    def icLabels(self):
        return [] #[self._name]
    
    def readUnitData(self, unit_data, file_line):
        """Reads the unit data into the geometry objects.
        
        Args:
            unit_data (list): The part of the isis dat file pertaining to 
                this section 
        
        See Also:
            AUnit - readUnitData()
        """
        file_line, rows = self._readHeadData(unit_data, file_line)
        file_line = self._readRowData(unit_data, file_line, rows)
        return file_line - 1

    def _readHeadData(self, unit_data, file_line):            
        """Reads the data in the file header section into the class.
        
        Args:
            unit_data (list): contains data for this unit.
        """
        self.head_data['comment'].value = unit_data[file_line][5:].strip()
        self._name = unit_data[file_line + 1][:12].strip()

        l = unit_data[file_line+2]
        rows = 1
        if 'LUNAR MONTHS' in l:
            l = l.replace('LUNAR MONTHS', 'LUNAR-MONTHS')
            l = ' '.join(l.split())
            vars = l.split()
            vars[1] = 'LUNAR MONTHS'
        else:
            l = ' '.join(l.split())
            vars = l.split()

        rows = int(vars[0])
        if uf.isNumeric(vars[1]):
            self.head_data['time_units'].value = 'USER SET'
            self.head_data['multiplier'].value = vars[1]
        else:
            self.head_data['time_units'].value = vars[1]
        
        self.head_data['extending_method'].value = vars[2] 
        self.head_data['interpolation'].value = vars[3] 

        return file_line + 3, rows


    def _readRowData(self, unit_data, file_line, rows):
        """Reads the units rows into the row collection.

        This is all the geometry data that occurs after the no of rows variable in
        the Spill Units of the dat file.
        
        Args:
            unit_data: the data pertaining to this unit.
        """ 
        out_line = file_line + rows
        try:
            # Load the geometry data
            for i in range(file_line, out_line):
                elev   = unit_data[i][0:10].strip()
                time   = unit_data[i][10:20].strip()
                
                self.row_data['main'].addRow({
                    rdt.ELEVATION: elev, rdt.TIME: time
                })
                
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
        for i in range(0, self.row_data['main'].numberOfRows()): 
            out_data.append(self.row_data['main'].getPrintableRow(i))
        
        return out_data
   
  
    def _getHeadData(self):
        """Get the header data formatted for printing out.
        
        This is a bit messy because the formatting changes depending on what
        the setting of 'time_units' is. If it LUNAR MONTHS it takes 12 spaces,
        while all others take 10. It can also be the float value in 'multiplier'
        if 'time_units' is set to USER SET....gaaarrrggghhhhhh.
        
        Returns:
            list - contining the formatted head data.
        """
        out = ['HTBDY ' + self.head_data['comment'].value]
        out.append('\n' + '{:<12}'.format(self._name))
        out.append('\n' + '{:>10}'.format(self.row_data['main'].numberOfRows()))

        out.append('{:<10}'.format('')) # There's a weired blank column

        units = self.head_data['time_units'].value
        if units == 'USER SET':
            out.append(self.head_data['multiplier'].format())
        elif units == 'LUNAR MONTHS':
            out.append('{:>12}'.format(self.head_data['time_units'].value))
        else:
            out.append(self.head_data['time_units'].format())
        out.append(self.head_data['extending_method'].format())
        out.append(self.head_data['interpolation'].format())
        
        final_out = ''.join(out).split('\n')
        return final_out
            
   
#     def addDataRow(elevation, time=None, index=None): 
    def addRow(self, row_vals, data_key='main', index=None):
        """
        
        Args:
        
        Raises:
            IndexError: If the index does not exist.
            ValueError: If the given value is not accepted by the DataObjects. 
            
        See Also:
            ADataObject and subclasses for information on the parameters.
        """
        if not rdt.ELEVATION in row_vals.keys():
            raise AttributeError('row_vals must contain an ELEVATION value')
        
        elevation = row_vals.get(rdt.ELEVATION, None)
        time = row_vals.get(rdt.TIME, None)

        if index is not None and index < 0:
            raise IndexError('Index value cannot be less than zero')
        if index == 1 and time is None:
            raise ValueError('Cannot determine timestep with only 1 previous value')
        
        # If it's the same as the record length then we can set index to None
        # type and it will be appended instead of inserted.
        num_rows = self.row_data['main'].numberOfRows()
        orig_index = index
        if index is None or index >= num_rows:
            index = num_rows
        
        if time is None:
            temp = index
            if index == num_rows: temp = index - 1
            t1 = self.row_data['main'].dataValue(rdt.TIME, temp)
            t2 = self.row_data['main'].dataValue(rdt.TIME, temp-1)
            time = t1 + (t1 - t2)
        
        if orig_index is None:
            self.row_data['main'].addRow({rdt.TIME: time, 
                                          rdt.ELEVATION: elevation})
        else:
            self.row_data['main'].addRow({rdt.TIME: time, 
                                             rdt.ELEVATION: elevation}, index)
    
        