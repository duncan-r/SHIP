"""

 Summary:
    Contains factory classes that are used in the library.
    At the moment the only factory in here is the IsisFactory. This is used
    to build the isisunit types.

 Author:  
     Duncan Runnacles

  Created:  
     01 Apr 2016

 Copyright:  
     Duncan Runnacles 2016

 TODO:
     There's a lot of functions in this module or more specifically the 
     IsisUnitFactory class that should be private, but currenlty aren't.
     
     They need to be set to private to avoid confusion.

 Updates:
     DR - 21/02/16: Major change to the setup of the factory. It no longer 
     scans the .dat file contents to identify the extent of the section and 
     passes only that to the unit. It now identifies the unit type to create 
     and hands the entire contents list to the new unit which extracts the 
     data required.

"""

from ship.isis.datunits import spillunit
from ship.isis.datunits import riverunit
from ship.isis.datunits import junctionunit
from ship.isis.datunits import initialconditionsunit
from ship.isis.datunits import gisinfounit
from ship.isis.datunits import bridgeunit
from ship.isis.datunits import isisunit 
from ship.isis.datunits import refhunit
from ship.isis.datunits import orificeunit
from ship.isis.datunits import culvertunit
from ship.isis.datunits import htbdyunit 
from ship.isis.datunits import interpolateunit 

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class IsisUnitFactory(object):
    """Builds isisunit type objects.
    
    This is a Factory pattern object for the creation of isisunit subclasses.
    """
    
    def __init__(self):
        """Constructor.

        Sets up the unit_identifiers. This is fetched by the DatLoader class to
        identify lines where the unit starts. It should be the first word on the 
        line where the unit data begins.

        Also contains all the unit specific read data for each unit in unit_vars.
        this dict should be updated each time a new unit is added so that the
        factory knows how to process it.
        
        Args:
            node_count (int): The number of unit nodes in the model. 
        """
        self.node_count = 0
        self.reach_number = 0
        self.same_reach = False
        self.available_units = {'river': riverunit.RiverUnit, 
                                'initialconditions': initialconditionsunit.InitialConditionsUnit, 
                                'gisinfo': gisinfounit.GisInfoUnit,
                                'header': isisunit.HeaderUnit, 
                                'comment': isisunit.CommentUnit,
                                'bridge': bridgeunit.BridgeUnitUsbpr,
                                'bridge': bridgeunit.BridgeUnitArch,
                                'spill': spillunit.SpillUnit,
                                'junction': junctionunit.JunctionUnit,
                                'refh': refhunit.RefhUnit,
                                'orifice': orificeunit.OrificeUnit,
                                'outlet': orificeunit.OutfallUnit,
                                'frelief': orificeunit.FloodReliefArchUnit,
                                'culvert': culvertunit.CulvertInletUnit,
                                'culvert': culvertunit.CulvertOutletUnit,
                                'htbdy': htbdyunit.HtbdyUnit,
                                'interolate': interpolateunit.InterpolateUnit,
                               }
        try:
            self._getFileKeys()
        except:
            logger.error('UNIT_VARS incorrectly set in some classes')
            raise Exception ('UNIT_VARS incorrectly set in some classes')
        
    
    def _getFileKeys(self):
        """Get the file keys for the available units.
        
        Every AIsisUnit type class must declare a static variable that 
        defines the key word used in the .dat file. This is then used to
        recognise when a unit of that type has been found.
        """
        self.unit_identifiers = {}
        for key, item in self.available_units.items():
            self.unit_identifiers[item.FILE_KEY] = key
            
    
    def createUnit(self, contents, file_line, key, file_order, reach_number = None):
        """
        """
        # Update reach number info
        if not key == 'river' or key == 'comment':
            self.same_reach = False
            
        '''Need to deal with RiverUnit slightly differently because it records
        information about the reach number.
        Same is true for the InitialConditionsUnit as it can only know how 
        long it is by taking the number of units from the HeaderUnit.

        TODO: This needs looking into, perhaps either apply a reach number to
              all units or create a seperate lookup in the collection.
        '''
        if key == 'river':
            # River can also be used for Muskingham units
            if not contents[file_line+1].strip().startswith('SECTION'):
                return file_line, False
            
            reach_no = self._getReachNumber(reach_number)
            unit = riverunit.RiverUnit(reach_no)
        
        elif key == 'initialconditions' or key == 'gisinfo':
            unit = self.available_units[key](self.ic_rows)
        
        elif key == 'bridge':
            if contents[file_line + 1].strip().startswith('USBPR1978'):
                unit = bridgeunit.BridgeUnitUsbpr()
            else:
                unit = bridgeunit.BridgeUnitArch()
        
        elif key == 'culvert':
            if contents[file_line + 1].strip().startswith('INLET'):
                unit = culvertunit.CulvertInletUnit()
            else:
                unit = culvertunit.CulvertOutletUnit()
        
        # All other units only need a file_order for their constructor.
        else:
            '''If no matching unit can be found False is return as the second
            part of the tuple and the datloader will know to start creating an
            UnknownUnit.
            '''
            if key in self.available_units.keys():
                unit = self.available_units[key]()
            else:
                return file_line, False
        
        # Send contents to unit for construction.
        file_line = unit.readUnitData(contents, file_line)
        
        '''Need to grab the number of units in the initial conditions from the
        header unit because there's no way to know how long it is otherwise.
        '''
        if key == 'header':
            self.ic_rows = unit.node_count
        
        return file_line, unit
    
     
    def _getReachNumber(self, reach_number):
        """Find whether we need to increase the reach number or not.

        Checks if the previous section created was a river or not. If it
        wasn't the reach number is increased by 1. Otherwise if a reach
        number is supplied use that instead.
        
        Args:
            reach_number (int): The reach number that this unit should be 
                created with.         
        
        Returns:
            int - reach number.
        """
        # If we've been given a reach number use that.
        if not reach_number == None:
            return reach_number

        if self.same_reach == False:
            self.same_reach = True
            self.reach_number += 1
            return self.reach_number
        else:
            return self.reach_number

        
    def getUnitIdentifiers(self):
        """Returns all the unit identifiers that the object holds.
        
        Getter for obtaining the identifier strings needed to find the units 
        that have been defined, when loading the dat file.
        
        Args:
            Dict - unit_identifers dictionary.
        """
        return self.unit_identifiers
    

