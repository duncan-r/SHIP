
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
from ship.fmp.datunits import ROW_DATA_TYPES as rdt
from ship.datastructures import dataobject as do
from ship.datastructures.rowdatacollection import RowDataCollection


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
        self.head_data['roughness_type'].value = unit_data[file_line + 4][:15].strip()
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
        self.head_data['roughness_type'].value = unit_data[file_line + 4][:15].strip()
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
    

class FullarchConduitUnit(ConduitUnit):

    # Class constants
    UNIT_TYPE = 'conduit_fullarch'
    UNIT_CATEGORY = 'conduit'
    FILE_KEY = 'CONDUIT'
    FILE_KEY2 = 'FULLARCH'

    def __init__(self, **kwargs):
        '''Constructor.
        '''
        super(FullarchConduitUnit, self).__init__(**kwargs)
        self._unit_type = FullarchConduitUnit.UNIT_TYPE
        self._unit_category = FullarchConduitUnit.UNIT_CATEGORY

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
        self.head_data['roughness_type'].value = unit_data[file_line + 4][:15].strip()
        self.head_data['invert'].value = unit_data[file_line + 5][:10].strip()
        self.head_data['width'].value = unit_data[file_line + 5][10:20].strip()
        self.head_data['height'].value = unit_data[file_line + 5][20:30].strip()
        self.head_data['bottom_slot_status'].value = unit_data[file_line + 5][30:40].strip()
        self.head_data['bottom_slot_distance'].value = unit_data[file_line + 5][40:50].strip()
        self.head_data['bottom_slot_depth'].value = unit_data[file_line + 5][50:60].strip()
        self.head_data['top_slot_status'].value = unit_data[file_line + 5][60:70].strip()
        self.head_data['top_slot_distance'].value = unit_data[file_line + 5][70:80].strip()
        self.head_data['top_slot_depth'].value = unit_data[file_line + 5][80:].strip()
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
        out.append('\nFULLARCH')
        out.append('\n' + '{:<12}'.format(self._name) + '{:<12}'.format(self._name_ds))

        key_order = ['distance', 'roughness_type', 'invert', 'width', 'height',
                     'bottom_slot_status', 'bottom_slot_distance', 'bottom_slot_depth',
                     'top_slot_status', 'top_slot_distance', 'top_slot_depth',
                     'roughness_below_axis', 'roughness_above_axis']
        for k in key_order:
            out.append(self.head_data[k].format(True))
        out_data = ''.join(out).split('\n')
        return out_data
    

