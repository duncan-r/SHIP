from __future__ import unicode_literals

import unittest
 
from ship.fmp.datunits import htbdyunit
from ship.fmp.datunits import ROW_DATA_TYPES as rdt
from ship.fmp.isisunitfactory import IsisUnitFactory
 
class test_HtbdyUnit(unittest.TestCase):
    """
    """
     
    def setUp(self):
        """
        """
        self.htbdy_data = [
            'HTBDY A comment',
            'RIV_DS2',
            '        11               WEEKS    REPEAT    SPLINE',
            '     1.000     0.000',
            '     2.000     1.000',
            '     3.000     2.000',
            '     4.000     3.000',
            '     5.000     4.000',
            '     4.000     5.000',
            '     3.000     6.000',
            '     2.000     7.000',
            '     1.000     8.000',
            '     1.000     9.000',
            '     1.000    10.000',
        ]
         
        self.time      = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        self.elevation = [1.0, 2.0, 3.0, 4.0, 5.0, 4.0, 3.0, 2.0, 1.0, 1.0, 1.0]
    
    def test_readHeadData(self):
        """Check the head data is read in properly."""
        # create a unloaded river unit to just check the readHeadData() method.
        h = htbdyunit.HtbdyUnit()
        # Put the test data into the method
        h._readHeadData(self.htbdy_data, 0) 
        
        self.assertEqual(h.unit_type, 'htbdy')
        self.assertEqual(h.unit_category, 'boundary_ds')
        self.assertEqual(h._name, 'RIV_DS2')
        self.assertEqual(h._name_ds, 'unknown')
        self.assertEqual(h.head_data['comment'].value, 'A comment')
        self.assertEqual(h.head_data['multiplier'].value, 1.000)
        self.assertEqual(h.head_data['time_units'].value, 'WEEKS')
        self.assertEqual(h.head_data['extending_method'].value, 'REPEAT')
        self.assertEqual(h.head_data['interpolation'].value, 'SPLINE')

     
    def test_readSpillUnit(self):
        """check the row data is read in correctly."""
        # create a unloaded river unit to just check the readHeadData() method.
        h = htbdyunit.HtbdyUnit()
        # Put the test data into the method
        h.readUnitData(self.htbdy_data, 0) 
        
        self.assertEqual(h.row_data['main'].row_count, 11)
        self.assertListEqual(h.row_data['main'].dataObjAsList(rdt.TIME), self.time)
        self.assertListEqual(h.row_data['main'].dataObjAsList(rdt.ELEVATION), self.elevation)
        
        
    def test_getData(self):
        """Make sure the returned data is formatted corretly."""
        test_data = [
            'HTBDY A comment',
            'RIV_DS2     ',
            '        11               WEEKS    REPEAT    SPLINE',
            '     1.000     0.000',
            '     2.000     1.000',
            '     3.000     2.000',
            '     4.000     3.000',
            '     5.000     4.000',
            '     4.000     5.000',
            '     3.000     6.000',
            '     2.000     7.000',
            '     1.000     8.000',
            '     1.000     9.000',
            '     1.000    10.000',
        ]
        # create a unloaded river unit to just check the readHeadData() method.
        h = htbdyunit.HtbdyUnit()
        # Put the test data into the method
        h.readUnitData(self.htbdy_data, 0) 

        out = h.getData()
        self.assertListEqual(out, test_data)
    
    def test_addRow(self):
        """Make sure that new rows are added correctly.
        
        This is a bit of a complex one because of the way it works out some
        state when it is not provided.
        """
        # create a unloaded river unit to just check the readHeadData() method.
        h = htbdyunit.HtbdyUnit()
        # Put the test data into the method
        h.readUnitData(self.htbdy_data, 0) 

        ttest1 = [0.0, 1.0, 2.0, 3.0, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        etest1 = [1.0, 2.0, 3.0, 4.0, 5.0, 5.0, 4.0, 3.0, 2.0, 1.0, 1.0, 1.0]
        h.addRow(row_vals={rdt.ELEVATION: 5.0, rdt.TIME: 4.5}, index=5)
        outt = h.row_data['main'].dataObjAsList(rdt.TIME)
        oute = h.row_data['main'].dataObjAsList(rdt.ELEVATION)
        self.assertListEqual(ttest1, outt)
        self.assertListEqual(etest1, oute)

        ttest2 = [0.0, 1.0, 2.0, 3.0, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0]
        etest2 = [1.0, 2.0, 3.0, 4.0, 5.0, 5.0, 4.0, 3.0, 2.0, 1.0, 1.0, 1.0, 5.0]
        h.addRow(row_vals={rdt.ELEVATION: 5.0})
        outt = h.row_data['main'].dataObjAsList(rdt.TIME)
        oute = h.row_data['main'].dataObjAsList(rdt.ELEVATION)
        self.assertListEqual(ttest2, outt)
        self.assertListEqual(etest2, oute)
        
        
        
        
        
        