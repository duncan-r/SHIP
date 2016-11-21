"""

 Summary:
    Contains the GisInfoUnit, as subclass of isisunit.
    It's used to hold the details in the gis section of the dat file which
    sets up the ixy or gxy files.

 Author:  
    Duncan Runnacles

 Created:  
     01 Apr 2016
     
 Copyright:  
     Duncan Runnacles 2016
     
 TODO:
    
    Not really implemented at the moment - see class TODO.

 Updates:

"""
from __future__ import unicode_literals


from ship.isis.datunits.isisunit import AIsisUnit

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class GisInfoUnit (AIsisUnit):
    """isisunit for storing the GIS info.

    Stores the GIS info found at the bottom of .dat file.
 
    Warning:
        Reads the file by simply parsing until it reaches EOF. This isn't 
        necessarily the case as there can be information about photos 
        attached to the model below it. Be careful of this.
    
    See Also:
        isisunit
    
    TODO:
        Actually do something with this class. At the moment it might as well 
        be an UnknownSection.
    """
    # Class constants
    UNIT_TYPE = 'gis_info'
    UNIT_CATEGORY = 'gis_info'
    FILE_KEY = 'GISINFO'
    FILE_KEY2 = None
    

    def __init__(self, **kwargs):
        """Constructor
        
        Args:
            node_count (int): The number of nodes in the model. We need this 
                to know how many lines there are to read from the contents list.
            fileOrder (inti) The location of this unit in the .DAT file. This 
                will always be at the end but for the GisInfoUnit, but we need 
                to pass it to the superclass.
        """
    
        AIsisUnit.__init__(self)
        self._unit_type = GisInfoUnit.UNIT_TYPE
        self._unit_category = GisInfoUnit.UNIT_CATEGORY
        self._name = "GisInfo"
#         self.has_datarows = True
#         self.has_ics = False
    
    
    def readUnitData(self, unit_data, file_line):
        """
        """
        self.head_data['all'] = [''.join(unit_data[file_line:]).strip()]
        return len(unit_data)


    def getData(self): 
        return self.head_data['all']
        
        