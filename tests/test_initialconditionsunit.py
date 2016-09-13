import unittest

from ship.isis.datunits import initialconditionsunit
from ship.isis.datunits import ROW_DATA_TYPES as rdt

class InitialConditionsUnitTests(unittest.TestCase): 
    """
    """
    '''        
    1.042_US     y     5.000    32.788     2.084     3.935     0.000     0.000    32.417
    1.042_BU     y     5.000    32.788     2.080     3.930     1.000     0.000    32.417
    1.042_BD     y     5.000    32.788     2.080     3.930     0.000     0.000     0.000
    1.042_SU     y     0.000    32.788     2.080     3.930     0.000     0.000    33.881
    '''
    def setUp(self):
        """
        """

        self.test_data = \
            [
            'INITIAL CONDITIONS',
            ' label   ?      flow     stage froude no  velocity     umode    ustate         z',
            'ic1         y     5.000    31.084     0.871     2.082     0.000     0.000    30.380',
            'ic2         y     5.000    31.022     0.542     1.433     0.000     0.000    30.017',
            'ic3         y     5.000    30.448     0.541     1.569     0.000     0.000    29.427',
            ]
            

        
    def test_readUnitData(self):
        """Read unit data properly."""
        ic_rows = \
        [
            ['ic1', 'ic2', 'ic3'],
            ['y', 'y', 'y'],
            [5.000, 5.000, 5.000],
            [31.084, 31.022, 30.448],
            [0.871, 0.542, 0.541],
            [2.082, 1.433, 1.569],
            [0.000, 0.000, 0.000],
            [0.000, 0.000, 0.000],
            [30.380, 30.017, 29.427],
        ]
        
        ic = initialconditionsunit.InitialConditionsUnit(3)
        ic.readUnitData(self.test_data, 0)
        row_data = ic.row_collection.getRowDataAsList()
        self.assertListEqual(ic_rows, row_data)
        
    
    def test_getData(self):
        out_data = \
        [
            'INITIAL CONDITIONS',
            ' label   ?      flow     stage froude no  velocity     umode    ustate         z',
            'ic1          y     5.000    31.084     0.871     2.082     0.000     0.000    30.380',
            'ic2          y     5.000    31.022     0.542     1.433     0.000     0.000    30.017',
            'ic3          y     5.000    30.448     0.541     1.569     0.000     0.000    29.427'
        ]
        
        ic = initialconditionsunit.InitialConditionsUnit(3)
        ic.readUnitData(self.test_data, 0)
        d = ic.getData()
        self.assertListEqual(d, out_data)
        self.assertEqual(ic.node_count, 3)
        
        
    def test_addDataRow(self):
        row_data = {rdt.LABEL: 'ic4', rdt.ELEVATION: 10.000, rdt.FLOW: 3.000, rdt.VELOCITY: 1.5}
        ic = initialconditionsunit.InitialConditionsUnit(0)
        ic.addDataRow(row_data)
        self.assertEqual(ic.node_count, 1)
        
        # Make sure we can't add the same ic row twice
        row_data2 = {rdt.LABEL: 'ic4', rdt.ELEVATION: 10.000, rdt.FLOW: 3.000, rdt.VELOCITY: 1.5}
        self.assertEqual(ic.node_count, 1)

        
    def test_deleteRowByName(self): 
        """Delete a row from the ic's."""
        ic = initialconditionsunit.InitialConditionsUnit(3)
        ic.readUnitData(self.test_data, 0)
        self.assertEqual(ic.node_count, 3)
        ic.deleteDataRowByName('ic2')
        self.assertEqual(ic.node_count, 2)
        
    
    def test_getRowByName(self): 
        """Get row by name."""
        ic = initialconditionsunit.InitialConditionsUnit(3)
        ic.readUnitData(self.test_data, 0)
        row_data = ic.getRowByName('ic2')
        test_data = {rdt.ELEVATION: 30.017, rdt.LABEL: 'ic2', rdt.FLOW: 5.0,
                     rdt.STAGE: 31.022, rdt.FROUDE_NO: 0.542, rdt.VELOCITY: 1.433,
                     rdt.UMODE: 0.0, rdt.USTATE: 0.0, rdt.QMARK: 'y'}
        self.assertDictEqual(row_data, test_data)
        
    
    def test_updateDataRowByName(self):
        """Test updating row with new values."""
        ic = initialconditionsunit.InitialConditionsUnit(3)
        ic.readUnitData(self.test_data, 0)
        ic.updateDataRowByName({rdt.ELEVATION: 999.9}, 'ic2')
        row_data = ic.getRowByName('ic2')
        elev = row_data[rdt.ELEVATION]
        self.assertEqual(elev, 999.9)
        
        
        
        
        
        