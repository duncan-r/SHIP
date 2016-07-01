"""

 Summary:
    Contains the Culvert unit type classes.
    This holds all of the data read in from the culvert units in the dat file.
    Can be called to load in the data and read and update the contents 
    held in the object.

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


class Culvert(AIsisUnit):
    '''Class for dealing with Inlet Culvert units in the .dat file.'''

    # Class constants
    UNIT_TYPE = 'Culvert'
    CATEGORY = 'Culvert'
    UNIT_VARS = None
    

    def __init__(self):
        '''Constructor.'''
        AIsisUnit.__init__(self)
        self.unit_type = Culvert.UNIT_TYPE
        self.unit_category = Culvert.CATEGORY
        self.name = 'Outfall'
        self.has_datarows = False

class CulvertUnit(AIsisUnit):
    '''Class for dealing with Inlet Culvert units in the .dat file.'''

    # Class constants
    UNIT_TYPE = 'Culvert'
    CATEGORY = 'Culvert'
    FILE_KEY = 'CULVERT'
    

    def __init__(self):
        '''Constructor.
        '''
        AIsisUnit.__init__(self)
        self.unit_type = CulvertUnit.UNIT_TYPE
        self.unit_category = CulvertUnit.CATEGORY
        self.has_datarows = False


class CulvertInletUnit(CulvertUnit):
    
    # Class constants
    UNIT_TYPE = 'Culvert Inlet'
    CATEGORY = 'Culvert'
    FILE_KEY = 'CULVERT'
    
    def __init__(self):
        '''Constructor.
        '''
        CulvertUnit.__init__(self)
        self.unit_type = CulvertInletUnit.UNIT_TYPE
            
    
    def readUnitData(self, unit_data, file_line): 
        '''Reads the given data into the object.
        
        See Also:
            isisunit.
        
        Args:
            unit_data (list): The raw file data to be processed.
        '''
        self.head_data = {'comment': unit_data[file_line][8:].strip(), 
                          'us_label': unit_data[file_line + 2][:12].strip(),
                          'ds_label': unit_data[file_line + 2][12:].strip(),
                          'K': unit_data[file_line + 3][:10].strip(),
                          'M': unit_data[file_line + 3][10:20].strip(),
                          'C': unit_data[file_line + 3][20:30].strip(),
                          'Y': unit_data[file_line + 3][30:40].strip(),
                          'Ki': unit_data[file_line + 3][40:50].strip(),
                          'conduit_type': unit_data[file_line + 3][50:60].strip(),
                          'screen_width': unit_data[file_line + 4][:10].strip(),
                          'bar_proportion': unit_data[file_line + 4][10:20].strip(),
                          'debris_proportion': unit_data[file_line + 4][20:30].strip(),
                          'loss_coefficient': unit_data[file_line + 4][30:40].strip(),
                          'reverse_flow_model': unit_data[file_line + 4][40:50].strip(),
                          'headloss_type': unit_data[file_line + 4][50:60].strip(),
                          'trash_screen_height': unit_data[file_line + 4][60:].strip()
                         }
        
        return file_line + 4
        
        
    def getData(self):
        '''Returns the formatted data for this unit. 
        
        See Also:
            isisunit.
        
        Returns:
            List of strings formatted for writing to the new dat file.
        '''
        out_data = []
        
        out_data.append('CULVERT ' + self.head_data['comment'])
        out_data.append('INLET')
        out_data.append('{:<12}'.format(self.head_data['us_label']) +
                        '{:<12}'.format(self.head_data['ds_label']))
        out_data.append('{:>10}'.format(self.head_data['K']) +
                        '{:>10}'.format(self.head_data['M']) +
                        '{:>10}'.format(self.head_data['C']) +
                        '{:>10}'.format(self.head_data['Y']) +
                        '{:>10}'.format(self.head_data['Ki']) +
                        '{:>10}'.format(self.head_data['conduit_type']))
        out_data.append('{:>10}'.format(self.head_data['screen_width']) +
                        '{:>10}'.format(self.head_data['bar_proportion']) +
                        '{:>10}'.format(self.head_data['debris_proportion']) +
                        '{:>10}'.format(self.head_data['loss_coefficient']) +
                        '{:<10}'.format(self.head_data['reverse_flow_model']) +
                        '{:>10}'.format(self.head_data['headloss_type']) +
                        '{:>10}'.format(self.head_data['trash_screen_height']))
        
        return out_data


class CulvertOutletUnit(CulvertUnit):
    
    # Class constants
    UNIT_TYPE = 'Culvert Outlet'
    CATEGORY = 'Culvert'
    FILE_KEY = 'CULVERT'
    
    def __init__(self):
        '''Constructor.
        '''
        CulvertUnit.__init__(self)
        self.unit_type = CulvertOutletUnit.UNIT_TYPE
            
    
    def readUnitData(self, unit_data, file_line): 
        '''Reads the given data into the object.
        
        See Also:
            isisunit.
        
        Args:
            unit_data (list): The raw file data to be processed.
        '''
        self.head_data = {'comment': unit_data[file_line][8:].strip(), 
                          'us_label': unit_data[file_line + 2][:12].strip(),
                          'ds_label': unit_data[file_line + 2][12:].strip(),
                          'loss_coefficient': unit_data[file_line + 3][:10].strip(),
                          'reverse_flow_model': unit_data[file_line + 3][10:20].strip(),
                          'headloss_type': unit_data[file_line + 3][20:].strip()
                         }
        
        return file_line + 3
        
        
    def getData(self):
        '''Returns the formatted data for this unit. 
        
        See Also:
            isisunit.
        
        Returns:
            List of strings formatted for writing to the new dat file.
        '''
        out_data = []
        
        out_data.append('CULVERT ' + self.head_data['comment'])
        out_data.append('OUTLET')
        out_data.append('{:<12}'.format(self.head_data['us_label']) +
                        '{:<12}'.format(self.head_data['ds_label']))
        out_data.append('{:>10}'.format(self.head_data['loss_coefficient']) +
                        '{:<10}'.format(self.head_data['reverse_flow_model']) +
                        '{:>10}'.format(self.head_data['headloss_type']))
        
        return out_data
    
    
        
        