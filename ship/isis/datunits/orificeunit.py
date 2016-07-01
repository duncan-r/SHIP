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


from ship.isis.datunits.isisunit import AIsisUnit

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class OrificeUnit(AIsisUnit):
    '''Class for dealing with Orifice units in the .dat file.'''

    # Class constants
    UNIT_TYPE = 'Orifice'
    CATEGORY = 'Orifice'
    FILE_KEY = 'ORIFICE'
    

    def __init__(self):
        '''Constructor.
        '''
        AIsisUnit.__init__(self)
        self.unit_type = OrificeUnit.UNIT_TYPE
        self.unit_category = OrificeUnit.CATEGORY
        self._name = 'Orifice'
        self.has_datarows = False
        
        self.head_data = {'comment': '',
                          'type': 'OPEN',
                          'section_label': 'OrificUS',
                          'ds_label': 'OrificeDS',
                          'invert_level': 0.000,
                          'soffit_level': 0.000,
                          'bore_area': 0.000,
                          'us_sill_level': 0.000,
                          'ds_sill_level': 0.000,
                          'weir_flow': 0.000,
                          'surcharged_flow': 0.000,
                          'modular_limit': 0.000,
                         }
            
    
    def readUnitData(self, unit_data, file_line): 
        '''Reads the given data into the object.
        
        See Also:
            isisunit.
        
        Args:
            unit_data (list): The raw file data to be processed.
        '''
        self.head_data = {'comment': unit_data[file_line][8:].strip(), 
                          'type': unit_data[file_line + 1].strip(),
                          'section_label': unit_data[file_line + 2][:12].strip(),
                          'ds_label': unit_data[file_line + 2][12:].strip(),
                          'invert_level': unit_data[file_line + 3][:10].strip(),
                          'soffit_level': unit_data[file_line + 3][10:20].strip(),
                          'bore_area': unit_data[file_line + 3][20:30].strip(),
                          'us_sill_level': unit_data[file_line + 3][30:40].strip(),
                          'ds_sill_level': unit_data[file_line + 3][40:50].strip(),
                          'weir_flow': unit_data[file_line + 4][:10].strip(),
                          'surcharged_flow': unit_data[file_line + 4][10:20].strip(),
                          'modular_limit': unit_data[file_line + 4][20:30].strip()
                         }
        self._name = self.head_data['section_label']
        return file_line + 4
        
        
    def getData(self):
        '''Returns the formatted data for this unit. 
        
        See Also:
            isisunit.
        
        Returns:
            List of strings formatted for writing to the new dat file.
        '''
        out_data = []
        
        self.head_data['section_label'] = self._name
        out_data.append(self.unit_type.upper() + ' ' + self.head_data['comment'])
        out_data.append(self.head_data['type'])
        out_data.append('{:<12}'.format(self.head_data['section_label']) +
                        '{:<12}'.format(self.head_data['ds_label']))
        out_data.append('{:>10}'.format(self.head_data['invert_level']) +
                        '{:>10}'.format(self.head_data['soffit_level']) +
                        '{:>10}'.format(self.head_data['bore_area']) +
                        '{:>10}'.format(self.head_data['us_sill_level']) +
                        '{:>10}'.format(self.head_data['ds_sill_level']))
        out_data.append('{:>10}'.format(self.head_data['weir_flow']) +
                        '{:>10}'.format(self.head_data['surcharged_flow']) +
                        '{:>10}'.format(self.head_data['modular_limit']))
        
        return out_data
    
    
class OutfallUnit(OrificeUnit):
    '''Class for dealing with Outfall units in the .dat file.
    
    Subclasses the orifice unit because they are essentially the same as far
    as the .dat file setup goes.
    '''

    # Class constants
    UNIT_TYPE = 'Outfall'
    CATEGORY = 'Outfall'
    FILE_KEY = 'OUTFALL'
    

    def __init__(self):
        '''Constructor.
        '''
        OrificeUnit.__init__(self)
        self.unit_type = OutfallUnit.UNIT_TYPE
        self.unit_category = OutfallUnit.CATEGORY
        self._name = 'Outfall'
        self.has_datarows = False
        self.head_data['section_label'] = 'OutfallUS' 
        self.head_data['ds_label'] = 'OutfallDS' 



class FloodReliefArchUnit(OrificeUnit):
    '''Class for dealing with flood relief arch units in the .dat file.
    
    Subclasses the orifice unit because they are essentially the same as far
    as the .dat file setup goes.
    '''

    # Class constants
    UNIT_TYPE = 'Relief Arch'
    CATEGORY = 'Relief Arch'
    FILE_KEY = 'FLOOD RELIEF'
    

    def __init__(self):
        '''Constructor.
        '''
        OrificeUnit.__init__(self)
        self.unit_type = OutfallUnit.UNIT_TYPE
        self.unit_category = OutfallUnit.CATEGORY
        self._name = 'FRelief'
        self.has_datarows = False
        self.head_data['section_label'] = 'ReliefUS' 
        self.head_data['ds_label'] = 'ReliefDS' 
    
        
        