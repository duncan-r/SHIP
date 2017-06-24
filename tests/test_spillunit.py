from __future__ import unicode_literals

import unittest

from ship.fmp.datunits import spillunit
from ship.fmp.datunits import ROW_DATA_TYPES as rdt
from ship.fmp.fmpunitfactory import FmpUnitFactory


class test_SpillUnit(unittest.TestCase):
    """
    """

    def setUp(self):
        """
        """
        self.spill_unitdata = ['SPILL A spill comment',
                               '1.056_SU    1.056_SD',
                               '     1.200     0.900',
                               '         3',
                               '     0.000    37.651      0.00      0.00',
                               '     5.000    38.000      0.00      0.00',
                               '     6.550    37.900      0.00      0.00']

        self.chainage = [0.000, 5.000, 6.550]
        self.elevation = [37.651, 38.000, 37.900]
        self.easting = [0.00, 0.00, 0.00]
        self.northing = [0.00, 0.00, 0.00]

    def test_readHeadData(self):
        """Check the head data is read in properly."""
        # create a unloaded river unit to just check the readHeadData() method.
        s = spillunit.SpillUnit()
        # Put the test data into the method
        s._readHeadData(self.spill_unitdata, 0)

        self.assertEqual(s.unit_type, 'spill')
        self.assertEqual(s.unit_category, 'spill')

        self.assertEqual(s._name, '1.056_SU')
        self.assertEqual(s._name_ds, '1.056_SD')
        self.assertEqual(s.head_data['comment'].value, 'A spill comment')
        self.assertEqual(s.head_data['weir_coef'].value, 1.200)
        self.assertEqual(s.head_data['modular_limit'].value, 0.900)

    def test_readSpillUnit(self):
        """Check that it's reading the spill unit in properly"""

        # create a unloaded river unit to just check the readHeadData() method.
        s = spillunit.SpillUnit()
        # Put the test data into the readrowData() method
        s.readUnitData(self.spill_unitdata, 0)

        self.assertEqual(s.row_data['main'].row_count, 3)

        self.assertListEqual(s.row_data['main'].dataObjectAsList(rdt.CHAINAGE), self.chainage)
        self.assertListEqual(s.row_data['main'].dataObjectAsList(rdt.ELEVATION), self.elevation)
        self.assertListEqual(s.row_data['main'].dataObjectAsList(rdt.EASTING), self.easting)
        self.assertListEqual(s.row_data['main'].dataObjectAsList(rdt.NORTHING), self.northing)

    def test_addDataRow(self):
        """Test adding a new row to 'main' data."""
        # Create a factory and load the river unit
        ifactory = FmpUnitFactory()
        i, spill = ifactory.createUnitFromFile(self.spill_unitdata, 0, 'SPILL', 1, 1)

        # Add with required only args
        args = {rdt.CHAINAGE: 6.0, rdt.ELEVATION: 37.2}
        spill.addRow(args, index=1)
        row = spill.row_data['main'].rowAsList(1)
        testrow = [6.0, 37.2, 0.00, 0.00]
        self.assertListEqual(testrow, row)

        # Add with all args
        args = {rdt.CHAINAGE: 8.0, rdt.ELEVATION: 39.4,
                rdt.EASTING: 12.0, rdt.NORTHING: 40.0}
        spill.addRow(args)
        row = spill.row_data['main'].rowAsList(4)
        testrow = [8.0, 39.4, 12.0, 40.0]
        self.assertListEqual(testrow, row)

        # Check it fails without required args
        args = {rdt.CHAINAGE: 56.2}
        with self.assertRaises(AttributeError):
            spill.addRow(args)
        args = {rdt.ELEVATION: 36.2}
        with self.assertRaises(AttributeError):
            spill.addRow(args)

        # Check we catch non increasing chainage
        args = {rdt.CHAINAGE: 5.1, rdt.ELEVATION: 37.2}
        with self.assertRaises(ValueError):
            spill.addRow(args, index=1)
