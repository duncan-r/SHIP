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
        
        
class test_FullarchConduit(unittest.TestCase):
    """FullarchConduitUnit.
    """

    def setUp(self):
        """
        """
        self.conduit_data = [
            'CONDUIT Full arch conduit unit',
            'FULLARCH',
            'ARCH_US     ARCH_DS',
            '    10.000',
            'COLEBROOK-WHITE',
            '   100.000     2.000     1.000       OFF     0.100     0.110        ON     0.200     0.210',
            '   0.03000   0.03500',
        ]

    def test_readHeadData(self):
        """Test that the data is read in properly."""
        # create a unloaded river unit to just check the readHeadData() method.
        c = conduitunit.FullarchConduitUnit()
        # Put the test data into the method
        c.readUnitData(self.conduit_data, 0)

        self.assertEqual(c.unit_type, 'conduit_fullarch')
        self.assertEqual(c.unit_category, 'conduit')

        self.assertEqual(c._name, 'ARCH_US')
        self.assertEqual(c._name_ds, 'ARCH_DS')
        self.assertEqual(c.head_data['distance'].value, 10.0)
        self.assertEqual(c.head_data['roughness_type'].value, 'COLEBROOK-WHITE')
        self.assertEqual(c.head_data['invert'].value, 100.0)
        self.assertEqual(c.head_data['width'].value, 2.0)
        self.assertEqual(c.head_data['height'].value, 1.0)
        self.assertEqual(c.head_data['bottom_slot_status'].value, 'OFF')
        self.assertEqual(c.head_data['bottom_slot_distance'].value, 0.1)
        self.assertEqual(c.head_data['bottom_slot_depth'].value, 0.11)
        self.assertEqual(c.head_data['top_slot_status'].value, 'ON')
        self.assertEqual(c.head_data['top_slot_distance'].value, 0.2)
        self.assertEqual(c.head_data['top_slot_depth'].value, 0.21)
        self.assertEqual(c.head_data['roughness_below_axis'].value, 0.03)
        self.assertEqual(c.head_data['roughness_above_axis'].value, 0.035)

    def test_getData(self):
        """Check that the correctly formatted text is being returned."""
        test_out = [
            'CONDUIT Full arch conduit unit',
            'FULLARCH',
            'ARCH_US     ARCH_DS     ',
            '    10.000',
            'COLEBROOK-WHITE',
            '   100.000     2.000     1.000       OFF     0.100     0.110        ON     0.200     0.210',
            '   0.03000   0.03500',
        ]
        # create a unloaded river unit to just check the readHeadData() method.
        c = conduitunit.FullarchConduitUnit()
        # Put the test data into the method
        c.readUnitData(self.conduit_data, 0)
        out = c.getData()
        self.assertListEqual(out, test_out)
        
        
class test_SprungarchConduit(unittest.TestCase):
    """SprungarchConduitUnit.
    """

    def setUp(self):
        """
        """
        self.conduit_data = [
            'CONDUIT Sprung arch conduit unit',
            'SPRUNGARCH',
            'SPRUNG_US     SPRUNG_DS',
            '    10.000',
            'COLEBROOK-WHITE',
            '   100.000     5.000     1.000     1.500    GLOBAL     0.100     0.110    GLOBAL     0.200     0.210',
            '   0.03000   0.03500   0.04000',
        ]

    def test_readHeadData(self):
        """Test that the data is read in properly."""
        # create a unloaded river unit to just check the readHeadData() method.
        c = conduitunit.SprungarchConduitUnit()
        # Put the test data into the method
        c.readUnitData(self.conduit_data, 0)

        self.assertEqual(c.unit_type, 'conduit_sprungarch')
        self.assertEqual(c.unit_category, 'conduit')

        self.assertEqual(c._name, 'SPRUNG_US')
        self.assertEqual(c._name_ds, 'SPRUNG_DS')
        self.assertEqual(c.head_data['distance'].value, 10.0)
        self.assertEqual(c.head_data['roughness_type'].value, 'COLEBROOK-WHITE')
        self.assertEqual(c.head_data['invert'].value, 100.0)
        self.assertEqual(c.head_data['width'].value, 5.0)
        self.assertEqual(c.head_data['springing_height'].value, 1.0)
        self.assertEqual(c.head_data['crown_height'].value, 1.5)
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
            'CONDUIT Sprung arch conduit unit',
            'SPRUNGARCH',
            'SPRUNG_US   SPRUNG_DS   ',
            '    10.000',
            'COLEBROOK-WHITE',
            '   100.000     5.000     1.000     1.500    GLOBAL     0.100     0.110    GLOBAL     0.200     0.210',
            '   0.03000   0.03500   0.04000',
        ]
        # create a unloaded river unit to just check the readHeadData() method.
        c = conduitunit.SprungarchConduitUnit()
        # Put the test data into the method
        c.readUnitData(self.conduit_data, 0)
        out = c.getData()
        self.assertListEqual(out, test_out)
        
        
