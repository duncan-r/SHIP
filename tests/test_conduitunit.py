import unittest

from ship.fmp.datunits import conduitunit
from ship.fmp.datunits import ROW_DATA_TYPES as rdt
from ship.fmp.fmpunitfactory import FmpUnitFactory


class test_RectangularConduit(unittest.TestCase):
    """RectangularConduitUnit.
    """

    def setUp(self):
        """
        """
        self.conduit_data = [
            'CONDUIT Rectangular conduit unit',
            'RECTANGULAR',
            'RECT_US     RECT_DS',
            '    10.000',
            'MANNING',
            '   100.300     1.500     1.000    GLOBAL     0.100     0.110    GLOBAL     0.200     0.210',
            '   0.03000   0.03500   0.04000',
        ]

    def test_readHeadData(self):
        """Test that the data is read in properly."""
        # create a unloaded river unit to just check the readHeadData() method.
        c = conduitunit.RectangularConduitUnit()
        # Put the test data into the method
        c.readUnitData(self.conduit_data, 0)

        self.assertEqual(c.unit_type, 'conduit_rectangular')
        self.assertEqual(c.unit_category, 'conduit')

        self.assertEqual(c._name, 'RECT_US')
        self.assertEqual(c._name_ds, 'RECT_DS')
        self.assertEqual(c.head_data['distance'].value, 10.0)
        self.assertEqual(c.head_data['roughness_type'].value, 'MANNING')
        self.assertEqual(c.head_data['invert'].value, 100.3)
        self.assertEqual(c.head_data['width'].value, 1.5)
        self.assertEqual(c.head_data['height'].value, 1.0)
        self.assertEqual(c.head_data['bottom_slot_status'].value, 'GLOBAL')
        self.assertEqual(c.head_data['bottom_slot_distance'].value, 0.1)
        self.assertEqual(c.head_data['bottom_slot_depth'].value, 0.11)
        self.assertEqual(c.head_data['top_slot_status'].value, 'GLOBAL')
        self.assertEqual(c.head_data['top_slot_distance'].value, 0.2)
        self.assertEqual(c.head_data['top_slot_depth'].value, 0.21)
        self.assertEqual(c.head_data['roughness_invert'].value, 0.03)
        self.assertEqual(c.head_data['roughness_walls'].value, 0.035)
        self.assertEqual(c.head_data['roughness_soffit'].value, 0.04)

    def test_getData(self):
        """Check that the correctly formatted text is being returned."""
        test_out = [
            'CONDUIT Rectangular conduit unit',
            'RECTANGULAR',
            'RECT_US     RECT_DS     ',
            '    10.000',
            'MANNING',
            '   100.300     1.500     1.000    GLOBAL     0.100     0.110    GLOBAL     0.200     0.210',
            '   0.03000   0.03500   0.04000',
        ]
        # create a unloaded river unit to just check the readHeadData() method.
        c = conduitunit.RectangularConduitUnit()
        # Put the test data into the method
        c.readUnitData(self.conduit_data, 0)
        out = c.getData()
        self.assertListEqual(out, test_out)
        

class test_CircularConduit(unittest.TestCase):
    """CircularConduitUnit.
    """

    def setUp(self):
        """
        """
        self.conduit_data = [
            'CONDUIT Circular conduit unit',
            'CIRCULAR',
            'CIRC_US     CIRC_DS',
            '    10.000',
            'MANNING',
            '   101.200     1.500    GLOBAL     0.100     0.110    GLOBAL     0.200     0.210',
            '   0.03000   0.03500',
        ]

    def test_readHeadData(self):
        """Test that the data is read in properly."""
        # create a unloaded river unit to just check the readHeadData() method.
        c = conduitunit.CircularConduitUnit()
        # Put the test data into the method
        c.readUnitData(self.conduit_data, 0)

        self.assertEqual(c.unit_type, 'conduit_circular')
        self.assertEqual(c.unit_category, 'conduit')

        self.assertEqual(c._name, 'CIRC_US')
        self.assertEqual(c._name_ds, 'CIRC_DS')
        self.assertEqual(c.head_data['distance'].value, 10.0)
        self.assertEqual(c.head_data['roughness_type'].value, 'MANNING')
        self.assertEqual(c.head_data['invert'].value, 101.2)
        self.assertEqual(c.head_data['diameter'].value, 1.5)
        self.assertEqual(c.head_data['bottom_slot_status'].value, 'GLOBAL')
        self.assertEqual(c.head_data['bottom_slot_distance'].value, 0.1)
        self.assertEqual(c.head_data['bottom_slot_depth'].value, 0.11)
        self.assertEqual(c.head_data['top_slot_status'].value, 'GLOBAL')
        self.assertEqual(c.head_data['top_slot_distance'].value, 0.2)
        self.assertEqual(c.head_data['top_slot_depth'].value, 0.21)
        self.assertEqual(c.head_data['roughness_below_axis'].value, 0.03)
        self.assertEqual(c.head_data['roughness_above_axis'].value, 0.035)

    def test_getData(self):
        """Check that the correctly formatted text is being returned."""
        test_out = [
            'CONDUIT Circular conduit unit',
            'CIRCULAR',
            'CIRC_US     CIRC_DS     ',
            '    10.000',
            'MANNING',
            '   101.200     1.500    GLOBAL     0.100     0.110    GLOBAL     0.200     0.210',
            '   0.03000   0.03500',
        ]
        # create a unloaded river unit to just check the readHeadData() method.
        c = conduitunit.CircularConduitUnit()
        # Put the test data into the method
        c.readUnitData(self.conduit_data, 0)
        out = c.getData()
        self.assertListEqual(out, test_out)
        