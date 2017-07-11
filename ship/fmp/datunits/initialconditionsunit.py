"""

 Summary:
    Contains the InitialConditionsUnit class.
    This is a holder for all of the data in the initial conditions section
    of the dat file.

 Author:
     Duncan Runnacles

 Created:
     01 Apr 2016

 Copyright:
     Duncan Runnacles 2016

 TODO:
    Not fully implemented at the moment - see class TODO comment for details.

 Updates:

"""

from __future__ import unicode_literals

from ship.fmp.datunits.isisunit import AUnit
from ship.datastructures.rowdatacollection import RowDataCollection
from ship.datastructures import dataobject as do
from ship.fmp.datunits import ROW_DATA_TYPES as rdt

import logging
logger = logging.getLogger(__name__)


class InitialConditionsUnit (AUnit):
    """isisunit for storing the initial conditions.

    Stores the initial conditions data; near the end of the .dat file.
    """

    # Class constants
    UNIT_TYPE = 'initial_conditions'
    UNIT_CATEGORY = 'initial_conditions'
    FILE_KEY = 'INITIAL'
    FILE_KEY2 = None

    def __init__(self, **kwargs):
        """Constructor

        Args:
            node_count (int): The number of nodes in the model. We need this to
                know how many lines there are to read from the contents list.
            fileOrder (int): The location of the initial conditions in the
                .DAT file. This will always be at the end but before the
                GISINFO if there is any.
        """
        super(InitialConditionsUnit, self).__init__(**kwargs)
        self._unit_type = InitialConditionsUnit.UNIT_TYPE
        self._unit_category = InitialConditionsUnit.UNIT_CATEGORY
        self._name = "initial_conditions"
        self._name_types = {}
        self._node_count = 0
#         self.has_datarows = True
#         self.has_ics = False

        dobjs = [
            do.StringData(rdt.LABEL, format_str='{:<12}'),
            do.StringData(rdt.QMARK, format_str='{:>2}', default='y'),
            do.FloatData(rdt.FLOW, format_str='{:>10}', default=0.000, no_of_dps=3),
            do.FloatData(rdt.STAGE, format_str='{:>10}', default=0.000, no_of_dps=3),
            do.FloatData(rdt.FROUDE_NO, format_str='{:>10}', default=0.000, no_of_dps=3),
            do.FloatData(rdt.VELOCITY, format_str='{:>10}', default=0.000, no_of_dps=3),
            do.FloatData(rdt.UMODE, format_str='{:>10}', default=0.000, no_of_dps=3),
            do.FloatData(rdt.USTATE, format_str='{:>10}', default=0.000, no_of_dps=3),
            do.FloatData(rdt.ELEVATION, format_str='{:>10}', default=0.000, no_of_dps=3),
        ]
        self.row_data['main'] = RowDataCollection.bulkInitCollection(dobjs)

    @property
    def node_count(self):
        return self._node_count
#         return self.row_data['main'].getNumberOfRows()

    def readUnitData(self, unit_data, file_line, **kwargs):
        """
        """
        self._node_count = kwargs['node_count']
        self._name_types = kwargs['name_types']

        i = file_line
        out_line = file_line + self._node_count + 2
        for i in range(file_line, out_line):
            if i < file_line + 2:
                continue  # Skip the first couple of header lines

            label = unit_data[i][0:12].strip()
            qmark = unit_data[i][12:14].strip()
            flow = unit_data[i][14:24].strip()
            stage = unit_data[i][24:34].strip()
            froude_no = unit_data[i][34:44].strip()
            velocity = unit_data[i][44:54].strip()
            umode = unit_data[i][54:64].strip()
            ustate = unit_data[i][64:74].strip()
            elevation = unit_data[i][74:84].strip()

            self.row_data['main'].addRow({
                rdt.LABEL: label, rdt.QMARK: qmark, rdt.FLOW: flow,
                rdt.STAGE: stage, rdt.FROUDE_NO: froude_no, rdt.VELOCITY: velocity,
                rdt.UMODE: umode, rdt.USTATE: ustate,
                rdt.ELEVATION: elevation
            }, no_copy=True)

        return out_line - 1

    def getData(self):
        """
        """
        out_data = []
        out_data.append('INITIAL CONDITIONS')
        out_data.append(' label   ?      flow     stage froude no  velocity     umode    ustate         z')
#         for i in range(0, self._node_count):
        for i in range(0, self.row_data['main'].numberOfRows()):
            out_data.append(self.row_data['main'].getPrintableRow(i))

        return out_data


#     def updateDataRow(self, row_vals, index):
    def updateRow(self, row_vals, index, **kwargs):
        """Updates the row at the given index in the row_collection.

        Changes the state of the values in the initial conditions list of
        the .dat file at the given index.

        Args:
            row_vals(Dict): keys must be datunits.ROW_DATA_TYPES with a legal
                value assigned for the DataType. Chainage and Elevation MUST
                be included.
            index: the row to update.

        Raises:
            IndexError: If the index does not exist.
            ValueError: If the given value is not accepted by the DataObject's.

        See Also:
            ADataObject and subclasses for information on the parameters.
        """

        # Call superclass method to add the new row
        AUnit.updateRow(self, row_vals=row_vals, index=index, **kwargs)


