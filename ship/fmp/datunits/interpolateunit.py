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
from __future__ import unicode_literals

from ship.fmp.datunits.isisunit import AUnit
from ship.fmp.headdata import HeadDataItem
from ship.datastructures import DATA_TYPES as dt

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class InterpolateUnit(AUnit):
    '''Class for dealing with Interpolate units in the .dat file.'''

    # Class constants
    UNIT_TYPE = 'interpolate'
    UNIT_CATEGORY = 'interpolate'
    FILE_KEY = 'INTERPOLATE'
    FILE_KEY2 = None

    def __init__(self):
        '''Constructor.

        Args:
            file_order (int): the order of this unit in the .dat file.
        '''
        super(InterpolateUnit, self).__init__()
        self._unit_type = InterpolateUnit.UNIT_TYPE
        self._unit_category = InterpolateUnit.UNIT_CATEGORY
        self._name = 'Interp'

        self.head_data = {
            'comment': HeadDataItem('', '', 0, 0, dtype=dt.STRING),
            'spill1': HeadDataItem('', '{:<12}', 1, 0, dtype=dt.STRING),
            'spill2': HeadDataItem('', '{:<12}', 1, 1, dtype=dt.STRING),
            'lateral1': HeadDataItem('', '{:<12}', 1, 2, dtype=dt.STRING),
            'lateral2': HeadDataItem('', '{:<12}', 1, 3, dtype=dt.STRING),
            'lateral3': HeadDataItem('', '{:<12}', 1, 4, dtype=dt.STRING),
            'lateral4': HeadDataItem('', '{:<12}', 1, 5, dtype=dt.STRING),
            'distance': HeadDataItem(0.00, '{:>10}', 2, 0, dtype=dt.FLOAT, dps=3),
            'easting': HeadDataItem(0.00, '{:>10}', 2, 1, dtype=dt.FLOAT, dps=3, default=0.00),
            'northing': HeadDataItem(0.00, '{:>10}', 2, 2, dtype=dt.FLOAT, dps=3, default=0.00),
        }

    def icLabels(self):
        """Overriddes superclass method."""
        return [self._name]

    def readUnitData(self, unit_data, file_line):
        '''Reads the given data into the object.

        See Also:
            isisunit.

        Args:
            unit_data (list): The raw file data to be processed.
        '''
        self.head_data['comment'].value = unit_data[file_line][12:].strip()
        self._name = unit_data[file_line + 1][:12].strip()
        self.head_data['spill1'].value = unit_data[file_line + 1][12:24].strip()
        self.head_data['spill2'].value = unit_data[file_line + 1][24:36].strip()
        self.head_data['lateral1'].value = unit_data[file_line + 1][36:48].strip()
        self.head_data['lateral2'].value = unit_data[file_line + 1][48:60].strip()
        self.head_data['lateral3'].value = unit_data[file_line + 1][60:72].strip()
        self.head_data['lateral4'].value = unit_data[file_line + 1][72:84].strip()
        self.head_data['distance'].value = unit_data[file_line + 2][:10].strip()
        self.head_data['easting'].value = unit_data[file_line + 2][10:20].strip()
        self.head_data['northing'].value = unit_data[file_line + 2][20:30].strip()
        return file_line + 2

    def getData(self):
        '''Returns the formatted data for this unit.

        See Also:
            isisunit.

        Returns:
            List of strings formatted for writing to the new dat file.
        '''
        out = []
        out.append('INTERPOLATE ' + self.head_data['comment'].value)
        out.append('\n' + '{:<12}'.format(self._name))
        key_order1 = ['spill1', 'spill2', 'lateral1', 'lateral2', 'lateral3',
                      'lateral4']
        for k in key_order1:
            out.append(self.head_data[k].format())
        key_order2 = ['distance', 'easting', 'northing']
        for k in key_order2:
            out.append(self.head_data[k].format(True))
        out_data = ''.join(out).split('\n')
        return out_data