class test_SymmetricalConduit(unittest.TestCase):
    """SymmetricalConduitUnit.
    """

    def setUp(self):
        """
        """
        self.conduit_data = [
            'CONDUIT Symmetrical conduit unit',
            'SECTION',
            'SYM_US      SYM_DS',
            '    10.000',
            '         4',
            '     0.000   100.000   0.00300',
            '     5.000   100.000   0.00300',
            '     5.000   105.000   0.00300',
            '     0.000   105.000   0.00300',
        ]

    def test_readHeadData(self):
        """Test that the data is read in properly."""
        # create a unloaded river unit to just check the readHeadData() method.
        c = conduitunit.SymmetricalConduitUnit()
        # Put the test data into the method
        c.readUnitData(self.conduit_data, 0)

        self.assertEqual(c.unit_type, 'conduit_symmetrical')
        self.assertEqual(c.unit_category, 'conduit')

        self.assertEqual(c._name, 'SYM_US')
        self.assertEqual(c._name_ds, 'SYM_DS')
        self.assertEqual(c.head_data['distance'].value, 10.0)
        
    def test_readRowData(self):
        """Check that row data is ok"""
        # create a unloaded river unit to just check the readHeadData() method.
        b = conduitunit.SymmetricalConduitUnit()
        # Put the test data into the method
        b.readUnitData(self.conduit_data, 0)

        # Lists for each of the data objects that are created when reading the file
        chainage = [0.000, 5.000, 5.000, 0.000]
        elevation = [100.000, 100.000, 105.000, 105.000]
        roughness = [0.003, 0.003, 0.003, 0.003]

        self.assertListEqual(b.row_data['main'].dataObjectAsList(rdt.CHAINAGE), chainage)
        self.assertListEqual(b.row_data['main'].dataObjectAsList(rdt.ELEVATION), elevation)
        self.assertListEqual(b.row_data['main'].dataObjectAsList(rdt.ROUGHNESS), roughness)

    def test_getData(self):
        """Check that the correctly formatted text is being returned."""
        test_out = [
            'CONDUIT Symmetrical conduit unit',
            'SECTION',
            'SYM_US      SYM_DS      ',
            '    10.000',
            '         4',
            '     0.000   100.000   0.00300',
            '     5.000   100.000   0.00300',
            '     5.000   105.000   0.00300',
            '     0.000   105.000   0.00300',
        ]
        # create a unloaded river unit to just check the readHeadData() method.
        c = conduitunit.SymmetricalConduitUnit()
        # Put the test data into the method
        c.readUnitData(self.conduit_data, 0)
        out = c.getData()
        self.assertListEqual(out, test_out)


class test_AsymmetricalConduit(unittest.TestCase):
    """AsymmetricalConduitUnit.
    """

    def setUp(self):
        """
        """
        self.conduit_data = [
            'CONDUIT Asymmetrical conduit unit',
            'ASYMMETRIC',
            'ASYM_US     ASYM_DS',
            '    10.000   MANNING',
            '        11',
            '     0.000   100.000     0.003',
            '     0.500    99.500     0.003',
            '     1.000    99.000     0.003',
            '     1.000    98.500     0.003',
            '     1.500    98.000     0.003',
            '     2.000    98.050     0.003',
            '     2.500    98.000     0.003',
            '     5.000    98.100     0.003',
            '     3.000    99.000     0.003',
            '     2.000    99.500     0.003',
            '     0.000   100.000     0.003',  
        ]

    def test_readHeadData(self):
        """Test that the data is read in properly."""
        # create a unloaded river unit to just check the readHeadData() method.
        c = conduitunit.AsymmetricalConduitUnit()
        # Put the test data into the method
        c.readUnitData(self.conduit_data, 0)

        self.assertEqual(c.unit_type, 'conduit_asymmetrical')
        self.assertEqual(c.unit_category, 'conduit')

        self.assertEqual(c._name, 'ASYM_US')
        self.assertEqual(c._name_ds, 'ASYM_DS')
        self.assertEqual(c.head_data['distance'].value, 10.0)
        
    def test_readRowData(self):
        """Check that row data is ok"""
        # create a unloaded river unit to just check the readHeadData() method.
        b = conduitunit.AsymmetricalConduitUnit()
        # Put the test data into the method
        b.readUnitData(self.conduit_data, 0)

        # Lists for each of the data objects that are created when reading the file
        chainage = [0.000, 0.500, 1.000, 1.000, 1.500, 2.000, 2.500, 5.000, 3.000, 2.000, 0.000]
        elevation = [100.000, 99.500, 99.000, 98.500, 98.000, 98.050, 98.000, 98.100, 99.000, 99.500, 100.000]
        roughness = [0.003, 0.003, 0.003, 0.003, 0.003, 0.003, 0.003, 0.003, 0.003, 0.003, 0.003]

        self.assertListEqual(b.row_data['main'].dataObjectAsList(rdt.CHAINAGE), chainage)
        self.assertListEqual(b.row_data['main'].dataObjectAsList(rdt.ELEVATION), elevation)
        self.assertListEqual(b.row_data['main'].dataObjectAsList(rdt.ROUGHNESS), roughness)

    def test_getData(self):
        """Check that the correctly formatted text is being returned."""
        
        # Note that it's always written out to 5sf because it makes it easier when
        # switching between Darcy and Manning precision and FMP doesn't care.
        test_out = [
            'CONDUIT Asymmetrical conduit unit',
            'ASYMMETRIC',
            'ASYM_US     ASYM_DS     ',
            '    10.000   MANNING',
            '        11',
            '     0.000   100.000   0.00300',
            '     0.500    99.500   0.00300',
            '     1.000    99.000   0.00300',
            '     1.000    98.500   0.00300',
            '     1.500    98.000   0.00300',
            '     2.000    98.050   0.00300',
            '     2.500    98.000   0.00300',
            '     5.000    98.100   0.00300',
            '     3.000    99.000   0.00300',
            '     2.000    99.500   0.00300',
            '     0.000   100.000   0.00300',  
        ]
        # create a unloaded river unit to just check the readHeadData() method.
        c = conduitunit.AsymmetricalConduitUnit()
        # Put the test data into the method
        c.readUnitData(self.conduit_data, 0)
        out = c.getData()
        self.assertListEqual(out, test_out)