#     def updateDataRowByName(self, row_vals, name):
    def updateRowByName(self, row_vals, name, **kwargs):
        """Updates the row for the entry with the give name.

        Changes the state of the values in the initial conditions list for the
        the .dat file for the unit with the given name.

        Args:
            row_vals(Dict): keys must be datunits.ROW_DATA_TYPES with a legal
                value assigned for the DataType. Chainage and Elevation MUST
                be included.
            name: the name of the unit who's ic's should be updated.

        Raises:
            IndexError: If the index does not exist.
            ValueError: If the given value is not accepted by the DataObject's.
            AttributeError: If the given name doesn't exists in the collection.

        See Also:
            ADataObject and subclasses for information on the parameters.
        """
        labels = self.row_data['main'].dataObjectAsList(rdt.LABEL)
        try:
            index = labels.index(name)
        except ValueError:
            raise KeyError('Name does not exist in initial conditions: ' + str(name))

        # Call superclass method to add the new row
        AUnit.updateRow(self, row_vals=row_vals, index=index, **kwargs)


#     def addDataRow(self, row_vals):
    def addRow(self, row_vals, unit_type, **kwargs):
        """Adds a new row to the InitialCondition units row_collection.

        The new row will be added at the given index. If no index is given it
        will be appended to the end of the collection.

        If no LABEL value is given a AttributeError will be raised as it
        cannot have a default value. All other values can be ommitted. If they
        are they will be given defaults.

        Examples:
            >>> import ship.fmp.datunits.ROW_DATA_TYPES as rdt
            >>> ics.addRow({rdt.LABEL:UNITNAME, rdt.STAGE:10.2}, index=4)

        Args:
            row_vals(Dict): keys must be datunits.ROW_DATA_TYPES with a legal
                value assigned for the DataType. Chainage and Elevation MUST
                be included.

        Raises:
            AttributeError: If LABEL is not given.
            IndexError: If the index does not exist.
            ValueError: If the given value is not accepted by the DataObject's.

        See Also:
            ADataObject and subclasses for information on the parameters.
        """
        if not rdt.LABEL in row_vals.keys():
            logger.error('Required values of LABEL not given')
            raise AttributeError("Required value 'LABEL' not given")

        # Keep a record of multiple unit types under the same name
        if row_vals[rdt.LABEL] in self._name_types.keys():
            if not unit_type in self._name_types[row_vals[rdt.LABEL]]:
                self._name_types[row_vals[rdt.LABEL]].append(unit_type)
        else:
            self._name_types[row_vals[rdt.LABEL]] = [unit_type]

        # Don't add the same ic's in twice
        labels = self.row_data['main'].dataObjectAsList(rdt.LABEL)
        if row_vals[rdt.LABEL] in labels:
            return self._node_count

        # Call superclass method to add the new row
        AUnit.addRow(self, row_vals=row_vals, index=None, **kwargs)
        self._node_count += 1
        return self._node_count

    def deleteRowByName(self, unit_name, unit_type, **kwargs):
        """Delete one of the RowDataCollection objects in the row_collection.

        This calls the AUnit deleteRow method, but obtains the index
        of the row to be deleted from the name first.

        Args:
            section_name(str): the name of the AUnit to be removed from
                the initial conditions.

        Raises:
            KeyError - if section_name does not exist.
        """
        labels = self.row_data['main'].dataObjectAsList(rdt.LABEL)
        try:
            index = labels.index(unit_name)
        except ValueError:
            raise KeyError('Name does not exist in initial conditions: ' + str(unit_name))

        # Delete the ic if the unit_name is the only one using it
        # Otherwise remove the type and keep the ic's as they are
        if not unit_name in self._name_types.keys():
            return
        elif len(self._name_types[unit_name]) > 1:
            self._name_types[unit_name].remove(unit_type)
        else:
            self.deleteRow(index, **kwargs)
            self._node_count -= 1
            del self._name_types[unit_name]

    def rowByName(self, section_name):
        """Get the data vals in a particular row by name.

        This is the same functionality as the AUnit's getRow(int) method
        which returns a row in the RowDataCollection by the index value given.
        In this case it will find the index based on the section label and
        return the same dictionary of row values.

        Args:
            section_name(str): the name of the AUnit to be removed from
                the initial conditions.

        Return:
            dict - containing the values for the requested row.
        """
        labels = self.row_data['main'].dataObjectAsList(rdt.LABEL)
        index = labels.index(section_name)

        if index == -1:
            raise AttributeError('Name does not exist in initial conditions: ' + str(section_name))

        return self.row(index)
