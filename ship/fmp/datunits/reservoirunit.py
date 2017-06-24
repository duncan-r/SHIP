"""

 Summary:
    Contains the ReservoirUnit class.
    This holds all of the data read in from the reservoir units in the dat file.
    Can be called to load in the data and read and update the contents 
    held in the object.

 Author:  
     Duncan R.

  Created:  
     18 May 2017

 Copyright:  
     Duncan Runnacles 2017

 TODO:

 Updates:

"""
from __future__ import unicode_literals

from ship.fmp.datunits.isisunit import AUnit
from ship.fmp.datunits import ROW_DATA_TYPES as rdt
from ship.datastructures import dataobject as do
from ship.datastructures.rowdatacollection import RowDataCollection
from ship.fmp.headdata import HeadDataItem
from ship.datastructures import DATA_TYPES as dt

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class ReservoirUnit (AUnit):
    """Concrete implementation of AUnit storing Isis Reservoir Unit data.

    Contains a reference to a rowdatacollection for storing and
    accessing all the row data. i.e. the geometry data for the reservoir.
    Methods for accessing the data in these objects and adding removing rows
    are available.

    See Also:
        AUnit
    """
    UNIT_TYPE = 'reservoir'
    UNIT_CATEGORY = 'reservoir'
    FILE_KEY = 'RESERVOIR'
    FILE_KEY2 = None

    def __init__(self, **kwargs):
        """Constructor.

        Args:
            fileOrder (int): The location of this unit in the file.
        """
        AUnit.__init__(self, **kwargs)

        self._name = 'Res'
        self.head_data = {
            'revision': HeadDataItem(0, '{:<1}', 0, 0, dtype=dt.INT, allow_blank=True),
            'comment': HeadDataItem('', '', 0, 1, dtype=dt.STRING),
            'easting': HeadDataItem(0.000, '{:>10}', 1, 0, dtype=dt.FLOAT, dps=3),
            'northing': HeadDataItem(0.000, '{:>10}', 1, 1, dtype=dt.FLOAT, dps=3),
            'runoff_factor': HeadDataItem(0.000, '{:>10}', 1, 2, dtype=dt.FLOAT, dps=3),
            'lateral1': HeadDataItem('', '{:<12}', 2, 0, dtype=dt.STRING),
            'lateral2': HeadDataItem('', '{:<12}', 2, 1, dtype=dt.STRING),
            'lateral3': HeadDataItem('', '{:<12}', 2, 2, dtype=dt.STRING),
            'lateral4': HeadDataItem('', '{:<12}', 2, 3, dtype=dt.STRING),
            'names': []
        }

        self._unit_type = ReservoirUnit.UNIT_TYPE
        self._unit_category = ReservoirUnit.UNIT_CATEGORY

        dobjs = [
            do.FloatData(
                rdt.ELEVATION, format_str='{:>10}', no_of_dps=3, use_sn=1000000,
                update_callback=self.checkIncreases
            ),
            do.FloatData(
                rdt.AREA, format_str='{:>10}', no_of_dps=3, use_sn=1000000,
                update_callback=self.checkIncreases
            ),
        ]
        self.row_data['main'] = RowDataCollection.bulkInitCollection(dobjs)
        self.row_data['main'].setDummyRow({rdt.ELEVATION: 0, rdt.AREA: 0})

    def icLabels(self):
        labels = [self._name] + self.head_data['names']
        for i in range(1, 4):
            latname = 'lateral' + str(i)
            if self.head_data[latname].value != '':
                labels.append(self.head_data[latname].value)
        return labels

    def linkLabels(self):
        names = {}
        for i, n in enumerate([self._name] + self.head_data['names']):
            names['name' + str(i)] = n
        laterals = {
            'lateral1': self.head_data['lateral1'].value,
            'lateral2': self.head_data['lateral2'].value,
            'lateral3': self.head_data['lateral3'].value,
            'lateral4': self.head_data['lateral4'].value
        }
        names.update(laterals)
        return names

    def readUnitData(self, unit_data, file_line):
        """Reads the unit data into the geometry objects.

        Args:
            unit_data (list): The part of the isis dat file pertaining to 
                this section 

        See Also:
            AUnit - readUnitData()
        """
        file_line = self._readHeadData(unit_data, file_line)
        file_line = self._readRowData(unit_data, file_line)
        if self.head_data['revision'].value > 0:
            file_line = self._readPostRowData(unit_data, file_line)
        return file_line - 1

    def _readHeadData(self, unit_data, file_line):
        """Reads the data in the file header section into the class.

        Args:
            unit_data (list): contains data for this unit.
        """
        if '#revision#' in unit_data[file_line]:
            self.head_data['revision'].value = unit_data[file_line][20:21]
            self.head_data['comment'].value = unit_data[file_line][23:].strip()
        else:
            self.head_data['comment'].value = unit_data[file_line][11:]

        line = unit_data[file_line + 1]
        names = [line[i:i + 12].strip() for i in range(0, len(line), 12)]
        self._name = names[0]
        self.head_data['names'] = names[1:]  # Remove the main name from the list

        line_count = 2
        if self.head_data['revision'].value > 0:
            line_count += 1
            line = unit_data[file_line + 2]
            names = [line[i:i + 12].strip() for i in range(0, len(line), 12)]
            for i, n in enumerate(names):
                if i > 3:
                    break
                self.head_data['lateral' + str(i + 1)].value = n.strip()

        return file_line + line_count

    def _readPostRowData(self, unit_data, file_line):
        self.head_data['easting'].value = unit_data[file_line][:10].strip()
        self.head_data['northing'].value = unit_data[file_line][10:20].strip()
        self.head_data['runoff_factor'].value = unit_data[file_line][20:].strip()
        return file_line + 1

    def _readRowData(self, unit_data, file_line):
        """Reads the units rows into the row collection.

        This is all the geometry data that occurs after the no of rows variable in
        the Spill Units of the dat file.

        Args:
            unit_data: the data pertaining to this unit.
        """
        self.unit_length = int(unit_data[file_line].strip())
        file_line += 1
        out_line = file_line + self.unit_length
        try:
            # Load the geometry data
            for i in range(file_line, out_line):
                elev = unit_data[i][0:10].strip()
                area = unit_data[i][10:20].strip()

                self.row_data['main'].addRow({
                    rdt.ELEVATION: elev, rdt.AREA: area,
                }, no_copy=True)

        except NotImplementedError:
            logger.ERROR('Unable to read Unit Data(dataRowObject creation) - NotImplementedError')
            raise

        return out_line

    def getData(self):
        """Retrieve the data in this unit.

        The String[] returned is formatted for printing in the fashion
        of the .dat file.

        The _getPostRowData function is only returned for units that have
        a revision number > 0.

        Returns:
            list of output data formated the same as in the .DAT file.
        """
        num_rows = self.row_data['main'].numberOfRows()
        out_data = self._getHeadData(num_rows)
        out_data.extend(self._getRowData(num_rows))
        if self.head_data['revision'].value > 0:
            out_data.extend(self._getPostRowData())
        return out_data

    def _getRowData(self, num_rows):
        """Get the data in the row collection.

        For all the rows in the spill geometry section get the data from
        the rowdatacollection class.

        Returns:
            list containing the formatted unit rows.
        """
        out_data = []
        out_data.append('{:>10}'.format(num_rows))
        for i in range(0, num_rows):
            out_data.append(self.row_data['main'].getPrintableRow(i))
        return out_data

    def _getHeadData(self, num_rows):
        """Get the header data formatted for printing out.

        Returns:
            list - contining the formatted head data.
        """
        out = []
        if self.head_data['revision'].value > 0:
            out.append('RESERVOIR ' + '#revision#' + str(self.head_data['revision'].value) +
                       ' ' + self.head_data['comment'].value)
        else:
            out.append('RESERVOIR ' + self.head_data['comment'].value)
        names = []
        for n in ([self._name] + self.head_data['names']):
            names.append('{:<12}'.format(n))
        out.append(''.join(names))
        lats = []
        if self.head_data['revision'].value > 0:
            lats.append(self.head_data['lateral1'].format())
            lats.append(self.head_data['lateral2'].format())
            lats.append(self.head_data['lateral3'].format())
            lats.append(self.head_data['lateral4'].format())
            out.append(''.join(lats))
        return out

    def _getPostRowData(self):
        out = []
        if self.head_data['revision'].value > 0:
            out.append(self.head_data['easting'].format())
            out.append(self.head_data['northing'].format())
            out.append(self.head_data['runoff_factor'].format())
            out = ''.join(out)
            return [out]
        else:
            return out

    def addRow(self, row_vals, rowdata_key='main', index=None, **kwargs):
        """Adds a new row to the spill unit.

        Ensures that certain requirements of the data rows, such as the 
        elevation and area needing to increase for each row down are met, then 
        call the addNewRow() method in the row_collection.

        Args:
            row_vals(Dict): keys must be datunits.ROW_DATA_TYPES with a legal
                value assigned for the DataType. Chainage and Elevation MUST
                be included.
            index=None(int): the row to insert into. The existing row at the
                given index will be moved up by one.

        Returns:
            False if the addNewRow() method is unsuccessful.

        Raises:
            IndexError: If the index does not exist.
            ValueError: If the given value is not accepted by the DataObjects. 

        See Also:
            ADataObject and subclasses for information on the parameters.
        """
        keys = row_vals.keys()
        if not rdt.ELEVATION in keys or not rdt.AREA in keys:
            raise AttributeError('row_vals must include CHAINAGE and ELEVATION.')

        # Call superclass method to add the new row
        AUnit.addRow(self, row_vals, index=index, **kwargs)

    def convertToLatestVersion(self):
        """Convert old style reservoir units to the new format.

        We don't really need to do anything here. All of the defaults are
        set in the constructor, so it's just the revision value that needs
        updating.
        """
        if self.head_data['revision'].value > 0:
            return

        self.head_data['revision'].value = 1
