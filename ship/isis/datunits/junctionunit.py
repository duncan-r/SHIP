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


from ship.isis.datunits.isisunit import AIsisUnit

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class JunctionUnit(AIsisUnit):
    '''Class for dealing with Junction units in the .dat file.'''

    # Class constants
    UNIT_TYPE = 'Junction'
    CATEGORY = 'Junction'
    FILE_KEY = 'JUNCTION'
    

    def __init__(self):
        '''Constructor.
        
        Args:
            file_order (int): the order of this unit in the .dat file.
        '''
        AIsisUnit.__init__(self)
        self.unit_type = JunctionUnit.UNIT_TYPE
        self.unit_category = JunctionUnit.CATEGORY
        self._name = 'Junction'
        self.has_datarows = False
            
    
    def readUnitData(self, unit_data, file_line): 
        '''Reads the given data into the object.
        
        See Also:
            isisunit.
        
        Args:
            unit_data (list): The raw file data to be processed.
        '''
        self.head_data = {'Comment': unit_data[file_line][8:].strip(), 
                          'Type': unit_data[file_line + 1].strip(),
                          'Names': [] 
                         }
        # Get rid of multiple whitespace and then split
        names = ' '.join(unit_data[file_line + 2].split())
        names = names.split(' ')
        self.head_data['Names'] = names
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
        
        out_data.append('JUNCTION ' + self.head_data['Comment'])
        out_data.append(self.head_data['Type'])
        names = self.head_data['Names']
        
        # Format the names and then join into one line
        names_out = []
        for n in names:
            names_out.append('{:<12}'.format(n))
        out_data.append(''.join(names_out))
                        
        return out_data
        
        