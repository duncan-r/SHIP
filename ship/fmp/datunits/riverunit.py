"""

 Summary:
    Contains the RiverUnit class.
    This holds all of the data read in from the river units in the dat file.
    Can be called to load in the data and read and update the contents 
    held in the object.

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

from ship.fmp.datunits.isisunit import AUnit
from ship.datastructures import dataobject as do
from ship.datastructures.rowdatacollection import RowDataCollection 
from ship.fmp.datunits import ROW_DATA_TYPES as rdt
from ship.fmp.headdata import HeadDataItem
from ship.datastructures import DATA_TYPES as dt

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class RiverUnit (AUnit): 
    """Concrete implementation of AUnit storing Isis River Unit
    data.

    Contains a reference to a rowdatacollection for storing and
    accessing all the row data. i.e. the geometry data for the section,
    containing the chainage, elevation, roughness, etc values.

    Methods for accessing the data in these objects and adding removing rows
    are available.
    
    See Also:
        AUnit
    """
    
    UNIT_TYPE = 'river'
    UNIT_CATEGORY = 'river'
    FILE_KEY = 'RIVER'
    FILE_KEY2 = 'SECTION'


    def __init__(self, **kwargs): 
        """Constructor.
        
        Args:
            fileOrder (int): The location of this unit in the file.
            reach_number (int): The reach ID for this unit.
        """
        AUnit.__init__(self, **kwargs)

        self._unit_type = RiverUnit.UNIT_TYPE
        self._unit_category = RiverUnit.UNIT_CATEGORY
        if self._name == 'unknown': self._name = 'RivUS'

        self.reach_number = kwargs.get('reach_number', -1)
        
        self.head_data = {
            'comment': HeadDataItem('', '', 0, 1, dtype=dt.STRING),
            'spill1': HeadDataItem('', '{:<12}', 2, 3, dtype=dt.STRING),
            'spill2': HeadDataItem('', '{:<12}', 2, 4, dtype=dt.STRING),
            'lateral1': HeadDataItem('', '{:<12}', 2, 6, dtype=dt.STRING),
            'lateral2': HeadDataItem('', '{:<12}', 2, 7, dtype=dt.STRING),
            'lateral3': HeadDataItem('', '{:<12}', 2, 8, dtype=dt.STRING),
            'lateral4': HeadDataItem('', '{:<12}', 2, 9, dtype=dt.STRING),
            'distance': HeadDataItem(0.0, '{:>10}', 3, 0, dtype=dt.FLOAT, dps=3),
            'slope': HeadDataItem(0.0001, '{:>20}', 3, 1, dtype=dt.FLOAT, dps=4),
            'density': HeadDataItem(1000, '{:>10}', 3, 2, dtype=dt.INT),
        }
        
        '''
            Add the new row data types to the object collection
            All of them must have type, output format, and position
            in the row all other arguments are excepted as **kwargs.
        '''
        dobjs = [
            # update_callback is called every time a value is added or updated
            do.FloatData(rdt.CHAINAGE, format_str='{:>10}', no_of_dps=3, update_callback=self.checkIncreases),
            do.FloatData(rdt.ELEVATION, format_str='{:>10}', no_of_dps=3),
            do.FloatData(rdt.ROUGHNESS, format_str='{:>10}', default=0.039, no_of_dps=3),
            do.SymbolData(rdt.PANEL_MARKER, '*', format_str='{:<5}', default=False),
            do.FloatData(rdt.RPL, format_str='{:>5}', default=1.000, no_of_dps=3),
            do.ConstantData(rdt.BANKMARKER, ('', 'LEFT', 'RIGHT', 'BED'), format_str='{:<10}', default=''),
            do.FloatData(rdt.EASTING, format_str='{:>10}', default=0.0, no_of_dps=2),
            do.FloatData(rdt.NORTHING, format_str='{:>10}', default=0.0, no_of_dps=2),
            do.ConstantData(rdt.DEACTIVATION, ('', 'LEFT', 'RIGHT'), format_str='{:<10}', default=''),
            # Default == '~' means to ignore formatting and apply '' when value is None
            do.StringData(rdt.SPECIAL, format_str='{:<10}', default='~'),
        ]
        self.row_data['main'] = RowDataCollection.bulkInitCollection(dobjs)
        self.row_data['main'].setDummyRow({rdt.CHAINAGE: 0, rdt.ELEVATION:0, rdt.ROUGHNESS: 0})
    
    
    def icLabels(self):
        """Overriddes superclass method."""
        return [self._name]
    
    def linkLabels(self):
        """Overriddes superclass method."""
        out = {'name': self.name}
        for k, v in self.head_data.items():
            if 'spill' in k or 'lateral' in k:
                out[k] = v.value
        return out

        
    def readUnitData(self, unit_data, file_line):
        """Reads the unit data into the geometry objects.
        
        See Also:
            AUnit - readUnitData for more information.
        
        Args:
            unit_data (list): The section of the isis dat file pertaining 
                to this section 
        """
        file_line = self._readHeadData(unit_data, file_line)
        file_line = self._readRowData(unit_data, file_line) 
        return file_line - 1
        

    def _readHeadData(self, unit_data, file_line):            
        """Format the header data for writing to file.
        
        Args:
            unit_data (list): containing the data to read.
        """
        self.head_data['comment'].value = unit_data[file_line + 0][5:].strip()
        self._name = unit_data[file_line + 2][:12].strip()
        self.head_data['spill1'].value = unit_data[file_line + 2][12:24].strip()
        self.head_data['spill2'].value = unit_data[file_line + 2][24:36].strip()
        self.head_data['lateral1'].value = unit_data[file_line + 2][36:48].strip()
        self.head_data['lateral2'].value = unit_data[file_line + 2][48:60].strip()
        self.head_data['lateral3'].value = unit_data[file_line + 2][60:72].strip()
        self.head_data['lateral4'].value = unit_data[file_line + 2][72:84].strip()
        self.head_data['distance'].value = unit_data[file_line + 3][0:10].strip()
        self.head_data['slope'].value = unit_data[file_line + 3][10:30].strip()
        self.head_data['density'].value = unit_data[file_line + 3][30:40].strip()

        return file_line + 4

    def _readRowData(self, unit_data, file_line):
        """Reads the units rows into the row collection.

        This is all the geometry data that occurs after the no of rows variable in
        the River Units of the dat file.
        
        Args:
            unit_data (list): the data pertaining to this unit.
        """ 
        end_line = int(unit_data[file_line].strip())
        file_line += 1
        try:
            # Load the geometry data
            for i in range(file_line, end_line + file_line):
                chain   = unit_data[i][0:10].strip()
                elev    = unit_data[i][10:20].strip()
                rough   = unit_data[i][20:30].strip()
                panel   = unit_data[i][30:35].strip()
                rpl     = unit_data[i][35:40].strip()
                bank    = unit_data[i][40:50].strip()
                east    = unit_data[i][50:60].strip()
                north   = unit_data[i][60:70].strip()
                deact   = unit_data[i][70:80].strip()
                special = unit_data[i][80:90].strip()
                
                if east == '': east = None
                if north == '': north = None
                
                self.row_data['main'].addRow(
                    {   rdt.CHAINAGE: chain, rdt.ELEVATION: elev, rdt.ROUGHNESS: rough,
                        rdt.RPL: rpl, rdt.PANEL_MARKER: panel, rdt.BANKMARKER: bank, 
                        rdt.EASTING: east, rdt.NORTHING: north, 
                        rdt.DEACTIVATION: deact, rdt.SPECIAL: special
                    },
                    # We don't need to make backup copies here. If it fails the
                    # load fails anyway and this will just really slow us down
                    no_copy=True
                ) 
                
        except NotImplementedError:
            logger.ERROR('Unable to read Unit Data(dataRowObject creation) - NotImplementedError')
            raise
            
        return end_line + file_line

    def getData(self): 
        """Retrieve the data in this unit.

        The String[] returned is formatted for printing in the fashion
        of the .dat file.
        
        Return:
            List of strings formated for writing to .dat file.
        """
        row_count = self.row_data['main'].numberOfRows()
        out_data = self._getHeadData(row_count)
        out_data.extend(self._getRowData(row_count)) 
        
        return out_data
  
  
    def _getRowData(self, row_count):
        """Returns the row data in this class.
        
        For all the rows in the river geometry section get the data from
        the rowdatacollection class.
        
        Returns:
            list = containing the formatted unit rows.
        """
        out_data = []
        for i in range(0, row_count):
            out_data.append(self.row_data['main'].getPrintableRow(i))
        return out_data
   
  
    def _getHeadData(self, row_count):
        """Get the header data formatted for printing out to file.
        
        Returns:
            List of strings - The formatted header list.
        """
        out = []
        key_order = ['distance', 'slope', 'density']
        for k in key_order:
            out.append(self.head_data[k].format())
        out = ''.join(out).split('\n')
        out.append('{:>10}'.format(row_count))
        out.insert(0, self._name)
        out.insert(0, 'SECTION')
        out.insert(0, 'RIVER ' + self.head_data['comment'].value)
        return out
   
    
    # updateDataRow
    def updateRow(self, row_vals, index, **kwargs):
        """Updates the row at the given index in the river units row_data.
        
        The row will be updated at the given index. 

        Args:
            row_vals(Dict): keys must be datunits.ROW_DATA_TYPES with a legal
                value assigned for the DataType. Chainage and Elevation MUST
                be included.
            index: the row to update. 

        Raises:
            AttributeError: If CHAINAGE or ELEVATION are not given.
            IndexError: If the index does not exist.
            ValueError: If the given value is not accepted by the DataObject's. 
            
        See Also:
            ADataObject and subclasses for information on the parameters.
        """
        
        # Call superclass method to add the new row
        AUnit.updateRow(self, row_vals=row_vals, index=index, **kwargs)
        
    
    # addDataRow
    def addRow(self, row_vals, index=None, **kwargs): 
        """Adds a new row to the river units row_data.
        
        The new row will be added at the given index. If no index is given it
        will be appended to the end of the collection.
        
        If no chainage or elevation values are given a AttributeError will be 
        raised as they cannot have default values. All other values can be
        ommitted. If they are they will be given defaults.
        
        Examples:
            >>> import ship.fmp.datunits.ROW_DATA_TYPES as rdt
            >>> river_unit.addDataRow({rdt.CHAINAGE:5.0, rdt.ELEVATION:36.2}, index=4)

        Args:
            row_vals(Dict): keys must be datunits.ROW_DATA_TYPES with a legal
                value assigned for the DataType. Chainage and Elevation MUST
                be included.
            index=None(int): the row to insert into. The existing row at the
                given index will be moved up by one.

        Raises:
            AttributeError: If CHAINAGE or ELEVATION are not given.
            IndexError: If the index does not exist.
            ValueError: If the given value is not accepted by the DataObject's. 
            
        See Also:
            ADataObject and subclasses for information on the parameters.
        """
        keys = row_vals.keys()
        if not rdt.CHAINAGE in keys or not rdt.ELEVATION in keys:
            raise AttributeError('row_vals must include CHAINAGE and ELEVATION.')
        
        # Call superclass method to add the new row
        AUnit.addRow(self, row_vals, index=index, **kwargs)
            

        
        