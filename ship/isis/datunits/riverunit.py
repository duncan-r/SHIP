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

from ship.isis.datunits.isisunit import AIsisUnit
from ship.data_structures import dataobject as do
from ship.data_structures.rowdatacollection import RowDataCollection 
from ship.isis.datunits import ROW_DATA_TYPES as rdt

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class RiverUnit (AIsisUnit): 
    """Concrete implementation of AIsisUnit storing Isis River Unit
    data.

    Contains a reference to a rowdatacollection for storing and
    accessing all the row data. i.e. the geometry data for the section,
    containing the chainage, elevation, roughness, etc values.

    Methods for accessing the data in these objects and adding removing rows
    are available.
    
    See Also:
        AIsisUnit
    """
    
    UNIT_TYPE = 'River'
    CATEGORY = 'River'
    FILE_KEY = 'RIVER'


    def __init__(self, reach_number): 
        """Constructor.
        
        Args:
            fileOrder (int): The location of this unit in the file.
            reach_number (int): The reach ID for this unit.
        """
        AIsisUnit.__init__(self)

        # Fill in the header values these contain the data at the top of the
        # section, such as the unit name and labels.
        self.head_data = {'section_label': 'RivUS', 'spill1': '', 'spill2': '', 'lateral1': '',
                       'lateral2': '', 'lateral3': '', 'lateral4': '', 'distance': 0,
                       'slope': 0.0000, 'density': 1000, 'comment': '', 'rowcount': 0} 

        self.unit_type = RiverUnit.UNIT_TYPE
        self.unit_category = RiverUnit.CATEGORY
        self.has_datarows = True
        self.has_ics = True
        self.reach_number = reach_number
        self.unit_length = 0
        
        # Add the new row data types to the object collection
        # All of them must have type, output format, default value and position
        # in the row as the first variables in vars.
        # The others are DataType specific.
        self.row_collection = RowDataCollection()
        self.row_collection.initCollection(do.FloatData(0, rdt.CHAINAGE, format_str='{:>10}', no_of_dps=3))
        self.row_collection.initCollection(do.FloatData(1, rdt.ELEVATION, format_str='{:>10}', no_of_dps=3))
        self.row_collection.initCollection(do.FloatData(2, rdt.ROUGHNESS, format_str='{:>10}', default=0.0, no_of_dps=3))
        self.row_collection.initCollection(do.SymbolData(3, rdt.PANEL_MARKER, '*', format_str='{:<5}', default=False))
        self.row_collection.initCollection(do.FloatData(4, rdt.RPL, format_str='{:>5}', default=1.000, no_of_dps=3))
        self.row_collection.initCollection(do.ConstantData(5, rdt.BANKMARKER, ('LEFT', 'RIGHT', 'BED'), format_str='{:<10}', default=''))
        self.row_collection.initCollection(do.FloatData(6, rdt.EASTING, format_str='{:>10}', default=0.0, no_of_dps=2))
        self.row_collection.initCollection(do.FloatData(7, rdt.NORTHING, format_str='{:>10}', default=0.0, no_of_dps=2))
        self.row_collection.initCollection(do.ConstantData(8, rdt.DEACTIVATION, ('LEFT', 'RIGHT'), format_str='{:<10}', default=''))
        # Default == '~' means to ignore formatting and apply '' when value is None
        self.row_collection.initCollection(do.StringData(9, rdt.SPECIAL, format_str='{:<10}', default='~'))
    
        
    def readUnitData(self, unit_data, file_line):
        """Reads the unit data into the geometry objects.
        
        See Also:
            AIsisUnit - readUnitData for more information.
        
        Args:
            unit_data (list): The section of the isis dat file pertaining 
                to this section 
        """
        file_line = self._readHeadData(unit_data, file_line)
        file_line = self._readRowData(unit_data, file_line)
        self.head_data['rowcount'] = self.row_collection.getNumberOfRows()
        return file_line - 1
        

    def _readHeadData(self, unit_data, file_line):            
        """Format the header data for writing to file.
        
        Args:
            unit_data (list): containing the data to read.
        """
        self.head_data['comment'] = unit_data[file_line + 0][5:].strip()
        self._name = self.head_data['section_label'] = unit_data[file_line + 2][:12].strip()
        self.head_data['spill1'] = unit_data[file_line + 2][12:24].strip()
        self.head_data['spill2'] = unit_data[file_line + 2][24:36].strip()
        self.head_data['lateral1'] = unit_data[file_line + 2][36:48].strip()
        self.head_data['lateral2'] = unit_data[file_line + 2][48:60].strip()
        self.head_data['lateral3'] = unit_data[file_line + 2][60:72].strip()
        self.head_data['lateral4'] = unit_data[file_line + 2][72:84].strip()
        self.head_data['distance'] = unit_data[file_line + 3][0:10].strip()
        self.head_data['slope'] = unit_data[file_line + 3][10:30].strip()
        self.head_data['density'] = unit_data[file_line + 3][30:40].strip()
        self.unit_length = int(unit_data[file_line + 4].strip())
        return file_line + 5

    def _readRowData(self, unit_data, file_line):
        """Reads the units rows into the row collection.

        This is all the geometry data that occurs after the no of rows variable in
        the River Units of the dat file.
        
        Args:
            unit_data (list): the data pertaining to this unit.
        """ 
        out_line = file_line + self.unit_length
        try:
            # Load the geometry data
            for i in range(file_line, out_line):
                
                # Put the values into the respective data objects            
                # This is done based on the column widths set in the Dat file
                # for the river section.
                self.row_collection.addValue(rdt.CHAINAGE, unit_data[i][0:10].strip())
                self.row_collection.addValue(rdt.ELEVATION, unit_data[i][10:20].strip())
                self.row_collection.addValue(rdt.ROUGHNESS, unit_data[i][20:30].strip())
                self.row_collection.addValue(rdt.PANEL_MARKER, unit_data[i][30:35].strip())
                self.row_collection.addValue(rdt.RPL, unit_data[i][35:40].strip())
                self.row_collection.addValue(rdt.BANKMARKER, unit_data[i][40:50].strip())
                
                # It seems that ISIS will allow models to load that have no
                # value in the easting and northing parts. This checks if they
                # do and if not replaces with None so a default will be used.
                east = unit_data[i][50:60].strip()
                north = unit_data[i][60:70].strip()
                if east == '': east = None
                if north == '': north = None
                self.row_collection.addValue(rdt.EASTING, east)
                self.row_collection.addValue(rdt.NORTHING, north)
                    
                self.row_collection.addValue(rdt.DEACTIVATION, unit_data[i][70:80].strip())
                self.row_collection.addValue(rdt.SPECIAL, unit_data[i][80:90].strip())

        except NotImplementedError:
            logger.ERROR('Unable to read Unit Data(dataRowObject creation) - NotImplementedError')
            raise
            
        return out_line

    def getData(self): 
        """Retrieve the data in this unit.

        The String[] returned is formatted for printing in the fashion
        of the .dat file.
        
        Return:
            List of strings formated for writing to .dat file.
        """
        self.head_data['rowcount'] = self.row_collection.getNumberOfRows()
        out_data = self._getHeadData()
        out_data.extend(self._getRowData()) 
        
        return out_data
  
  
    def _getRowData(self):
        """Returns the row data in this class.
        
        For all the rows in the river geometry section get the data from
        the rowdatacollection class.
        
        Returns:
            list = containing the formatted unit rows.
        """
        out_data = []
        for i in range(0, self.row_collection.getNumberOfRows()): 
            out_data.append(self.row_collection.getPrintableRow(i))
        
        return out_data
   
  
    def _getHeadData(self):
        """Get the header data formatted for printing out to file.
        
        Returns:
            List of strings - The formatted header list.
        """
        out_data = []
