"""

 Summary:
    Contains classes for grouping AUnit types based on certain conditions.

    Currently contains:

        - LinkedUnits:
            Stores all of the direct associates of a particular unit. See the
            linkedUnits() method in DatCollection for more information.

 Author:
     Duncan Runnacles

 Created:
     02 Dec 2016

 Copyright:
     Duncan Runnacles 2016

 TODO:

 Updates:


"""

from __future__ import unicode_literals


class LinkedUnits(object):
    """Stores all units directly associated to a specific unit.

    main_unit: the unit to derive associates from.
    us_unit: the unit immediately above main_unit in the .dat/.ied file.
    ds_unit: the unit immediately below main_unit in the .dat/.ied file.
    named_units: all units that are specifically referenced by the main_unit
        within it's head_data (e.g. remote_us and remote_ds in bridge units).
    junctions: a list of all of the junctions that refer to the main_unit. Each
        list entry contains a tuple where [0] is the JunctionUnit and [1] is a
        list of units referenced by that junction.
    """

    def __init__(self, main_unit):
        self.main_unit = main_unit
        self.us_unit = None
        self.ds_unit = None
        self.named_unit = []
        self.junctions = []

    def addLinkedUnit(self, unit, link_type, additionals=None):
        """Add a unit to this LinkedUnits contents.

        Args:
            unit: the unit to add.
            link_type(str): the type of unit being added. Includes: 'upstream',
                'downstream', 'named' and 'junction'.
            additionals=None(list): used when link_type == 'junction' contains
                a list of all of the units referened by the JunctionUnit.
        """
        if link_type == 'upstream':
            self.us_unit = unit
        if link_type == 'downstream':
            self.ds_unit = unit
        if link_type == 'named':
            self.named_units.append(unit)
        if link_type == 'junction':
            self.junctions.append((unit, None))
            if additionals:
                self.junctions[-1][1] = additionals
