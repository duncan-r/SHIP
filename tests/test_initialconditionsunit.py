from __future__ import unicode_literals

import unittest
 
from ship.fmp.datunits import initialconditionsunit
from ship.fmp.datunits import ROW_DATA_TYPES as rdt
 
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
        self.name_types = {'ic1': ['river'], 'ic2': ['river'], 'ic3': ['river']}
 
         
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
         
        # create a unloaded river unit to just check the readHeadData() method.
        ic = initialconditionsunit.InitialConditionsUnit()
        # Put the test data into the readrowData() method
        ic.readUnitData(self.test_data, 0, node_count=3, name_types=self.name_types)

        row_data = ic.row_data['main'].toList()
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
         
        ic = initialconditionsunit.InitialConditionsUnit()
        ic.readUnitData(self.test_data, 0, node_count=3, name_types=self.name_types)
        d = ic.getData()
        self.assertListEqual(d, out_data)
        self.assertEqual(ic.node_count, 3)
         
         
    def test_addDataRow(self):
        """Test adding a row to ic unit."""
        row_data = {rdt.LABEL: 'ic4', rdt.ELEVATION: 10.000, rdt.FLOW: 3.000, rdt.VELOCITY: 1.5}

        # create a unloaded river unit to just check the readHeadData() method.
        ic = initialconditionsunit.InitialConditionsUnit()
        ic.addRow(row_data, 'river')
        self.assertEqual(ic.node_count, 1)
        
        added_row = ic.row_data['main'].rowAsList(0)
        self.assertListEqual(added_row, ['ic4', 'y', 3.0, 0.0, 0.0, 1.5, 0.0, 0.0, 10.0])
         
        # Make sure we can't add the same ic row twice
        row_data = {rdt.LABEL: 'ic4', rdt.ELEVATION: 10.000, rdt.FLOW: 3.000, rdt.VELOCITY: 1.5}
        ic.addRow(row_data, 'river')
        self.assertEqual(ic._node_count, 1)

#         row_data2 = {rdt.LABEL: 'ic4', rdt.ELEVATION: 10.000, rdt.FLOW: 3.000, rdt.VELOCITY: 1.5}
#         self.assertEqual(ic.node_count, 1)
 
         
    def test_deleteRowByName(self): 
        """Delete a row from the ic's."""
        ic = initialconditionsunit.InitialConditionsUnit()
        ic.readUnitData(self.test_data, 0, node_count=3, name_types=self.name_types)

        self.assertEqual(ic.node_count, 3)

        # See if we can delete one
        ic.deleteRowByName('ic2', 'river')
        self.assertEqual(ic.node_count, 2)
        
        # Try and delete one that doesn't exist
        with self.assertRaises(KeyError):
            ic.deleteRowByName('ic2', 'river')
        self.assertEqual(ic.node_count, 2)
        
     
    def test_rowByName(self): 
        """Get row by name."""
        ic = initialconditionsunit.InitialConditionsUnit()
        ic.readUnitData(self.test_data, 0, node_count=3, name_types=self.name_types)

        row_data = ic.rowByName('ic2')
        test_data = {rdt.ELEVATION: 30.017, rdt.LABEL: 'ic2', rdt.FLOW: 5.0,
                     rdt.STAGE: 31.022, rdt.FROUDE_NO: 0.542, rdt.VELOCITY: 1.433,
                     rdt.UMODE: 0.0, rdt.USTATE: 0.0, rdt.QMARK: 'y'}
        self.assertDictEqual(row_data, test_data)
         
     
    def test_updateDataRowByName(self):
        """Test updating row with new values."""
        ic = initialconditionsunit.InitialConditionsUnit()
        ic.readUnitData(self.test_data, 0, node_count=3, name_types=self.name_types)

        ic.updateRowByName({rdt.ELEVATION: 999.9}, 'ic2')

        row_data = ic.rowByName('ic2')
        elev = row_data[rdt.ELEVATION]
        self.assertEqual(elev, 999.9)
         
         
         