#         self.head_data['rowcount'] = self.unit_length
        out_data.append('RIVER ' + self.head_data['comment'])
        out_data.append('SECTION')
        
        # Get the row with the section name and spill info from the formatter
        out_data.append(self._getHeadSectionRowFormat())
        
        out_data.append('{:>10}'.format(self.head_data['distance']) + '{:>20}'.format(self.head_data['slope']) +
                        '{:>10}'.format(self.head_data['density']))
#         self.head_data['rowcount'] = self.row_collection.getNumberOfRows()
        out_data.append('{:>10}'.format(self.head_data['rowcount']))
        
        return out_data
   
   
    def _getHeadSectionRowFormat(self):
        """Formats the section name and spill file row according to contents.

        This is quite a pedantic method. Essentially if there are spills in the
        line of the file they each get 12 spaces. However if it's just the         
        one spill there the whitespace is cut off the end. Isis is pretty 
        weird about white space so it's best to get it right.
        
        Returns:
            string containing row data with whitespace trimmed from the right 
                side.
        """
        section_row = '{:<12}'.format(self.head_data['section_label'])
        if not self.head_data['spill1'] == '':
            section_row += '{:<12}'.format(self.head_data['spill1'])
        if not self.head_data['spill2'] == '':
            section_row += '{:<12}'.format(self.head_data['spill2'])
        
        section_row = section_row.rstrip()
        return section_row
        
    
    def updateDataRow(self, row_vals, index):
        """Updates the row at the given index in the river units row_collection.
        
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
        AIsisUnit.updateDataRow(self, row_vals=row_vals, index=index)
        
    
    def addDataRow(self, row_vals, index=None): 
        """Adds a new row to the river units row_collection.
        
        The new row will be added at the given index. If no index is given it
        will be appended to the end of the collection.
        
        If no chainage or elevation values are given a AttributeError will be 
        raised as they cannot have default values. All other values can be
        ommitted. If they are they will be given defaults.
        
        Examples:
            >>> import ship.isis.datunits.ROW_DATA_TYPES as rdt
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
        if not rdt.CHAINAGE in row_vals.keys() or not rdt.ELEVATION in row_vals.keys():
            logger.error('Required values of CHAINAGE and ELEVATION not given')
            raise  AttributeError ('Required values of CHAINAGE and ELEVATION not given')
        
        # Setup default values for arguments that aren't given
        kw={}
        kw[rdt.CHAINAGE] = row_vals.get(rdt.CHAINAGE)
        kw[rdt.ELEVATION] = row_vals.get(rdt.ELEVATION)
        kw[rdt.ROUGHNESS] = row_vals.get(rdt.ROUGHNESS, 0.039)
        kw[rdt.PANEL_MARKER] = row_vals.get(rdt.PANEL_MARKER, False)
        kw[rdt.RPL] = row_vals.get(rdt.RPL, 1.0)
        kw[rdt.BANKMARKER] = row_vals.get(rdt.BANKMARKER, '')
        kw[rdt.EASTING] = row_vals.get(rdt.EASTING, 0.0)
        kw[rdt.NORTHING] = row_vals.get(rdt.NORTHING, 0.0)
        kw[rdt.DEACTIVATION] = row_vals.get(rdt.DEACTIVATION, '')
        kw[rdt.SPECIAL] = row_vals.get(rdt.SPECIAL, '')

        # Call superclass method to add the new row
        AIsisUnit.addDataRow(self, index=index, row_vals=kw)
            
    
    
        
        