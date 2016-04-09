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
    UNIT_TYPE = 'GisInfo'
    CATEGORY = 'GisInfo'
    FILE_KEY = 'GISINFO'
    

    def __init__(self, file_order, node_count):
        """Constructor
        
        Args:
            node_count (int): The number of nodes in the model. We need this 
                to know how many lines there are to read from the contents list.
            fileOrder (inti) The location of this unit in the .DAT file. This 
                will always be at the end but for the GisInfoUnit, but we need 
                to pass it to the superclass.
        """
    
        AIsisUnit.__init__(self, file_order)
        self.unit_type = "GisInfo"
        self.unit_category = "GisInfo"
        self.name = "GisInfo"
        self.has_datarows = True
        self.node_count = node_count
    
    
    def readUnitData(self, unit_data, file_line):
        """
        """
        self.data = [''.join(unit_data[file_line:]).strip()]
        return len(unit_data)

        
        
        