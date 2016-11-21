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

from __future__ import unicode_literals

from ship.isis.datunits import spillunit
from ship.isis.datunits import riverunit
from ship.isis.datunits import junctionunit
from ship.isis.datunits import initialconditionsunit as icu
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

        Sets up the unit_ids. This is fetched by the DatLoader class to
        identify lines where the unit starts. It should be the first word on the 
        line where the unit data begins.
        """
        self.node_count = 0
        self.reach_number = 0
        self.same_reach = False
        self._ic_name_types = {}
        
        self.available_units = (
            isisunit.HeaderUnit,
            riverunit.RiverUnit, 
            refhunit.RefhUnit,
            icu.InitialConditionsUnit,
            gisinfounit.GisInfoUnit,
            bridgeunit.BridgeUnitArch,
            bridgeunit.BridgeUnitUsbpr,
            spillunit.SpillUnit,
            htbdyunit.HtbdyUnit,
        )
#         self.available_units = {
#             isisunit.HeaderUnit.FILE_KEY: (
#                 isisunit.HeaderUnit.FILE_KEY2, isisunit.HeaderUnit),
#             riverunit.RiverUnit.FILE_KEY: (
#                 riverunit.RiverUnit.FILE_KEY2, riverunit.RiverUnit), 
#             refhunit.RefhUnit.FILE_KEY: (
#                 refhunit.RefhUnit.FILE_KEY2, refhunit.RefhUnit),
#             icu.InitialConditionsUnit.FILE_KEY: (
#                 icu.InitialConditionsUnit.FILE_KEY2, icu.InitialConditionsUnit),
#             gisinfounit.GisInfoUnit.FILE_KEY: (
#                 gisinfounit.GisInfoUnit.FILE_KEY2, gisinfounit.GisInfoUnit),
#             bridgeunit.BridgeUnitArch.FILE_KEY: (
#                 bridgeunit.BridgeUnitArch.FILE_KEY2, bridgeunit.BridgeUnitArch)
#                                 'gisinfo': gisinfounit.GisInfoUnit,
#                                 'header': isisunit.HeaderUnit, 
#                                 'comment': isisunit.CommentUnit,
#                                 'bridge': bridgeunit.BridgeUnitUsbpr,
#                                 'bridge': bridgeunit.BridgeUnitArch,
#                                 'spill': spillunit.SpillUnit,
#                                 'junction': junctionunit.JunctionUnit,
#                                 'refh': refhunit.RefhUnit,
#                                 'orifice': orificeunit.OrificeUnit,
#                                 'outlet': orificeunit.OutfallUnit,
#                                 'frelief': orificeunit.FloodReliefArchUnit,
#                                 'culvert': culvertunit.CulvertInletUnit,
#                                 'culvert': culvertunit.CulvertOutletUnit,
#                                 'htbdy': htbdyunit.HtbdyUnit,
#                                 'interolate': interpolateunit.InterpolateUnit,
#         }
        
        try:
            self._getFileKeys()
        except Exception as err:
            logger.exception(err)
            logger.error('UNIT_VARS incorrectly set in some classes')
            raise Exception ('UNIT_KEYS incorrectly set in some classes')
        
    
    def _getFileKeys(self):
        """Get the file keys for the available units.
        
        Every AIsisUnit type class must declare a static variable that 
        defines the key word used in the .dat file. This is then used to
        recognise when a unit of that type has been found.
        """
        self.unit_keys = [k.FILE_KEY for k in self.available_units if k.FILE_KEY is not None]
        self.units = {}
        for u in self.available_units:
            if u.FILE_KEY is None: continue
            if not u.FILE_KEY in self.units.keys():
                self.units[u.FILE_KEY] = []
            self.units[u.FILE_KEY].append((u.FILE_KEY2, u))
            
    
    def createUnit(self, contents, file_line, file_key, file_order, reach_number = None):
        """
        """
        # Update reach number info
        if not file_key == 'RIVER' or file_key == 'COMMENT':
#         if not key == 'river' or key == 'comment':
            self.same_reach = False
            
        '''Need to deal with RiverUnit slightly differently because it records
        information about the reach number.
        Same is true for the InitialConditionsUnit as it can only know how 
        long it is by taking the number of units from the HeaderUnit.

        TODO: This needs looking into, perhaps either apply a reach number to
              all units or create a seperate lookup in the collection.
        '''
            
        # Check if we know what the unit is. If we do, instantiate it, if not
        # return the current line number and False to let the loader know
        found = False
        
        # Make sure the given FILE_KEY is found (it should be if we're here)
        if file_key in self.units.keys():
            u = self.units[file_key]
            
            # If FILE_KEY2 is none there's only a single type of this unit so
            # grab it
            if u[0][0] is None:
                unit_type = u[0][1]
                found = True
            else:
                
                # If not then find which one it is and  grab that
                key2 = contents[file_line + 1].split()[0].strip()
                for s in u:
                    if s[0] == key2:
                        unit_type = s[1]
                        found = True
        
        # If something went wrong send back as part of UnknownUnit instead
        if not found:
            return file_line, False

        read_kwargs = {}
        constructor_kwargs = {}
        if file_key == 'INITIAL':
            read_kwargs['node_count'] = self.unit_count
        elif file_key == 'RIVER':
            constructor_kwargs['reach_number'] = self.reach_number

        unit = unit_type(**constructor_kwargs)
        file_line = unit.readUnitData(contents, file_line, **read_kwargs)
        
        '''Need to grab the number of units in the initial conditions from the
        header unit because there's no way to know how long it is otherwise.
        '''
        if file_key == 'HEADER':
            self.unit_count = unit.head_data['node_count'].value
#         if key == 'header':
#             self.ic_rows = unit.node_count
        
        if file_key == 'INITIAL':
            unit._name_types = self._ic_name_types
        else:
            self.findIcLabels(unit)

        return file_line, unit
        
        
#         if file_key == 'RIVER':
#             # River can also be used for Muskingham units
#             if not contents[file_line+1].strip().startswith('SECTION'):
#                 return file_line, False
#             
#             reach_no = self._getReachNumber(reach_number)
#             unit = riverunit.RiverUnit(reach_no)
        
#         elif key == 'initialconditions' or key == 'gisinfo':
#             unit = self.available_units[key](self.ic_rows)
#         
#         elif key == 'bridge':
#             if contents[file_line + 1].strip().startswith('USBPR1978'):
#                 unit = bridgeunit.BridgeUnitUsbpr()
#             else:
#                 unit = bridgeunit.BridgeUnitArch()
#         
#         elif key == 'culvert':
#             if contents[file_line + 1].strip().startswith('INLET'):
#                 unit = culvertunit.CulvertInletUnit()
#             else:
#                 unit = culvertunit.CulvertOutletUnit()
#         
#         # All other units only need a file_order for their constructor.
#         else:
#             '''If no matching unit can be found False is return as the second
#             part of the tuple and the datloader will know to start creating an
#             UnknownUnit.
#             '''
#             if key in self.available_units.keys():
#                 unit = self.available_units[key]()
#             else:
#                 return file_line, False
        
        # Send contents to unit for construction.


    def findIcLabels(self, unit):
        """
        """
        if not unit.has_ics: return

        ic_labels = unit.icLabels()
        for l in ic_labels:
            if not l in self._ic_name_types.keys():
                self._ic_name_types[l] = [unit._unit_type]
            elif not unit._unit_type in self._ic_name_types[l]:
                self._ic_name_types[l].append(unit._unit_type) 
    
     
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
        return self.unit_keys
    
    


        
        
        
        
        
        

