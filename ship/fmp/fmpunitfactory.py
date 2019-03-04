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

 Updates:
     DR - 21/02/16: Major change to the setup of the factory. It no longer 
     scans the .dat file contents to identify the extent of the section and 
     passes only that to the unit. It now identifies the unit type to create 
     and hands the entire contents list to the new unit which extracts the 
     data required.

"""

from __future__ import unicode_literals

from ship.fmp.datunits import spillunit
from ship.fmp.datunits import riverunit
from ship.fmp.datunits import junctionunit
from ship.fmp.datunits import initialconditionsunit as icu
from ship.fmp.datunits import gisinfounit
from ship.fmp.datunits import bridgeunit
from ship.fmp.datunits import isisunit
from ship.fmp.datunits import refhunit
from ship.fmp.datunits import orificeunit
from ship.fmp.datunits import culvertunit
from ship.fmp.datunits import htbdyunit
from ship.fmp.datunits import interpolateunit
from ship.fmp.datunits import reservoirunit

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class FmpUnitFactory(object):
    """Builds isisunit type objects.

    This is a Factory pattern object for the creation of isisunit subclasses.
    """
    available_units = (
        isisunit.HeaderUnit,
        isisunit.CommentUnit,
        riverunit.RiverUnit,
        refhunit.RefhUnit,
        icu.InitialConditionsUnit,
        gisinfounit.GisInfoUnit,
        bridgeunit.BridgeUnitArch,
        bridgeunit.BridgeUnitUsbpr,
        spillunit.SpillUnit,
        htbdyunit.HtbdyUnit,
        junctionunit.JunctionUnit,
        orificeunit.OrificeUnit,
        orificeunit.FloodReliefUnit,
        orificeunit.OutfallUnit,
        culvertunit.CulvertUnitInlet,
        culvertunit.CulvertUnitOutlet,
        interpolateunit.InterpolateUnit,
        reservoirunit.ReservoirUnit,
    )

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

        try:
            self._getFileKeys()
        except Exception as err:
            logger.exception(err)
            logger.error('UNIT_VARS incorrectly set in some classes')
            raise Exception('UNIT_KEYS incorrectly set in some classes')

    def _getFileKeys(self):
        """Get the file keys for the available units.

        Every AUnit type class must declare a static variable that 
        defines the key word used in the .dat file. This is then used to
        recognise when a unit of that type has been found.
        """
        self.unit_keys = [k.FILE_KEY for k in FmpUnitFactory.available_units if k.FILE_KEY is not None]
        self.units = {}
        for u in FmpUnitFactory.available_units:
            if u.FILE_KEY is None:
                continue
            if not u.FILE_KEY in self.units.keys():
                self.units[u.FILE_KEY] = []
            self.units[u.FILE_KEY].append((u.FILE_KEY2, u))

    def createUnitFromFile(self, contents, file_line, file_key, file_order, reach_number=None):
        """
        """
        # Update reach number info
        if not file_key == 'RIVER' or file_key == 'COMMENT':
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
            read_kwargs['name_types'] = self._ic_name_types
        elif file_key == 'RIVER':
            constructor_kwargs['reach_number'] = self.reach_number

        unit = unit_type(**constructor_kwargs)
        
        # If the unit fails to load print the first line out to help with debugging
        try:
            file_line = unit.readUnitData(contents, file_line, **read_kwargs)
        except ValueError as err:
            print('Load failed at the following line:')
            print(contents[file_line])
            print('On dat file line number: {0}'.format(file_line + 1))
            raise

        # Need to grab the number of units in the initial conditions from the
        # header unit because there's no way to know how long it is otherwise.
        if file_key == 'HEADER':
            self.unit_count = unit.head_data['node_count'].value

        if file_key != 'INITIAL':
            self.findIcLabels(unit)

        return file_line, unit

    @staticmethod
    def createUnit(unit_type, **kwargs):
        """Create a new AUnit.

        **kwargs:
            'name': the name variable to apply to the unit. If not found
                'unknown' will be set.
            'name_ds': the name_ds variable to apply to the unit. If not found
                'unknown' will be set.
            head_data: dict of head_data values to set in the AUnit.
            row_data: dict of row_data keys containing lists of row data to
                set in the unit.
            no_copy(bool): When adding any row_data given to a new unit the
                no_copy flag will be given to the RowDataCollection.addRow()
                method. When True it stops the call to deepcopy while updating
                the rows. It's probably not needed when creating a new unit and
                it can be time-consuming. The default is True. See 
                RowDataCollection.addRow() for more details.

        The row_data kwarg is expected to be set out like the following::

            self.brg_rowdata = {
                'main': [
                    {rdt.CHAINAGE: 0.0, rdt.ELEVATION: 20.0},
                    {rdt.CHAINAGE: 2.0, rdt.ELEVATION: 10.0},
                    {rdt.CHAINAGE: 4.0, rdt.ELEVATION: 10.0},
                    {rdt.CHAINAGE: 6.0, rdt.ELEVATION: 20.0},
                ],
                'opening': [
                    {rdt.OPEN_START: 0.0, rdt.OPEN_END: 2.0},
                    {rdt.OPEN_START: 4.0, rdt.OPEN_END: 6.0}
                ]
            }

        I.e. dict's of row_data types to update, containing a list of row_vals
        data to set. These will be used to call the addRow() method in the
        AUnit. The contents of the list entries will be specific to the
        unit_type. For more information see the addRow() method and row_data
        setup of specific AUnit's.

        Args:
            unit_type(str): the AUnit.UNIT_TYPE to create.

        Return:
            AUnit - the newly created unit.
        """
        u = None
        for i in FmpUnitFactory.available_units:
            if i.UNIT_TYPE == unit_type:
                u = i

        if u is None:
            raise ValueError("unit type '" + str(unit_type) + "' is not supported")

        unit = u()
        head_data = kwargs.get('head_data', None)
        row_data = kwargs.get('row_data', None)
        unit.name = kwargs.get('name', 'unknown')
        unit.name_ds = kwargs.get('name_ds', 'unknown')
        no_copy = kwargs.get('no_copy', True)

        if unit.unit_category == 'river':
            unit.reach_number = kwargs.get('reach_number', -1)

        # Update any head_data values given
        if head_data is not None:
            head_keys = unit.head_data.keys()
            for key, val in head_data.items():
                if key in head_keys:
                    unit.head_data[key].value = val

        # Update any row_data entries given
        if row_data is not None:
            rowdata_keys = unit.row_data.keys()
            # For different RowDataCollections
            for row_key, row_data in row_data.items():
                if row_key in rowdata_keys:
                    # For different rows to add
                    for entry in row_data:
                        unit.row_data[row_key].addRow(entry, no_copy=no_copy)

        return unit

    def findIcLabels(self, unit):
        """
        """
        if not unit.has_ics:
            return

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
