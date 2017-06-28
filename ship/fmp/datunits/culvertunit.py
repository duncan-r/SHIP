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

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""

from ship.fmp.datunits.isisunit import AUnit
from ship.fmp.headdata import HeadDataItem
from ship.datastructures import DATA_TYPES as dt


class CulvertUnit(AUnit):
    '''Class for dealing with Inlet Culvert units in the .dat file.'''

    # Class constants
    UNIT_TYPE = 'culvert'
    UNIT_CATEGORY = 'culvert'
    FILE_KEY = 'CULVERT'
    FILE_KEY2 = None

    def __init__(self):
        '''Constructor.
        '''
        super(CulvertUnit, self).__init__()
        self._unit_type = CulvertUnit.UNIT_TYPE
        self._unit_category = CulvertUnit.UNIT_CATEGORY

    def icLabels(self):
        """Overriddes superclass method."""
        return [self._name, self._name_ds]

    def linkLabels(self):
        """Overriddes superclass method."""
        return {'name': self.name, 'name_ds': self.name_ds}


class CulvertUnitInlet(CulvertUnit):

    # Class constants
    UNIT_TYPE = 'culvert_inlet'
    UNIT_CATEGORY = 'culvert'
    FILE_KEY = 'CULVERT'
    FILE_KEY2 = 'INLET'

    def __init__(self, **kwargs):
        '''Constructor.
        '''
        super(CulvertUnitInlet, self).__init__(**kwargs)
        self._unit_type = CulvertUnitInlet.UNIT_TYPE
        self._unit_category = CulvertUnitInlet.UNIT_CATEGORY

        self.head_data = {
            'comment': HeadDataItem('', '', 0, 0, dtype=dt.STRING),
            'k': HeadDataItem(0.000, '{:>10}', 2, 0, dtype=dt.FLOAT, dps=4),
            'm': HeadDataItem(0.000, '{:>10}', 2, 1, dtype=dt.FLOAT, dps=3),
            'c': HeadDataItem(0.000, '{:>10}', 2, 2, dtype=dt.FLOAT, dps=4),
            'y': HeadDataItem(0.000, '{:>10}', 2, 3, dtype=dt.FLOAT, dps=3),
            'ki': HeadDataItem(0.000, '{:>10}', 2, 4, dtype=dt.FLOAT, dps=3),
            'conduit_type': HeadDataItem('A', '{:>10}', 2, 5, dtype=dt.CONSTANT, choices=('A', 'B', 'C')),
            'screen_width': HeadDataItem(0.000, '{:>10}', 3, 0, dtype=dt.FLOAT, dps=3),
            'bar_proportion': HeadDataItem(0.000, '{:>10}', 3, 1, dtype=dt.FLOAT, dps=3),
            'debris_proportion': HeadDataItem(0.000, '{:>10}', 3, 2, dtype=dt.FLOAT, dps=3),
            'loss_coef': HeadDataItem(0.000, '{:>10}', 3, 3, dtype=dt.FLOAT, dps=3),
            'trashscreen_height': HeadDataItem(0.000, '{:>10}', 3, 4, dtype=dt.FLOAT, dps=3),
            'headloss_type': HeadDataItem('STATIC', '{:>10}', 3, 5, dtype=dt.CONSTANT, choices=('STATIC', 'TOTAL')),
            'reverse_flow_model': HeadDataItem('CALCULATED', '{:<10}', 3, 6, dtype=dt.CONSTANT, choices=('CALCULATED', 'ZERO')),
        }

    def readUnitData(self, unit_data, file_line):
        '''Reads the given data into the object.

        See Also:
            isisunit.

        Args:
            unit_data (list): The raw file data to be processed.
        '''
        self.head_data['comment'].value = unit_data[file_line][8:].strip()
        self._name = unit_data[file_line + 2][:12].strip()
        self._name_ds = unit_data[file_line + 2][12:].strip()
        self.head_data['k'].value = unit_data[file_line + 3][:10].strip()
        self.head_data['m'].value = unit_data[file_line + 3][10:20].strip()
        self.head_data['c'].value = unit_data[file_line + 3][20:30].strip()
        self.head_data['y'].value = unit_data[file_line + 3][30:40].strip()
        self.head_data['ki'].value = unit_data[file_line + 3][40:50].strip()
        self.head_data['conduit_type'].value = unit_data[file_line + 3][50:60].strip()
        self.head_data['screen_width'].value = unit_data[file_line + 4][:10].strip()
        self.head_data['bar_proportion'].value = unit_data[file_line + 4][10:20].strip()
        self.head_data['debris_proportion'].value = unit_data[file_line + 4][20:30].strip()
        self.head_data['loss_coef'].value = unit_data[file_line + 4][30:40].strip()
        self.head_data['reverse_flow_model'].value = unit_data[file_line + 4][40:50].strip()
        self.head_data['headloss_type'].value = unit_data[file_line + 4][50:60].strip()
        self.head_data['trashscreen_height'].value = unit_data[file_line + 4][60:].strip()
        return file_line + 4

    def getData(self):
        '''Returns the formatted data for this unit.

        See Also:
            isisunit.

        Returns:
            List of strings formatted for writing to the new dat file.
        '''
        out = []
        out.append('CULVERT ' + self.head_data['comment'].value)
        out.append('\nINLET')
        out.append('\n' + '{:<12}'.format(self._name) + '{:<12}'.format(self._name_ds))

        key_order = ['k', 'm', 'c', 'y', 'ki', 'conduit_type', 'screen_width',
                     'bar_proportion', 'debris_proportion', 'loss_coef',
                     'reverse_flow_model', 'headloss_type', 'trashscreen_height']
        for k in key_order:
            out.append(self.head_data[k].format(True))
        out_data = ''.join(out).split('\n')
        return out_data


