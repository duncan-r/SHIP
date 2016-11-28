import unittest
 
from ship.fmp.datunits import culvertunit
from ship.fmp.datunits import ROW_DATA_TYPES as rdt
from ship.fmp.fmpunitfactory import FmpUnitFactory
 
class test_SpillUnit(unittest.TestCase):
    """
    """
     
    def setUp(self):
        """
        """
        self.culvert_data = [
            'CULVERT',
            'INLET',
            'CULV_US     CULV_DS',
            '    0.0098         2    0.0398      0.67       0.5         A',
            '     0.000     0.000     0.000     0.000CALCULATED     TOTAL     0.000',
        ]
    def test_readHeadData(self):
        """Test that the data is read in properly."""
        # create a unloaded river unit to just check the readHeadData() method.
        c = culvertunit.CulvertUnitInlet()
        # Put the test data into the method
        c.readUnitData(self.culvert_data, 0) 
        
        self.assertEqual(c.unit_type, 'culvert_inlet')
        self.assertEqual(c.unit_category, 'culvert')
        
        self.assertEqual(c._name, 'CULV_US')
        self.assertEqual(c._name_ds, 'CULV_DS')
        self.assertEqual(c.head_data['k'].value, 0.0098)
        self.assertEqual(c.head_data['m'].value, 2)
        self.assertEqual(c.head_data['c'].value, 0.0398)
        self.assertEqual(c.head_data['y'].value, 0.67)
        self.assertEqual(c.head_data['ki'].value, 0.500)
        self.assertEqual(c.head_data['conduit_type'].value, 'A')
        self.assertEqual(c.head_data['screen_width'].value, 0.000)
        self.assertEqual(c.head_data['bar_proportion'].value, 0.000)
        self.assertEqual(c.head_data['debris_proportion'].value, 0.000)
        self.assertEqual(c.head_data['loss_coef'].value, 0.000)
        self.assertEqual(c.head_data['reverse_flow_model'].value, 'CALCULATED')
        self.assertEqual(c.head_data['headloss_type'].value, 'TOTAL')
        self.assertEqual(c.head_data['trashscreen_height'].value, 0.000)
        
     
    def test_getData(self):
        """Check that the correctly formatted text is being returned."""
        test_out = [
            'CULVERT ',
            'INLET',
            'CULV_US     CULV_DS     ',
            '    0.0098     2.000    0.0398     0.670     0.500         A',
            '     0.000     0.000     0.000     0.000CALCULATED     TOTAL     0.000',
        ] 
        # create a unloaded river unit to just check the readHeadData() method.
        c = culvertunit.CulvertUnitInlet()
        # Put the test data into the method
        c.readUnitData(self.culvert_data, 0) 
        out = c.getData()
        self.assertListEqual(out, test_out)