class SprungarchConduitUnit(ConduitUnit):

    # Class constants
    UNIT_TYPE = 'conduit_sprungarch'
    UNIT_CATEGORY = 'conduit'
    FILE_KEY = 'CONDUIT'
    FILE_KEY2 = 'SPRUNGARCH'

    def __init__(self, **kwargs):
        '''Constructor.
        '''
        super(SprungarchConduitUnit, self).__init__(**kwargs)
        self._unit_type = SprungarchConduitUnit.UNIT_TYPE
        self._unit_category = SprungarchConduitUnit.UNIT_CATEGORY

        self.head_data = {
            'comment': HeadDataItem('', '', 0, 0, dtype=dt.STRING),
            'distance': HeadDataItem(0.000, '{:>10}', 3, 0, dtype=dt.FLOAT, dps=3),
            'roughness_type': HeadDataItem('MANNING', '', 4, 0, dtype=dt.CONSTANT, choices=('MANNING', 'COLEBROOK-WHITE')),
            'invert': HeadDataItem(0.000, '{:>10}', 5, 0, dtype=dt.FLOAT, dps=3),
            'width': HeadDataItem(0.000, '{:>10}', 5, 1, dtype=dt.FLOAT, dps=3),
            'springing_height': HeadDataItem(0.000, '{:>10}', 5, 2, dtype=dt.FLOAT, dps=3),
            'crown_height': HeadDataItem(0.000, '{:>10}', 5, 3, dtype=dt.FLOAT, dps=3),
            'bottom_slot_status': HeadDataItem('GLOBAL', '{:>10}', 5, 4, dtype=dt.CONSTANT, choices=('ON', 'OFF', 'GLOBAL')),
            'bottom_slot_distance': HeadDataItem(0.000, '{:>10}', 5, 5, dtype=dt.FLOAT, dps=3),
            'bottom_slot_depth': HeadDataItem(0.000, '{:>10}', 5, 6, dtype=dt.FLOAT, dps=3),
            'top_slot_status': HeadDataItem('GLOBAL', '{:>10}', 5, 7, dtype=dt.CONSTANT, choices=('ON', 'OFF', 'GLOBAL')),
            'top_slot_distance': HeadDataItem(0.000, '{:>10}', 5, 8, dtype=dt.FLOAT, dps=3),
            'top_slot_depth': HeadDataItem(0.000, '{:>10}', 5, 9, dtype=dt.FLOAT, dps=3),
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
        self.head_data['roughness_type'].value = unit_data[file_line + 4][:15].strip()
        self.head_data['invert'].value = unit_data[file_line + 5][:10].strip()
        self.head_data['width'].value = unit_data[file_line + 5][10:20].strip()
        self.head_data['springing_height'].value = unit_data[file_line + 5][20:30].strip()
        self.head_data['crown_height'].value = unit_data[file_line + 5][30:40].strip()
        self.head_data['bottom_slot_status'].value = unit_data[file_line + 5][40:50].strip()
        self.head_data['bottom_slot_distance'].value = unit_data[file_line + 5][50:60].strip()
        self.head_data['bottom_slot_depth'].value = unit_data[file_line + 5][60:70].strip()
        self.head_data['top_slot_status'].value = unit_data[file_line + 5][70:80].strip()
        self.head_data['top_slot_distance'].value = unit_data[file_line + 5][80:90].strip()
        self.head_data['top_slot_depth'].value = unit_data[file_line + 5][90:].strip()
        self.head_data['roughness_invert'].value = unit_data[file_line + 6][:10].strip()
        self.head_data['roughness_walls'].value = unit_data[file_line + 6][10:20].strip()
        self.head_data['roughness_soffit'].value = unit_data[file_line + 6][20:30].strip()
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
        out.append('\nSPRUNGARCH')
        out.append('\n' + '{:<12}'.format(self._name) + '{:<12}'.format(self._name_ds))

        key_order = ['distance', 'roughness_type', 'invert', 'width', 'springing_height',
                     'crown_height', 'bottom_slot_status', 'bottom_slot_distance', 
                     'bottom_slot_depth', 'top_slot_status', 'top_slot_distance', 
                     'top_slot_depth', 'roughness_invert', 'roughness_walls',
                     'roughness_soffit']
        for k in key_order:
            out.append(self.head_data[k].format(True))
        out_data = ''.join(out).split('\n')
        return out_data
    
    
class RowDataConduitType(ConduitUnit):

    def __init__(self, **kwargs):
        '''Constructor.
        '''
        super(RowDataConduitType, self).__init__(**kwargs)
        self._setup_headdata()

        dobjs = [
            # update_callback is called every time a value is added or updated
            do.FloatData(rdt.CHAINAGE, format_str='{:>10}', no_of_dps=3),
            do.FloatData(rdt.ELEVATION, format_str='{:>10}', no_of_dps=3),
            # Note roughness much be Colebrook-White for Symmetrical conduits
            do.FloatData(rdt.ROUGHNESS, format_str='{:>10}', default=0.039, no_of_dps=5),
        ]
        self.row_data['main'] = RowDataCollection.bulkInitCollection(dobjs)
        self.row_data['main'].setDummyRow({rdt.CHAINAGE: 0, rdt.ELEVATION: 0, rdt.ROUGHNESS: 0})
        
    def _setup_headdata(self):
        pass

    def readUnitData(self, unit_data, file_line):
        '''Reads the given data into the object.

        See Also:
            isisunit.

        Args:
            unit_data (list): The raw file data to be processed.
        '''
        file_line = self._readHeadData(unit_data, file_line)
        file_line = self._readRowData(unit_data, file_line)
        return file_line - 1

    def _readRowData(self, unit_data, file_line):
        """Reads the units rows into the row collection.

        This is all the geometry data that occurs after the no of rows variable in
        the River Units of the dat file.

        Args:
            unit_data (list): the data pertaining to this unit.
        """
        end_line = int(unit_data[file_line].strip())
        file_line += 1
        try:
            # Load the geometry data
            for i in range(file_line, end_line + file_line):
                chain = unit_data[i][0:10].strip()
                elev = unit_data[i][10:20].strip()
                rough = unit_data[i][20:30].strip()

                self.row_data['main'].addRow(
                    {rdt.CHAINAGE: chain, rdt.ELEVATION: elev, rdt.ROUGHNESS: rough},
                    # We don't need to make backup copies here. If it fails the
                    # load fails anyway and this will just really slow us down
                    no_copy=True
                )

        except NotImplementedError:
            logger.ERROR('Unable to read Unit Data(dataRowObject creation) - NotImplementedError')
            raise

        return end_line + file_line

    def getData(self):
        """Retrieve the data in this unit.

        The String[] returned is formatted for printing in the fashion
        of the .dat file.

        Return:
            List of strings formated for writing to .dat file.
        """
        row_count = self.row_data['main'].numberOfRows()
        out_data = self._getHeadData()
        out_data.append('{:>10}'.format(row_count))
        out_data.extend(self._getRowData(row_count))
        return out_data

    def _getRowData(self, row_count):
        """Returns the row data in this class.

        For all the rows in the river geometry section get the data from
        the rowdatacollection class.

        Returns:
            list = containing the formatted unit rows.
        """
        out_data = []
        for i in range(0, row_count):
            out_data.append(self.row_data['main'].getPrintableRow(i))
        return out_data


class SymmetricalConduitUnit(RowDataConduitType):

    # Class constants
    UNIT_TYPE = 'conduit_symmetrical'
    UNIT_CATEGORY = 'conduit'
    FILE_KEY = 'CONDUIT'
    FILE_KEY2 = 'SECTION'

    def __init__(self, **kwargs):
        '''Constructor.
        '''
        super(SymmetricalConduitUnit, self).__init__(**kwargs)

    def _setup_headdata(self):
        self._unit_type = SymmetricalConduitUnit.UNIT_TYPE
        self._unit_category = SymmetricalConduitUnit.UNIT_CATEGORY
        self.head_data = {
            'comment': HeadDataItem('', '', 0, 0, dtype=dt.STRING),
            'distance': HeadDataItem(0.000, '{:>10}', 3, 0, dtype=dt.FLOAT, dps=3),
        }

    def _readHeadData(self, unit_data, file_line):
        """Format the header data for writing to file.

        Args:
            unit_data (list): containing the data to read.
        """
        self.head_data['comment'].value = unit_data[file_line + 0][8:].strip()
        self._name = unit_data[file_line + 2][:12].strip()
        self._name_ds = unit_data[file_line + 2][12:24].strip()
        self.head_data['distance'].value = unit_data[file_line + 3][:10].strip()
        return file_line + 4

    def _getHeadData(self):
        """Get the header data formatted for printing out to file.

        Returns:
            List of strings - The formatted header list.
        """
        out = []
        out.append('CONDUIT ' + self.head_data['comment'].value)
        out.append('SECTION')
        out.append('{:<12}'.format(self._name) + '{:<12}'.format(self._name_ds))
        out.append('{:<10}'.format(self.head_data['distance'].format()))
        return out


class AsymmetricalConduitUnit(RowDataConduitType):

    # Class constants
    UNIT_TYPE = 'conduit_asymmetrical'
    UNIT_CATEGORY = 'conduit'
    FILE_KEY = 'CONDUIT'
    FILE_KEY2 = 'ASYMMETRIC'
    
    def __init__(self, **kwargs):
        '''Constructor.
        '''
        super(AsymmetricalConduitUnit, self).__init__(**kwargs)

    def _setup_headdata(self):
        self._unit_type = AsymmetricalConduitUnit.UNIT_TYPE
        self._unit_category = AsymmetricalConduitUnit.UNIT_CATEGORY
        self.head_data = {
            'comment': HeadDataItem('', '', 0, 0, dtype=dt.STRING),
            'distance': HeadDataItem(0.000, '{:>10}', 3, 0, dtype=dt.FLOAT, dps=3),
            'roughness_type': HeadDataItem('DARCY', '', 4, 0, dtype=dt.CONSTANT, choices=('MANNING', 'DARCY')),
        }

    def _readHeadData(self, unit_data, file_line):
        """Format the header data for writing to file.

        Args:
            unit_data (list): containing the data to read.
        """
        self.head_data['comment'].value = unit_data[file_line + 0][8:].strip()
        self._name = unit_data[file_line + 2][:12].strip()
        self._name_ds = unit_data[file_line + 2][12:24].strip()
        self.head_data['distance'].value = unit_data[file_line + 3][:10].strip()
        self.head_data['roughness_type'].value = unit_data[file_line + 3][10:20].strip()
        return file_line + 4

    def _getHeadData(self):
        """Get the header data formatted for printing out to file.

        Returns:
            List of strings - The formatted header list.
        """
        out = []
        out.append('CONDUIT ' + self.head_data['comment'].value)
        out.append('ASYMMETRIC')
        out.append('{:<12}'.format(self._name) + '{:<12}'.format(self._name_ds))
        out.append(
            '{:<10}'.format(self.head_data['distance'].format()) +
            '{:>10}'.format(self.head_data['roughness_type'].format())
        )
        return out
    
