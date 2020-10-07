
"""

 Summary:
    Contains the Conduit unit type classes.
    This holds all of the data read in from the conduit units in the dat file.
    Can be called to load in the data and read and update the contents
    held in the object.

 Author:
     Duncan Runnacles

 Copyright:
     Duncan Runnacles 2020

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


class ConduitUnit(AUnit):
    '''Class for dealing with conduit type units in the .dat file.'''

    # Class constants
    UNIT_TYPE = 'conduit'
    UNIT_CATEGORY = 'conduit'
    FILE_KEY = 'CONDUIT'
    FILE_KEY2 = None

    def __init__(self):
        '''Constructor.
        '''
        super(ConduitUnit, self).__init__()
        self._unit_type = ConduitUnit.UNIT_TYPE
        self._unit_category = ConduitUnit.UNIT_CATEGORY

    def icLabels(self):
        """Overriddes superclass method."""
        return [self._name, self._name_ds]

    def linkLabels(self):
        """Overriddes superclass method."""
        return {'name': self.name, 'name_ds': self.name_ds}


class RectangularConduitUnit(ConduitUnit):

    # Class constants
    UNIT_TYPE = 'conduit_rectangular'
    UNIT_CATEGORY = 'conduit'
    FILE_KEY = 'CONDUIT'
    FILE_KEY2 = 'RECTANGULAR'

    def __init__(self, **kwargs):
        '''Constructor.
        '''
        super(RectangularConduitUnit, self).__init__(**kwargs)
        self._unit_type = RectangularConduitUnit.UNIT_TYPE
        self._unit_category = RectangularConduitUnit.UNIT_CATEGORY

        self.head_data = {
            'comment': HeadDataItem('', '', 0, 0, dtype=dt.STRING),
            'distance': HeadDataItem(0.000, '{:>10}', 3, 0, dtype=dt.FLOAT, dps=3),
            'roughness_type': HeadDataItem('MANNING', '', 4, 0, dtype=dt.CONSTANT, choices=('MANNING', 'COLEBROOK-WHITE')),
            'invert': HeadDataItem(0.000, '{:>10}', 5, 0, dtype=dt.FLOAT, dps=3),
            'width': HeadDataItem(0.000, '{:>10}', 5, 1, dtype=dt.FLOAT, dps=3),
            'height': HeadDataItem(0.000, '{:>10}', 5, 2, dtype=dt.FLOAT, dps=3),
            'bottom_slot_status': HeadDataItem('GLOBAL', '{:>10}', 5, 3, dtype=dt.CONSTANT, choices=('ON', 'OFF', 'GLOBAL')),
            'bottom_slot_distance': HeadDataItem(0.000, '{:>10}', 5, 4, dtype=dt.FLOAT, dps=3),
            'bottom_slot_depth': HeadDataItem(0.000, '{:>10}', 5, 5, dtype=dt.FLOAT, dps=3),
            'top_slot_status': HeadDataItem('GLOBAL', '{:>10}', 5, 6, dtype=dt.CONSTANT, choices=('ON', 'OFF', 'GLOBAL')),
            'top_slot_distance': HeadDataItem(0.000, '{:>10}', 5, 7, dtype=dt.FLOAT, dps=3),
            'top_slot_depth': HeadDataItem(0.000, '{:>10}', 5, 8, dtype=dt.FLOAT, dps=3),
            'roughness_invert': HeadDataItem(0.000, '{:>10}', 6, 0, dtype=dt.FLOAT, dps=5),
            'roughness_walls': HeadDataItem(0.000, '{:>10}', 6, 1, dtype=dt.FLOAT, dps=5),
            'roughness_soffit': HeadDataItem(0.000, '{:>10}', 6, 2, dtype=dt.FLOAT, dps=5),
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
        self.head_data['distance'].value = unit_data[file_line + 3][:10].strip()
        self.head_data['roughness_type'].value = unit_data[file_line + 4][:10].strip()
        self.head_data['invert'].value = unit_data[file_line + 5][:10].strip()
        self.head_data['width'].value = unit_data[file_line + 5][10:20].strip()
        self.head_data['height'].value = unit_data[file_line + 5][20:30].strip()
        self.head_data['bottom_slot_status'].value = unit_data[file_line + 5][30:40].strip()
        self.head_data['bottom_slot_distance'].value = unit_data[file_line + 5][40:50].strip()
        self.head_data['bottom_slot_depth'].value = unit_data[file_line + 5][50:60].strip()
        self.head_data['top_slot_status'].value = unit_data[file_line + 5][60:70].strip()
        self.head_data['top_slot_distance'].value = unit_data[file_line + 5][70:80].strip()
        self.head_data['top_slot_depth'].value = unit_data[file_line + 5][80:].strip()
        self.head_data['roughness_invert'].value = unit_data[file_line + 6][:10].strip()
        self.head_data['roughness_walls'].value = unit_data[file_line + 6][10:20].strip()
        self.head_data['roughness_soffit'].value = unit_data[file_line + 6][20:].strip()
        return file_line + 6

    def getData(self):
        '''Returns the formatted data for this unit.

        See Also:
            isisunit.

        Returns:
            List of strings formatted for writing to the new dat file.
        '''
        out = []
        out.append('CONDUIT ' + self.head_data['comment'].value)
        out.append('\nRECTANGULAR')
        out.append('\n' + '{:<12}'.format(self._name) + '{:<12}'.format(self._name_ds))

        key_order = ['distance', 'roughness_type', 'invert', 'width', 'height', 
                     'bottom_slot_status', 'bottom_slot_distance', 'bottom_slot_depth',
                     'top_slot_status', 'top_slot_distance', 'top_slot_depth',
                     'roughness_invert', 'roughness_walls', 'roughness_soffit']
        for k in key_order:
            out.append(self.head_data[k].format(True))
        out_data = ''.join(out).split('\n')
        return out_data


class CircularConduitUnit(ConduitUnit):

    # Class constants
    UNIT_TYPE = 'conduit_circular'
    UNIT_CATEGORY = 'conduit'
    FILE_KEY = 'CONDUIT'
    FILE_KEY2 = 'CIRCULAR'

    def __init__(self, **kwargs):
        '''Constructor.
        '''
        super(CircularConduitUnit, self).__init__(**kwargs)
        self._unit_type = CircularConduitUnit.UNIT_TYPE
        self._unit_category = CircularConduitUnit.UNIT_CATEGORY

        self.head_data = {
            'comment': HeadDataItem('', '', 0, 0, dtype=dt.STRING),
            'distance': HeadDataItem(0.000, '{:>10}', 3, 0, dtype=dt.FLOAT, dps=3),
            'roughness_type': HeadDataItem('MANNING', '', 4, 0, dtype=dt.CONSTANT, choices=('MANNING', 'COLEBROOK-WHITE')),
            'invert': HeadDataItem(0.000, '{:>10}', 5, 0, dtype=dt.FLOAT, dps=3),
            'diameter': HeadDataItem(0.000, '{:>10}', 5, 1, dtype=dt.FLOAT, dps=3),
            'bottom_slot_status': HeadDataItem('GLOBAL', '{:>10}', 5, 2, dtype=dt.CONSTANT, choices=('ON', 'OFF', 'GLOBAL')),
            'bottom_slot_distance': HeadDataItem(0.000, '{:>10}', 5, 3, dtype=dt.FLOAT, dps=3),
            'bottom_slot_depth': HeadDataItem(0.000, '{:>10}', 5, 4, dtype=dt.FLOAT, dps=3),
            'top_slot_status': HeadDataItem('GLOBAL', '{:>10}', 5, 5, dtype=dt.CONSTANT, choices=('ON', 'OFF', 'GLOBAL')),
            'top_slot_distance': HeadDataItem(0.000, '{:>10}', 5, 6, dtype=dt.FLOAT, dps=3),
            'top_slot_depth': HeadDataItem(0.000, '{:>10}', 5, 7, dtype=dt.FLOAT, dps=3),
            'roughness_below_axis': HeadDataItem(0.000, '{:>10}', 6, 0, dtype=dt.FLOAT, dps=5),
            'roughness_above_axis': HeadDataItem(0.000, '{:>10}', 6, 1, dtype=dt.FLOAT, dps=5),
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
        self.head_data['distance'].value = unit_data[file_line + 3][:10].strip()
        self.head_data['roughness_type'].value = unit_data[file_line + 4][:10].strip()
        self.head_data['invert'].value = unit_data[file_line + 5][:10].strip()
        self.head_data['diameter'].value = unit_data[file_line + 5][10:20].strip()
        self.head_data['bottom_slot_status'].value = unit_data[file_line + 5][20:30].strip()
        self.head_data['bottom_slot_distance'].value = unit_data[file_line + 5][30:40].strip()
        self.head_data['bottom_slot_depth'].value = unit_data[file_line + 5][40:50].strip()
        self.head_data['top_slot_status'].value = unit_data[file_line + 5][50:60].strip()
        self.head_data['top_slot_distance'].value = unit_data[file_line + 5][60:70].strip()
        self.head_data['top_slot_depth'].value = unit_data[file_line + 5][70:].strip()
        self.head_data['roughness_below_axis'].value = unit_data[file_line + 6][:10].strip()
        self.head_data['roughness_above_axis'].value = unit_data[file_line + 6][10:20].strip()
        return file_line + 6

    def getData(self):
        '''Returns the formatted data for this unit.

        See Also:
            isisunit.

        Returns:
            List of strings formatted for writing to the new dat file.
        '''
        out = []
        out.append('CONDUIT ' + self.head_data['comment'].value)
        out.append('\nCIRCULAR')
        out.append('\n' + '{:<12}'.format(self._name) + '{:<12}'.format(self._name_ds))

        key_order = ['distance', 'roughness_type', 'invert', 'diameter',
                     'bottom_slot_status', 'bottom_slot_distance', 'bottom_slot_depth',
                     'top_slot_status', 'top_slot_distance', 'top_slot_depth',
                     'roughness_below_axis', 'roughness_above_axis']
        for k in key_order:
            out.append(self.head_data[k].format(True))
        out_data = ''.join(out).split('\n')
        return out_data