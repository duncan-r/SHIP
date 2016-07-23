"""

 Summary:
    Contains the InterpolateUnit class.
    These hold all of the data read in from the interpolate units in the dat 
    file. 

 Author:  
     Duncan Runnacles

  Created:  
     23 July 2016

 Copyright:  
     Duncan Runnacles 2016

 TODO:

 Updates:

"""

from ship.isis.datunits.isisunit import AIsisUnit

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class InterpolateUnit(AIsisUnit):
    '''Class for dealing with Interpolate units in the .dat file.'''

    # Class constants
    UNIT_TYPE = 'Interpolate'
    CATEGORY = 'Interpolate'
    FILE_KEY = 'INTERPOLATE'
    

    def __init__(self):
        '''Constructor.
        
        Args:
            file_order (int): the order of this unit in the .dat file.
        '''
        AIsisUnit.__init__(self)
        self.unit_type = InterpolateUnit.UNIT_TYPE
        self.unit_category = InterpolateUnit.CATEGORY
        self._name = 'Interpolate'
        self.has_datarows = False
        self.head_data = {'Comment': '', 
                          'section_label': 'Inter',
                          'spill1': '',
                          'spill2': '',
                          'lateral1': '',
                          'lateral2': '',
                          'lateral3': '',
                          'lateral4': '',
                          'distance': 0.0,
                          'easting': 0.0,
                          'northing': 0.0
                         }
            
    
    def readUnitData(self, unit_data, file_line): 
        '''Reads the given data into the object.
        
        See Also:
            isisunit.
        
        Args:
            unit_data (list): The raw file data to be processed.
        '''
        self.head_data = {'Comment': unit_data[file_line][12:].strip(), 
                          'section_label': unit_data[file_line+1][:12].strip(),
                          'spill1': unit_data[file_line+1][12:24].strip(),
                          'spill2': unit_data[file_line+1][24:36].strip(),
                          'lateral1': unit_data[file_line+1][36:48].strip(),
                          'lateral2': unit_data[file_line+1][48:60].strip(),
                          'lateral3': unit_data[file_line+1][60:72].strip(),
                          'lateral4': unit_data[file_line+1][72:84].strip(),
                          'distance': unit_data[file_line+2][:10].strip(),
                          'easting': unit_data[file_line+2][10:20].strip(),
                          'northing': unit_data[file_line+2][20:30].strip(),
                         }
        # Get rid of multiple whitespace and then split
        return file_line + 2
        
        
    def getData(self):
        '''Returns the formatted data for this unit. 
        
        See Also:
            isisunit.
        
        Returns:
            List of strings formatted for writing to the new dat file.
        '''
        out_data = []
        
        out_data.append('INTERPOLATE ' + self.head_data['Comment'])
        out_data.append('{:<12}'.format(self.head_data['section_label']) + 
                        '{:<12}'.format(self.head_data['spill1']) +
                        '{:<12}'.format(self.head_data['spill2']) +
                        '{:<12}'.format(self.head_data['lateral1']) +
                        '{:<12}'.format(self.head_data['lateral2']) +
                        '{:<12}'.format(self.head_data['lateral3']) +
                        '{:<12}'.format(self.head_data['lateral4']) 
                        )
        out_data.append('{:>10}'.format(self.head_data['distance']) + 
                        '{:>10}'.format(self.head_data['easting']) +
                        '{:>10}'.format(self.head_data['northing'])
                        )
        
        return out_data
        
        