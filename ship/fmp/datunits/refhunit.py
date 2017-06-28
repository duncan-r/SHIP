"""

 Summary:
    Contains the Refh class.
    This holds all of the data read in from the refh units in the dat file.
    Can be called to load in the data and read and update the contents
    held in the object.

 Author:
     Duncan Runnacles

  Created:
     01 Apr 2016

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
from ship.datastructures.rowdatacollection import RowDataCollection
from ship.datastructures import dataobject as do
from ship.datastructures import DATA_TYPES as dt
from ship.fmp.headdata import HeadDataItem
from ship.fmp.datunits import ROW_DATA_TYPES as rdt


class RefhUnit(AUnit):
    """Concrete implementation of AUnit storing Isis River Unit
    data.

    Contains a reference to a rowdatacollection for storing and
    accessing all the row data. i.e. the geometry data for the section,
    containing the chainage, elevation, roughness, etc values.

    Methods for accessing the data in these objects and adding removing rows
    are available.

    See Also:
        AUnit
    """

    UNIT_TYPE = 'refh'
    UNIT_CATEGORY = 'inflows'
    FILE_KEY = 'REFHBDY'
    FILE_KEY2 = None

    def __init__(self, **kwargs):
        """Constructor.
        """
        super(RefhUnit, self).__init__(**kwargs)

        self._unit_type = RefhUnit.UNIT_TYPE
        self._unit_category = RefhUnit.UNIT_CATEGORY
        if self._name == 'unknown':
            self._name = 'Refh_unit'

        # Fill in the header values these contain the data at the top of the
        # section, such as the unit name and labels.
        self.head_data = {
            'revision': HeadDataItem(1, '{:<1}', 0, 0, dtype=dt.INT),
            'comment': HeadDataItem('', '', 0, 1, dtype=dt.STRING),
            'z': HeadDataItem(0.000, '{:>10}', 2, 0, dtype=dt.FLOAT, dps=3),
            'easting': HeadDataItem('', '{:>10}', 2, 1, dtype=dt.STRING),
            'northing': HeadDataItem('', '{:>10}', 2, 2, dtype=dt.STRING),
            'time_delay': HeadDataItem(0.000, '{:>10}', 3, 0, dtype=dt.FLOAT, dps=3),
            'time_step': HeadDataItem(1.0, '{:>10}', 3, 1, dtype=dt.FLOAT, dps=1),
            'bf_only': HeadDataItem('', '{:>10}', 3, 2, dtype=dt.STRING),
            'sc_flag': HeadDataItem('SCALEFACT', '{:<10}', 3, 3, dtype=dt.CONSTANT, choices=('SCALEFACT', 'PEAKVALUE')),
            'scale_factor': HeadDataItem(1.000, '{:>10}', 3, 4, dtype=dt.FLOAT, dps=3),
            'hydrograph_mode': HeadDataItem('HYDROGRAPH', '{:>10}', 3, 5, dtype=dt.CONSTANT, choices=('HYDROGRAPH', 'HYETOGRAPH')),
            'hydrograph_scaling': HeadDataItem('RUNOFF', '{:>10}', 3, 6, dtype=dt.CONSTANT, choices=('RUNOFF', 'FULL')),
            'min_flow': HeadDataItem(1.000, '{:>10}', 3, 7, dtype=dt.FLOAT, dps=3),
            'catchment_area': HeadDataItem(0.00, '{:>10}', 4, 0, dtype=dt.FLOAT, dps=2),
            'saar': HeadDataItem(0, '{:>10}', 4, 1, dtype=dt.INT),
            'urbext': HeadDataItem(0.000, '{:>10}', 4, 2, dtype=dt.FLOAT, dps=3),
            'season': HeadDataItem('DEFAULT', '{:>10}', 4, 3, dtype=dt.CONSTANT, choices=('DEFAULT', 'WINTER', 'SUMMER')),
            'published_report': HeadDataItem('DLL', '{:>10}', 4, 4, dtype=dt.CONSTANT, choices=('DLL', 'REPORT')),

            # Urban - only used if 'urban' == 'URBANREFH'
            'urban': HeadDataItem('', '{:>10}', 4, 5, dtype=dt.CONSTANT, choices=('', 'URBANREFH')),
            'subarea_1': HeadDataItem(0.00, '{:>10}', 5, 0, dtype=dt.FLOAT, dps=2),
            'dplbar_1': HeadDataItem(0.000, '{:>10}', 5, 1, dtype=dt.FLOAT, dps=3),
            'suburbext_1': HeadDataItem(0.000, '{:>10}', 5, 2, dtype=dt.FLOAT, dps=3),
            'calibration_1': HeadDataItem(0.000, '{:>10}', 5, 3, dtype=dt.FLOAT, dps=3),
            'subarea_2': HeadDataItem(0.00, '{:>10}', 6, 0, dtype=dt.FLOAT, dps=2),
            'dplbar_2': HeadDataItem(0.000, '{:>10}', 6, 1, dtype=dt.FLOAT, dps=3),
            'suburbext_2': HeadDataItem(0.000, '{:>10}', 6, 2, dtype=dt.FLOAT, dps=3),
            'calibration_2': HeadDataItem(0.000, '{:>10}', 6, 3, dtype=dt.FLOAT, dps=3),
            'subrunoff_2': HeadDataItem(0.000, '{:>10}', 6, 4, dtype=dt.FLOAT, dps=3),
            'sewer_rp_2': HeadDataItem('RUNOFF', '{:>10}', 6, 5, dtype=dt.CONSTANT, choices=('RUNOFF', 'DEPTH')),
            'sewer_depth_2': HeadDataItem(0.000, '{:>10}', 6, 6, dtype=dt.FLOAT, dps=3),
            'sewer_lossvolume_2': HeadDataItem('VOLUME', '{:>10}', 6, 7, dtype=dt.CONSTANT, choices=('VOLUME', 'FLOW')),
            'subarea_3': HeadDataItem(0.00, '{:>10}', 7, 0, dtype=dt.FLOAT, dps=2),
            'dplbar_3': HeadDataItem(0.000, '{:>10}', 7, 1, dtype=dt.FLOAT, dps=3),
            'suburbext_3': HeadDataItem(0.000, '{:>10}', 7, 2, dtype=dt.FLOAT, dps=3),
            'calibration_3': HeadDataItem(0.000, '{:>10}', 7, 3, dtype=dt.FLOAT, dps=3),
            'subrunoff_3': HeadDataItem(0.000, '{:>10}', 7, 4, dtype=dt.FLOAT, dps=3),

            'storm_area': HeadDataItem(0.00, '{:>10}', 8, 0, dtype=dt.FLOAT, dps=2),
            'storm_duration': HeadDataItem(0.000, '{:>10}', 8, 1, dtype=dt.FLOAT, dps=3),
            'sn_rate': HeadDataItem(0.000, '{:>10}', 8, 2, dtype=dt.FLOAT, dps=3),
            'rainfall_flag': HeadDataItem('DESIGN', '{:>10}', 9, 0, dtype=dt.CONSTANT, choices=('DESIGN', 'USER')),
            'arf_flag': HeadDataItem('DESIGN', '{:>10}', 9, 1, dtype=dt.CONSTANT, choices=('DESIGN', 'USER')),
            'rainfall_comment': HeadDataItem('', '', 9, 2, dtype=dt.STRING),
            'rainfall_odepth': HeadDataItem(0.000, '{:>10}', 10, 0, dtype=dt.FLOAT, dps=3),
            'return_period': HeadDataItem(0, '{:>10}', 10, 1, dtype=dt.INT),
            'arf': HeadDataItem(0.000, '{:>10}', 10, 2, dtype=dt.FLOAT, dps=3),
            'c': HeadDataItem(0.000, '{:>10}', 10, 3, dtype=dt.FLOAT, dps=3),
            'd1': HeadDataItem(0.000, '{:>10}', 10, 4, dtype=dt.FLOAT, dps=3),
            'd2': HeadDataItem(0.000, '{:>10}', 10, 5, dtype=dt.FLOAT, dps=3),
            'd2': HeadDataItem(0.000, '{:>10}', 10, 6, dtype=dt.FLOAT, dps=3),
            'd3': HeadDataItem(0.000, '{:>10}', 10, 7, dtype=dt.FLOAT, dps=3),
            'e': HeadDataItem(0.000, '{:>10}', 10, 8, dtype=dt.FLOAT, dps=3),
            'f': HeadDataItem(0.000, '{:>10}', 10, 9, dtype=dt.FLOAT, dps=3),
            'rp_flag': HeadDataItem('DESIGN', '{:>10}', 11, 0, dtype=dt.CONSTANT, choices=('DESIGN', 'USER')),
            'scf_flag': HeadDataItem('DESIGN', '{:>10}', 11, 1, dtype=dt.CONSTANT, choices=('DESIGN', 'USER')),
            'scf': HeadDataItem(0.000, '{:>10}', 11, 2, dtype=dt.FLOAT, dps=3),
            'use_refined_rainfall': HeadDataItem('0', '{:>10}', 11, 3, dtype=dt.CONSTANT, choices=('0', '1')),

            'cmax_flag': HeadDataItem('DESIGN', '{:>10}', 12, 0, dtype=dt.CONSTANT, choices=('DESIGN', 'USER')),
            'cini_flag': HeadDataItem('DESIGN', '{:>10}', 12, 1, dtype=dt.CONSTANT, choices=('DESIGN', 'USER')),
            'alpha_flag': HeadDataItem('DESIGN', '{:>10}', 12, 2, dtype=dt.CONSTANT, choices=('DESIGN', 'USER')),
            'models_comment': HeadDataItem('', '{}', 12, 3, dtype=dt.STRING),
            'cm_dcf': HeadDataItem(0.000, '{:>10}', 13, 0, dtype=dt.FLOAT, dps=3),
            'cmax': HeadDataItem(0.000, '{:>10}', 13, 1, dtype=dt.FLOAT, dps=3),
            'cini': HeadDataItem(0.000, '{:>10}', 13, 2, dtype=dt.FLOAT, dps=3),
            'alpha': HeadDataItem(0.000, '{:>10}', 13, 3, dtype=dt.FLOAT, dps=3),
            'bfihost': HeadDataItem(0.000, '{:>10}', 13, 4, dtype=dt.FLOAT, dps=3),
            'uh_flag': HeadDataItem('DESIGN', '{:>10}', 14, 0, dtype=dt.CONSTANT, choices=('DESIGN', 'USER')),
            'tp_flag': HeadDataItem('DESIGN', '{:>10}', 14, 1, dtype=dt.CONSTANT, choices=('DESIGN', 'USER')),
            'up_flag': HeadDataItem('DESIGN', '{:>10}', 14, 3, dtype=dt.CONSTANT, choices=('DESIGN', 'USER')),
            'uk_flag': HeadDataItem('DESIGN', '{:>10}', 14, 4, dtype=dt.CONSTANT, choices=('DESIGN', 'USER')),
            'tp_dcf': HeadDataItem(0.000, '{:>10}', 15, 0, dtype=dt.FLOAT, dps=3),
            'tp0': HeadDataItem(0.000, '{:>10}', 15, 1, dtype=dt.FLOAT, dps=3),
            'tpt': HeadDataItem(0.000, '{:>10}', 15, 2, dtype=dt.FLOAT, dps=3),
            'dplbar': HeadDataItem(0.000, '{:>10}', 15, 3, dtype=dt.FLOAT, dps=3),
            'dpsbar': HeadDataItem(0.000, '{:>10}', 15, 4, dtype=dt.FLOAT, dps=3),
            'propwet': HeadDataItem(0.000, '{:>10}', 15, 5, dtype=dt.FLOAT, dps=3),
            'up': HeadDataItem(0.000, '{:>10}', 15, 6, dtype=dt.FLOAT, dps=3),
            'uk': HeadDataItem(0.000, '{:>10}', 15, 7, dtype=dt.FLOAT, dps=3),
            'uh_rows': HeadDataItem(0.000, '{:>10}', 16, 0, dtype=dt.INT),
            #             'uh_units': HeadDataItem(0.000, '{:>10}', 14, 9, dtype=dt.INT),        # TODO: Find out what the deal with these is
            #             'uh_fct': HeadDataItem(0.000, '{:>10}', 14, 10, dtype=dt.FLOAT, dps=3),
            'bl_flag': HeadDataItem('DESIGN', '{:>10}', 17, 0, dtype=dt.CONSTANT, choices=('DESIGN', 'USER')),
            'br_flag': HeadDataItem('DESIGN', '{:>10}', 17, 1, dtype=dt.CONSTANT, choices=('DESIGN', 'USER')),
            'bf0_flag': HeadDataItem('DESIGN', '{:>10}', 17, 2, dtype=dt.CONSTANT, choices=('DESIGN', 'USER')),
            'bl_dcf': HeadDataItem(0.000, '{:>10}', 18, 0, dtype=dt.FLOAT, dps=3),
            'bl': HeadDataItem(0.000, '{:>10}', 18, 1, dtype=dt.FLOAT, dps=3),
            'br_dcf': HeadDataItem(0.000, '{:>10}', 18, 2, dtype=dt.FLOAT, dps=3),
            'br': HeadDataItem(0.000, '{:>10}', 18, 3, dtype=dt.FLOAT, dps=3),
            'bf0': HeadDataItem(0.000, '{:>10}', 18, 4, dtype=dt.FLOAT, dps=3),
        }

        dobjs = [
            # update_callback is called every time a value is added or updated
            do.FloatData(rdt.RAIN, format_str='{:>10}', default=0, no_of_dps=3)
        ]
        dummy_row = {rdt.RAIN: 0}
        self.row_data['main'] = RowDataCollection.bulkInitCollection(dobjs)
        self.row_data['main'].setDummyRow({rdt.RAIN: 0})

    def icLabels(self):
        """Overriddes superclass method."""
        return [self._name]

    def linkLabels(self):
        """Overriddes superclass method."""
        return {'name': self.name}

    def useUrban(self, activate):
        """
        Args:
            turn_on(bool): if True urban refh will be turned on if false it
                will be turned off.
        """
        if activate:
            self.head_data['urban'].value = 'URBANREFH'
            self.head_data['revision'].value = '2'
            self.has_urban = True
        else:
            self.head_data['urban'].value = ''
            self.head_data['revision'].value = '1'
            self.has_urban = False

    def readUnitData(self, unit_data, file_line):
        """Reads the unit data into the geometry objects.

        See Also:
            AUnit - readUnitData for more information.

        Args:
            unit_data (list): The section of the isis dat file pertaining
                to this section
        """
        file_line, storm_rows = self._readHeadData(unit_data, file_line)
        file_line = self._readStormData(unit_data, file_line, storm_rows)
        file_line = self._readSuffix(unit_data, file_line)
        return file_line

    def _readHeadData(self, unit_data, file_line):
        """Format the header data for writing to file.

        Args:
            unit_data (list): containing the data to read.
        """
        self.has_urban = False

        self.head_data['revision'].value = unit_data[file_line][18:19]
        self.head_data['comment'].value = unit_data[file_line][20:].strip()

        self._name = self.head_data['section_label'] = unit_data[file_line + 1][:12].strip()

        self.head_data['z'].value = unit_data[file_line + 2][:10].strip()
        self.head_data['easting'].value = unit_data[file_line + 2][10:20].strip()
        self.head_data['northing'].value = unit_data[file_line + 2][20:30].strip()
        self.head_data['time_delay'].value = unit_data[file_line + 3][0:10].strip()
        self.head_data['time_step'].value = unit_data[file_line + 3][10:20].strip()
        self.head_data['bf_only'].value = unit_data[file_line + 3][20:30].strip()
        self.head_data['sc_flag'].value = unit_data[file_line + 3][30:40].strip()
        self.head_data['scale_factor'].value = unit_data[file_line + 3][40:50].strip()
        self.head_data['hydrograph_mode'].value = unit_data[file_line + 3][50:60].strip()
        self.head_data['hydrograph_scaling'].value = unit_data[file_line + 3][60:70].strip()
        self.head_data['min_flow'].value = unit_data[file_line + 3][70:80].strip()
        self.head_data['catchment_area'].value = unit_data[file_line + 4][0:10].strip()
        self.head_data['saar'].value = unit_data[file_line + 4][10:20].strip()
        self.head_data['urbext'].value = unit_data[file_line + 4][20:30].strip()
        self.head_data['season'].value = unit_data[file_line + 4][30:40].strip()
        self.head_data['published_report'].value = unit_data[file_line + 4][40:50].strip()
        self.head_data['urban'].value = unit_data[file_line + 4][50:60].strip()

        if self.head_data['urban'].compare('URBANREFH'):
            self.has_urban = True

            self.head_data['subarea_1'].value = unit_data[file_line + 5][0:10].strip()
            self.head_data['dplbar_1'].value = unit_data[file_line + 5][10:20].strip()
            self.head_data['suburbext_1'].value = unit_data[file_line + 5][20:30].strip()
            self.head_data['calibration_1'].value = unit_data[file_line + 5][30:40].strip()
            self.head_data['subarea_2'].value = unit_data[file_line + 6][0:10].strip()
            self.head_data['dplbar_2'].value = unit_data[file_line + 6][10:20].strip()
            self.head_data['suburbext_2'].value = unit_data[file_line + 6][20:30].strip()
            self.head_data['calibration_2'].value = unit_data[file_line + 6][30:40].strip()
            self.head_data['subrunoff_2'].value = unit_data[file_line + 6][40:50].strip()
            self.head_data['sewer_rp_2'].value = unit_data[file_line + 6][50:60].strip()
            self.head_data['sewer_depth_2'].value = unit_data[file_line + 6][60:70].strip()
            self.head_data['sewer_lossvolume_2'].value = unit_data[file_line + 6][70:80].strip()
            self.head_data['subarea_3'].value = unit_data[file_line + 7][0:10].strip()
            self.head_data['dplbar_3'].value = unit_data[file_line + 7][10:20].strip()
            self.head_data['suburbext_3'].value = unit_data[file_line + 7][20:30].strip()
            self.head_data['calibration_3'].value = unit_data[file_line + 7][30:40].strip()
            self.head_data['subrunoff_3'].value = unit_data[file_line + 7][40:50].strip()

        file_line += 5
        if self.has_urban:
            file_line += 3

        self.head_data['storm_area'].value = unit_data[file_line][0:10].strip()
        self.head_data['storm_duration'].value = unit_data[file_line][10:20].strip()
        self.head_data['sn_rate'].value = unit_data[file_line][20:30].strip()
        self.head_data['rainfall_flag'].value = unit_data[file_line + 1][0:10].strip()
        self.head_data['arf_flag'].value = unit_data[file_line + 1][10:20].strip()
        self.head_data['rainfall_comment'].value = unit_data[file_line + 1][20:].strip()
        self.head_data['rainfall_odepth'].value = unit_data[file_line + 2][0:10].strip()
        self.head_data['return_period'].value = unit_data[file_line + 2][10:20].strip()
        self.head_data['arf'].value = unit_data[file_line + 2][20:30].strip()
        self.head_data['c'].value = unit_data[file_line + 2][30:40].strip()
        self.head_data['d1'].value = unit_data[file_line + 2][40:50].strip()
        self.head_data['d2'].value = unit_data[file_line + 2][50:60].strip()
        self.head_data['d3'].value = unit_data[file_line + 2][60:70].strip()
        self.head_data['e'].value = unit_data[file_line + 2][70:80].strip()
        self.head_data['f'].value = unit_data[file_line + 2][80:90].strip()
        self.head_data['rp_flag'].value = unit_data[file_line + 3][0:10].strip()
        self.head_data['scf_flag'].value = unit_data[file_line + 3][10:20].strip()
        self.head_data['scf'].value = unit_data[file_line + 3][20:30].strip()
        self.head_data['use_refined_rainfall'].value = unit_data[file_line + 3][30:40].strip()
        temp = unit_data[file_line + 4]
        storm_rows = int(unit_data[file_line + 4][0:10].strip())

        file_line = file_line + 5
        return file_line, storm_rows

    def _readStormData(self, unit_data, file_line, storm_rows):
        """
        """
        out_line = file_line + storm_rows
        for i in range(file_line, out_line):
            self.row_data['main'].addRow(
                {rdt.RAIN: unit_data[i][0:10].strip()}, no_copy=True
            )

        return out_line

    def _readSuffix(self, unit_data, file_line):
        """
        """
        self.head_data['cmax_flag'].value = unit_data[file_line][0:10].strip()
        self.head_data['cini_flag'].value = unit_data[file_line][10:20].strip()
        self.head_data['alpha_flag'].value = unit_data[file_line][20:30].strip()
        self.head_data['models_comment'].value = unit_data[file_line][30:].strip()
        self.head_data['cm_dcf'].value = unit_data[file_line + 1][0:10].strip()
        self.head_data['cmax'].value = unit_data[file_line + 1][10:20].strip()
        self.head_data['cini'].value = unit_data[file_line + 1][20:30].strip()
        self.head_data['alpha'].value = unit_data[file_line + 1][30:40].strip()
        self.head_data['bfihost'].value = unit_data[file_line + 1][40:50].strip()
        self.head_data['uh_flag'].value = unit_data[file_line + 2][0:10].strip()
        self.head_data['tp_flag'].value = unit_data[file_line + 2][10:20].strip()
        self.head_data['up_flag'].value = unit_data[file_line + 2][20:30].strip()
        self.head_data['uk_flag'].value = unit_data[file_line + 2][30:40].strip()
        self.head_data['tp_dcf'].value = unit_data[file_line + 3][0:10].strip()
        self.head_data['tp0'].value = unit_data[file_line + 3][10:20].strip()
        self.head_data['tpt'].value = unit_data[file_line + 3][20:30].strip()
        self.head_data['dplbar'].value = unit_data[file_line + 3][30:40].strip()
        self.head_data['dpsbar'].value = unit_data[file_line + 3][40:50].strip()
        self.head_data['propwet'].value = unit_data[file_line + 3][50:60].strip()
        self.head_data['up'].value = unit_data[file_line + 3][60:70].strip()
        self.head_data['uk'].value = unit_data[file_line + 3][70:80].strip()
        self.head_data['uh_rows'].value = unit_data[file_line + 4][0:10].strip()
        self.head_data['bl_flag'].value = unit_data[file_line + 5][0:10].strip()
        self.head_data['br_flag'].value = unit_data[file_line + 5][10:20].strip()
        self.head_data['bf0_flag'].value = unit_data[file_line + 5][20:30].strip()
        self.head_data['bl_dcf'].value = unit_data[file_line + 6][0:10].strip()
        self.head_data['bl'].value = unit_data[file_line + 6][10:20].strip()
        self.head_data['br_dcf'].value = unit_data[file_line + 6][20:30].strip()
        self.head_data['br'].value = unit_data[file_line + 6][30:40].strip()
        self.head_data['bf0'].value = unit_data[file_line + 6][40:50].strip()

        return file_line + 6

    def getData(self):
        """Retrieve the data in this unit.

        The String[] returned is formatted for printing in the fashion
        of the .dat file.

        Return:
            List of strings formated for writing to .dat file.
        """
        out_data = self._getHeadData()
        out_data.extend(self._getStormData())
        out_data.extend(self._getSuffix())

        return out_data

    def _getHeadData(self):
        """
        """
        out = []
        out.append('REFHBDY #revision#' + self.head_data['revision'].format() + ' ' + self.head_data['comment'].value)
        out.append('\n' + self._name)

        key_order = ['z', 'easting', 'northing', 'time_delay', 'time_step',
                     'bf_only', 'sc_flag', 'scale_factor', 'hydrograph_mode',
                     'hydrograph_scaling', 'min_flow', 'catchment_area', 'saar',
                     'urbext', 'season', 'published_report', 'urban']
        for k in key_order:
            out.append(self.head_data[k].format(True))

        if self.head_data['urban'].compare('URBANREFH'):
            key_order = ['subarea_1', 'dplbar_1', 'suburbext_1', 'calibration_1',
                         'subarea_2', 'dplbar_2', 'suburbext_2', 'calibration_2',
                         'subrunoff_2', 'sewer_rp_2', 'sewer_depth_2',
                         'sewer_lossvolume_2', 'subarea_3', 'dplbar_3',
                         'suburbext_3', 'calibration_3', 'subrunoff_3']
            for k in key_order:
                out.append(self.head_data[k].format(True))

        key_order = ['storm_area', 'storm_duration', 'sn_rate', 'rainfall_flag',
                     'arf_flag', 'rainfall_comment', 'rainfall_odepth', 'return_period', 'arf',
                     'c', 'd1', 'd2', 'd3', 'e', 'f', 'rp_flag', 'scf_flag', 'scf',
                     'use_refined_rainfall']
        for k in key_order:
            out.append(self.head_data[k].format(True))
        j = ''.join(out)
        finalout = ''.join(out).split('\n')

        return finalout

    def _getStormData(self):
        """
        """
        out_data = []
        out_data = ['{:>10}'.format(self.row_data['main'].numberOfRows())]
        for i in range(self.row_data['main'].numberOfRows()):
            out_data.append(self.row_data['main'].getPrintableRow(i))
        return out_data
#         out_data = ['{:>10}'.format(self.row_data['main'].numberOfRows())]
#         for line in self.row_data['main']:
#             out_data.append('{:>10}'.format(line))

        return out_data

    def _getSuffix(self):
        """
        """
        out = []
        # Add this heere to avoid an additional newline
        out.append(self.head_data['cmax_flag'].format())
        key_order = [
            'cini_flag', 'alpha_flag', 'models_comment', 'cm_dcf',
            'cmax', 'cini', 'alpha', 'bfihost', 'uh_flag', 'tp_flag', 'up_flag',
            'uk_flag', 'tp_dcf', 'tp0', 'tpt', 'dplbar', 'dpsbar', 'propwet',
            'up', 'uk', 'uh_rows', 'bl_flag', 'br_flag', 'bf0_flag', 'bl_dcf',
            'bl', 'br_dcf', 'br', 'bf0'
        ]
        for k in key_order:
            out.append(self.head_data[k].format(True))
        out = ''.join(out).split('\n')

        return out
