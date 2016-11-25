"""

 Summary:
    Contains the JuntionUnit type classes.
    This holds all of the data read in from the junction units in the dat file.
    Can be called to load in the data and read and update the contents 
    held in the object.

 Author:  
     Duncan Runnacles

 Copyright:  
     Duncan Runnacles 2016

 TODO:

 Updates:

"""
from __future__ import unicode_literals

from ship.fmp.datunits.isisunit import AUnit
from ship.fmp.headdata import HeadDataItem
from ship.data_structures import DATA_TYPES as dt

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class JunctionUnit(AUnit):
    '''Class for dealing with Junction units in the .dat file.'''

    # Class constants
    UNIT_TYPE = 'Junction'
    UNIT_CATEGORY = 'Junction'
    FILE_KEY = 'JUNCTION'
    FILE_KEY2 = None
    

    def __init__(self):
        '''Constructor.
        
        Args:
            file_order (int): the order of this unit in the .dat file.
        '''
        AUnit.__init__(self)
        self._unit_type = JunctionUnit.UNIT_TYPE
        self._unit_category = JunctionUnit.UNIT_CATEGORY
        self._name = 'Junc'
        self.head_data = {
            'comment': HeadDataItem('', '', 0, 0, dtype=dt.STRING),
            'type': HeadDataItem('OPEN', '', 0, 0, dtype=dt.CONSTANT, choices=('OPEN', 'ENERGY')),
            'names': [],
        }


    def icLabels(self):
        """Overriddes superclass method."""
        return [self._name]
            
    
    def readUnitData(self, unit_data, file_line): 
        '''Reads the given data into the object.
        
        See Also:
            isisunit.
        
        Args:
            unit_data (list): The raw file data to be processed.
        '''
        self.head_data['comment'].value = unit_data[file_line][8:].strip() 
        self.head_data['type'].value = unit_data[file_line + 1].strip()

        # Get rid of multiple whitespace and then split
        names = ' '.join(unit_data[file_line + 2].split())
        names = names.split(' ')
        self.head_data['names'] = names
        self._name = names[0]
        return file_line + 2
        
        
    def getData(self):
        '''Returns the formatted data for this unit. 
        
        See Also:
            isisunit.
        
        Returns:
            List of strings formatted for writing to the new dat file.
        '''
        out_data = []
        
        out_data.append('JUNCTION ' + self.head_data['comment'].value)
        out_data.append(self.head_data['type'].value)
        names = self.head_data['names']
        
        # Format the names and then join into one line
        names_out = []
        for n in names:
            names_out.append('{:<12}'.format(n))
        out_data.append(''.join(names_out))
                        
        return out_data
        
        