class CulvertUnitOutlet(CulvertUnit):

    # Class constants
    UNIT_TYPE = 'culvert_outlet'
    CATEGORY = 'culvert'
    FILE_KEY = 'CULVERT'
    FILE_KEY2 = 'OUTLET'

    def __init__(self):
        super(CulvertUnitOutlet, self).__init__()
        self._unit_type = CulvertUnitOutlet.UNIT_TYPE
        self._unit_category = CulvertUnitOutlet.UNIT_CATEGORY

        self.head_data = {
            'comment': HeadDataItem('', '', 0, 0, dtype=dt.STRING),
            'loss_coef': HeadDataItem(0.000, '{:>10}', 2, 0, dtype=dt.FLOAT, dps=3),
            'headloss_type': HeadDataItem('STATIC', '{:>10}', 2, 1, dtype=dt.CONSTANT, choices=('STATIC', 'TOTAL')),
            'reverse_flow_model': HeadDataItem('CALCULATED', '{:<10}', 2, 2, dtype=dt.CONSTANT, choices=('CALCULATED', 'ZERO')),
        }

    def readUnitData(self, unit_data, file_line):
        '''Reads the given data into the object.

        See Also:
            isisunit.

        Args:
            unit_data (list): The raw file data to be processed.
        '''
        self.head_data['comment'].value = unit_data[file_line][8:].strip()
        self._name = unit_data[file_line + 2][:12].strip()
        self._name_ds = unit_data[file_line + 2][12:].strip()
        self.head_data['loss_coef'].value = unit_data[file_line + 3][:10].strip()
        self.head_data['reverse_flow_model'].value = unit_data[file_line + 3][10:20].strip()
        self.head_data['headloss_type'].value = unit_data[file_line + 3][20:].strip()
        return file_line + 3

    def getData(self):
        '''Returns the formatted data for this unit.

        See Also:
            isisunit.

        Returns:
            List of strings formatted for writing to the new dat file.
        '''
        out = []
        out.append('CULVERT ' + self.head_data['comment'].value)
        out.append('\nOUTLET')
        out.append('\n' + '{:>12}'.format(self._name) + '{:>12}'.format(self._name_ds))

        key_order = ['loss_coef', 'reverse_flow_model', 'headloss_type']
        for k in key_order:
            out.append(self.head_data[k].format(True))
        out_data = ''.join(out).split('\n')
        return out_data
