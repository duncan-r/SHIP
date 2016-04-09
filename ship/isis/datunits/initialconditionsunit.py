"""

 Summary:
    Contains the InitialConditionsUnit class.
    This is a holder for all of the data in the initial conditions section
    of the dat file.

 Author:  
     Duncan Runnacles

 Created:  
     01 Apr 2016

 Copyright:  
     Duncan Runnacles 2016

 TODO:
    Not fully implemented at the moment - see class TODO comment for details.

 Updates:

"""


from ship.isis.datunits.isisunit import AIsisUnit

import logging
logger = logging.getLogger(__name__)

class InitialConditionsUnit (AIsisUnit):
    """isisunit for storing the initial conditions.

    Stores the initial conditions data near the end of the .dat file.
 
    TODO:
        Actually do something with this class. At the moment it might as well 
        be an UnknownSection
    """
    
    # Class constants
    UNIT_TYPE = 'InitialConditions'
    CATEGORY = 'InitialConditions'
    FILE_KEY = 'INITIAL'
    

    def __init__(self, file_order, node_count):
        """Constructor

        Args:
            node_count (int): The number of nodes in the model. We need this to 
                know how many lines there are to read from the contents list.
            fileOrder (int): The location of the initial conditions in the 
                .DAT file. This will always be at the end but before the 
                GISINFO if there is any.
        """
        AIsisUnit.__init__(self, file_order)
        self.unit_type = "InitialConditions"
        self.unit_category = "InitialConditions"
        self.name = "Initial Conditions"
        self.has_datarows = True
        self.node_count = node_count
    
    
    def readUnitData(self, data, file_line):
        """
        """
        out_line = file_line + self.node_count + 2
        self.data = [''.join(data[file_line:out_line]).strip()]
        return out_line - 1
       
    
    
    
