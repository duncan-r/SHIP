import unittest
 
from ship.fmp.datunits import orificeunit
from ship.fmp.datunits import ROW_DATA_TYPES as rdt
from ship.fmp.fmpunitfactory import FmpUnitFactory
 
class test_SpillUnit(unittest.TestCase):
    """
    """
     
    def setUp(self):
        """
        """
        self.orifice_data = [
            'ORIFICE Some comments',
            'FLAPPED',
            'ORIF_US     ORIF_DS',
            '    10.000    12.000     2.000    10.000     9.000 RECTANGLE',
            '     1.000     1.100     0.700',
        ]
    def test_readHeadData(self):
        """Test that the data is read in properly."""
        # create a unloaded river unit to just check the readHeadData() method.
        s = orificeunit.OrificeUnit()
        # Put the test data into the method
        s.readUnitData(self.orifice_data, 0) 
        
        self.assertEqual(s.unit_type, 'orifice')
        self.assertEqual(s.unit_category, 'orifice')
        
        self.assertEqual(s._name, 'ORIF_US')
        self.assertEqual(s._name_ds, 'ORIF_DS')
        self.assertEqual(s.head_data['type'].value, 'FLAPPED')
        self.assertEqual(s.head_data['comment'].value, 'Some comments')
        self.assertEqual(s.head_data['invert_level'].value, 10.000)
        self.assertEqual(s.head_data['soffit_level'].value, 12.000)
        self.assertEqual(s.head_data['bore_area'].value, 2.000)
        self.assertEqual(s.head_data['us_sill_level'].value, 10.000)
        self.assertEqual(s.head_data['ds_sill_level'].value, 9.000)
        self.assertEqual(s.head_data['weir_flow'].value, 1.000)
        self.assertEqual(s.head_data['surcharged_flow'].value, 1.100)
        self.assertEqual(s.head_data['modular_limit'].value, 0.700)
        
     
    def test_getData(self):
        """Check that the correctly formatted text is being returned."""
        test_out = [
            'ORIFICE Some comments',
            'FLAPPED',
            'ORIF_US     ORIF_DS     ',
            '    10.000    12.000     2.000    10.000     9.000 RECTANGLE',
            '     1.000     1.100     0.700',
        ] 
        o = orificeunit.OrificeUnit()
        # Put the test data into the method
        o.readUnitData(self.orifice_data, 0) 
        out = o.getData()
        self.assertListEqual(out, test_out)

