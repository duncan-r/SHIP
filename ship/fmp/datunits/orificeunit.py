"""

 Summary:
    Contains the OrificeUnit type classes.
    This holds all of the data read in from the orifice units in the dat file.
    Can be called to load in the data and read and update the contents 
    held in the object.
    
    The OutfallUnit is also in here. It has the same setup as the OrificeUnit
    so it subclasses orifice.

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
from ship.utils import utilfunctions as uf

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class OrificeUnit(AUnit):
    '''Class for dealing with Orifice units in the .dat file.'''

    # Class constants
    UNIT_TYPE = 'orifice'
    UNIT_CATEGORY = 'orifice'
    FILE_KEY = 'ORIFICE'
    FILE_KEY2 = None
    

    def __init__(self, **kwargs):
        '''Constructor.
        '''
        AUnit.__init__(self, **kwargs)
        self._unit_type = OrificeUnit.UNIT_TYPE
        self._unit_category = OrificeUnit.UNIT_CATEGORY
        self._name = 'orif'
        
        self.head_data = {
            'comment': HeadDataItem('', '', 0, 0, dtype=dt.STRING),
            'type': HeadDataItem('OPEN', '{:>10}', 1, 0, dtype=dt.CONSTANT, choices=('OPEN', 'FLAPPED')),
            'invert_level': HeadDataItem(0.000, '{:>10}', 2, 0, dtype=dt.FLOAT, dps=3),
            'soffit_level': HeadDataItem(0.000, '{:>10}', 2, 1, dtype=dt.FLOAT, dps=3),
            'bore_area': HeadDataItem(0.000, '{:>10}', 2, 2, dtype=dt.FLOAT, dps=3),
            'us_sill_level': HeadDataItem(0.000, '{:>10}', 2, 3, dtype=dt.FLOAT, dps=3),
            'ds_sill_level': HeadDataItem(0.000, '{:>10}', 2, 4, dtype=dt.FLOAT, dps=3),
            'shape': HeadDataItem('RECTANGLE', '{:>10}', 2, 5, dtype=dt.CONSTANT, choices=('RECTANGLE', 'CIRCULAR')),
            'weir_flow': HeadDataItem(0.000, '{:>10}', 3, 0, dtype=dt.FLOAT, dps=3),
            'surcharged_flow': HeadDataItem(0.000, '{:>10}', 3, 1, dtype=dt.FLOAT, dps=3),
            'modular_limit': HeadDataItem(0.000, '{:>10}', 3, 2, dtype=dt.FLOAT, dps=3),
        }

    
    def icLabels(self):
        """Overriddes superclass method."""
        return [self._name, self._name_ds]

        
    def readUnitData(self, unit_data, file_line): 
        '''Reads the given data into the object.
        
        See Also:
            isisunit.
        
        Args:
            unit_data (list): The raw file data to be processed.
        '''
        self.head_data['comment'].value = unit_data[file_line][8:].strip() 
        self.head_data['type'].value = unit_data[file_line + 1].strip()
        self._name = unit_data[file_line + 2][:12].strip()
        self._name_ds = unit_data[file_line + 2][12:].strip()
        self.head_data['invert_level'].value = unit_data[file_line + 3][:10].strip()
        self.head_data['soffit_level'].value = unit_data[file_line + 3][10:20].strip()
        self.head_data['bore_area'].value = unit_data[file_line + 3][20:30].strip()
        self.head_data['us_sill_level'].value = unit_data[file_line + 3][30:40].strip()
        self.head_data['ds_sill_level'].value = unit_data[file_line + 3][40:50].strip()
        self.head_data['shape'].value = unit_data[file_line + 3][50:60].strip()
        self.head_data['weir_flow'].value = unit_data[file_line + 4][:10].strip()
        self.head_data['surcharged_flow'].value = unit_data[file_line + 4][10:20].strip()
        self.head_data['modular_limit'].value = unit_data[file_line + 4][20:30].strip()
        return file_line + 4
        
        
    def getData(self):
        '''Returns the formatted data for this unit. 
        
        See Also:
            isisunit.
        
        Returns:
            List of strings formatted for writing to the new dat file.
        '''
        out = []
        out.append('ORIFICE ' + self.head_data['comment'].value)
        out.append('\n'+self.head_data['type'].value)
        out.append('\n{:<12}'.format(self._name) + '{:<12}'.format(self._name_ds))
        key_order = ['invert_level', 'soffit_level', 'bore_area', 'us_sill_level',
                     'ds_sill_level', 'shape', 'weir_flow', 'surcharged_flow',
                     'modular_limit']
        for k in key_order:
            out.append(self.head_data[k].format(True))
        out_data = ''.join(out).split('\n')
        return out_data
    
    
class OutfallUnit(OrificeUnit):
    '''Class for dealing with Outfall units in the .dat file.
    
    Subclasses the orifice unit because they are essentially the same as far
    as the .dat file setup goes.
    '''

    # Class constants
    UNIT_TYPE = 'outfall'
    UNIT_CATEGORY = 'outfall'
    FILE_KEY = 'OUTFALL'
    FILE_KEY2 = None
    

    def __init__(self, **kwargs):
        '''Constructor.
        '''
        OrificeUnit.__init__(self, **kwargs)
        self._unit_type = OutfallUnit.UNIT_TYPE
        self._unit_category = OutfallUnit.UNIT_CATEGORY
        self._name = 'outf'
        self._name_ds = 'outfds'



class FloodReliefUnit(OrificeUnit):
    '''Class for dealing with flood relief arch units in the .dat file.
    
    Subclasses the orifice unit because they are essentially the same as far
    as the .dat file setup goes.
    '''

    # Class constants
    UNIT_TYPE = 'relief_arch'
    CATEGORY = 'relief_arch'
    FILE_KEY = 'FLOOD RELIEF'
    FILE_KEY2 = None
    

    def __init__(self, **kwargs):
        '''Constructor.
        '''
        OrificeUnit.__init__(self, **kwargs)
        self._unit_type = FloodReliefUnit.UNIT_TYPE
        self._unit_category = FloodReliefUnit.UNIT_CATEGORY
        self._name = 'FRelUs'
        self._name_ds = 'FRelDs'
    
        
        