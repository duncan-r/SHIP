import unittest

from ship.isis.datunits import spillunit

class test_SpillUnit(unittest.TestCase):
    """
    """
    
    def setUp(self):
        """
        """
        self.spill_unitdata = [  'SPILL',
                                 '1.056_SU    1.056_SD',
                                 '     1.200     0.900',
                                 '         3',
                                 '     0.000    37.651      0.00      0.00',
                                 '     5.000    38.000      0.00      0.00',
                                 '     6.550    37.900      0.00      0.00']
        
        self.spill_header_vars = {'coeff': '1.200',
                                 'comment': '',
                                 'modular_limit': '0.900',
                                 'rowcount': 3,
                                 'section_label': '1.056_SU',
                                 'ds_label': '1.056_SD'}
    
    
    def test_readSpillUnit(self):
        """Check that it's reading the spill unit in properly"""

        spill_rows = [[0.0, 5.0, 6.55], [37.651, 38.0, 37.9], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        
        spill = spillunit.SpillUnit()
        spill.readUnitData(self.spill_unitdata, 0)
        row_data = spill.row_collection.getRowDataAsList()
        self.assertListEqual(spill_rows, row_data)
        self.assertDictEqual(self.spill_header_vars, spill.head_data, 'Arch head data match fail')
        
    
    def test_getSpillData(self):
        """Check the contents returned by the Spill unit are correct"""
        test_output = [  'SPILL ',
                         '1.056_SU    1.056_SD    ',
                         '     1.200     0.900',
                         '         3',
                         '     0.000    37.651      0.00      0.00',
                         '     5.000    38.000      0.00      0.00',
                         '     6.550    37.900      0.00      0.00'
                      ]
                     
        
        spill = spillunit.SpillUnit()
        spill.readUnitData(self.spill_unitdata, 0)
        output = spill.getData()

        self.assertListEqual(test_output, output)

