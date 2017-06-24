from __future__ import unicode_literals

import unittest

from ship.fmp.datunits import riverunit
from ship.fmp.datunits import ROW_DATA_TYPES as rdt
from ship.datastructures.rowdatacollection import RowDataCollection 
from ship.datastructures import dataobject as do
from ship.fmp.fmpunitfactory import FmpUnitFactory

class RiverUnitTests(unittest.TestCase):
    '''Tests for all of the methods in the river class.
    The complications involved in writing these tests show that there is probably some
    serious factoring needed in the RiverUnit class.
    Perhaps breaking down the readData() method in to smaller chunks would be a good
    start. Then looking at a similar approach to the setupUnit() method.
    '''    
     
    def setUp(self):
        '''Sets up everyting that is needed in multiple tests to save too
        much mucking about.
        '''
         
        # Example list as read from the dat file on the readFile() method in FileTools.py
        self.input_contents = \
        ['RIVER (Culvert Exit) CH:7932 - Trimmed to BT\n',
         'SECTION\n',
         '1.069       Spill1      Spill2      Lat1\n',
         '    15.078            1.111111      1000\n',
         '        18\n',
         '     5.996    37.560     0.080     1.000LEFT       291391.67  86582.61LEFT      16        \n',
         '     6.936    37.197     0.035*    1.000           291391.43  86581.70          \n',
         '     7.446    36.726     0.035     1.000           291391.30  86581.21          \n',
         '     7.635    35.235     0.035     1.000           291391.25  86581.03          \n',
         '     8.561    35.196     0.035     1.000           291391.01  86580.13          \n',
         '     9.551    35.190     0.035     1.000BED        291390.75  86579.18          \n',
         '    10.323    35.229     0.035     1.000           291390.55  86578.43          \n',
         '    10.904    35.319     0.035     1.000           291390.40  86577.87          \n',
         '    12.542    35.637     0.035     1.000           291389.98  86576.29          \n',
         '    13.740    35.593     0.035     1.000           291389.67  86575.13          \n',
         '    13.788    35.592     0.035     1.000           291389.66  86575.09          \n',
         '    13.944    36.148     0.035     1.000           291389.62  86574.93          \n',
         '    15.008    36.559     0.080*    1.000           291389.34  86573.91          \n',
         '    16.355    37.542     0.080     1.000           291389.00  86572.60          \n',
         '    17.424    38.518     0.080     1.000           291388.72  86571.57          \n',
         '    18.449    39.037     0.080     1.000           291388.46  86570.58          \n',
         '    19.416    39.146     0.080     1.000           291388.21  86569.65          \n',
         '    19.420    39.133     0.080     1.000RIGHT      291388.21  86569.65RIGHT     4095      \n']
                      
                      
 
        # List as exported from the setupUnit() method
        self.unit_data_test = \
        ['RIVER (Culvert Exit) CH:7932 - Trimmed to BT',
         'SECTION',
         '1.069',
         '    15.078            1.111111      1000',
         '        18',
         '     5.996    37.560     0.080     1.000LEFT       291391.67  86582.61LEFT      16        ',
         '     6.936    37.197     0.035*    1.000           291391.43  86581.70          ',
         '     7.446    36.726     0.035     1.000           291391.30  86581.21          ',
         '     7.635    35.235     0.035     1.000           291391.25  86581.03          ',
         '     8.561    35.196     0.035     1.000           291391.01  86580.13          ',
         '     9.551    35.190     0.035     1.000BED        291390.75  86579.18          ',
         '    10.323    35.229     0.035     1.000           291390.55  86578.43          ',
         '    10.904    35.319     0.035     1.000           291390.40  86577.87          ',
         '    12.542    35.637     0.035     1.000           291389.98  86576.29          ',
         '    13.740    35.593     0.035     1.000           291389.67  86575.13          ',
         '    13.788    35.592     0.035     1.000           291389.66  86575.09          ',
         '    13.944    36.148     0.035     1.000           291389.62  86574.93          ',
         '    15.008    36.559     0.080*    1.000           291389.34  86573.91          ',
         '    16.355    37.542     0.080     1.000           291389.00  86572.60          ',
         '    17.424    38.518     0.080     1.000           291388.72  86571.57          ',
         '    18.449    39.037     0.080     1.000           291388.46  86570.58          ',
         '    19.416    39.146     0.080     1.000           291388.21  86569.65          ',
         '    19.420    39.133     0.080     1.000RIGHT      291388.21  86569.65RIGHT     4095      ']
        
        # Lists for each of the data objects that are created when reading the file
        self.bankmarker = ['LEFT', '', '', '', '', 'BED', '', '', '', '', '', '', '', '', '', '', '', 'RIGHT']    
        self.chainage = [5.996, 6.936, 7.446, 7.635, 8.561, 9.551, 10.323, 10.904, 12.542, 13.74, 13.788, 13.944, 15.008, 16.355, 17.424, 18.449, 19.416, 19.420]    
        self.deactivation = ['LEFT', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'RIGHT']    
        self.easting = [291391.67, 291391.43, 291391.3, 291391.25, 291391.01, 291390.75, 291390.55, 291390.4, 291389.98, 291389.67, 291389.66, 291389.62, 291389.34, 291389.0, 291388.72, 291388.46, 291388.21, 291388.21]    
        self.elevation = [37.56, 37.197, 36.726, 35.235, 35.196, 35.19, 35.229, 35.319, 35.637, 35.593, 35.592, 36.148, 36.559, 37.542, 38.518, 39.037, 39.146, 39.133]    
        self.northing = [86582.61, 86581.7, 86581.21, 86581.03, 86580.13, 86579.18, 86578.43, 86577.87, 86576.29, 86575.13, 86575.09, 86574.93, 86573.91, 86572.6, 86571.57, 86570.58, 86569.65, 86569.65]    
        self.panelmarker = [False, True, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False]    
        self.roughness = [0.08, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08]    
        self.rpl = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]    
        self.special = ['16', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '4095']    
         
     
    def test_readHeadData(self):
        '''Checks that the readHeadData() method works individually from the
        factory load in the test_river_object_vars_from_load() test.
        This should help to narrow down the problem if tests fail.
        '''
        # create a unloaded river unit to just check the readHeadData() method.
        r = riverunit.RiverUnit()
        # Put the test data into the method
        r._readHeadData(self.unit_data_test, 0) 
        
        self.assertEqual(r._name, '1.069')
        self.assertEqual(r._name_ds, 'unknown')
        self.assertEqual(r.head_data['comment'].value, '(Culvert Exit) CH:7932 - Trimmed to BT')
        self.assertEqual(r.head_data['distance'].value, 15.078)
        self.assertEqual(r.head_data['slope'].value, 1.111111)
        self.assertEqual(r.head_data['density'].value, 1000)
  
 
    def test_readRowData(self):
        '''Checks that the readRowData() method works individually from the
        factory load in the test_river_object_vars_from_load() test.
        This should help to narrow down the problem if tests fail.
        '''
        # create a unloaded river unit to just check the readHeadData() method.
        river = riverunit.RiverUnit()
        # Put the test data into the readrowData() method
        river.readUnitData(self.unit_data_test, 0)
        
        self.assertListEqual(river.row_data['main'].dataObjectAsList(rdt.CHAINAGE), self.chainage)
        self.assertListEqual(river.row_data['main'].dataObjectAsList(rdt.ELEVATION), self.elevation)
        self.assertListEqual(river.row_data['main'].dataObjectAsList(rdt.ROUGHNESS), self.roughness)
        self.assertListEqual(river.row_data['main'].dataObjectAsList(rdt.PANEL_MARKER), self.panelmarker)
        self.assertListEqual(river.row_data['main'].dataObjectAsList(rdt.RPL), self.rpl)
        self.assertListEqual(river.row_data['main'].dataObjectAsList(rdt.BANKMARKER), self.bankmarker)
        self.assertListEqual(river.row_data['main'].dataObjectAsList(rdt.EASTING), self.easting)
        self.assertListEqual(river.row_data['main'].dataObjectAsList(rdt.NORTHING), self.northing)
        self.assertListEqual(river.row_data['main'].dataObjectAsList(rdt.DEACTIVATION), self.deactivation)
        self.assertListEqual(river.row_data['main'].dataObjectAsList(rdt.SPECIAL), self.special)
        
        self.assertEqual(river.unit_category, 'river')
        self.assertEqual(river.unit_type, 'river')

     
    def test_getData(self):
        '''Test to check the suitability of the getData() method.
        '''
        # Create a factory and load the river unit
        ifactory = FmpUnitFactory()       
        i, river = ifactory.createUnitFromFile(self.input_contents, 0, 'RIVER', 1, 1)
         
        # Setup the list that we expect to be returned from the getData() method 
        out_data = \
        ['RIVER (Culvert Exit) CH:7932 - Trimmed to BT',
         'SECTION',
         '1.069       Spill1      Spill2      Lat1',
         '    15.078              1.1111   1000.00',
         '        18',
         '     5.996    37.560     0.080     1.000LEFT       291391.67  86582.61LEFT      16        ',
         '     6.936    37.197     0.035*    1.000           291391.43  86581.70          ',
         '     7.446    36.726     0.035     1.000           291391.30  86581.21          ',
         '     7.635    35.235     0.035     1.000           291391.25  86581.03          ',
         '     8.561    35.196     0.035     1.000           291391.01  86580.13          ',
         '     9.551    35.190     0.035     1.000BED        291390.75  86579.18          ',
         '    10.323    35.229     0.035     1.000           291390.55  86578.43          ',
         '    10.904    35.319     0.035     1.000           291390.40  86577.87          ',
         '    12.542    35.637     0.035     1.000           291389.98  86576.29          ',
         '    13.740    35.593     0.035     1.000           291389.67  86575.13          ',
         '    13.788    35.592     0.035     1.000           291389.66  86575.09          ',
         '    13.944    36.148     0.035     1.000           291389.62  86574.93          ',
         '    15.008    36.559     0.080*    1.000           291389.34  86573.91          ',
         '    16.355    37.542     0.080     1.000           291389.00  86572.60          ',
         '    17.424    38.518     0.080     1.000           291388.72  86571.57          ',
         '    18.449    39.037     0.080     1.000           291388.46  86570.58          ',
         '    19.416    39.146     0.080     1.000           291388.21  86569.65          ',
         '    19.420    39.133     0.080     1.000RIGHT      291388.21  86569.65RIGHT     4095      ']

            
        # Get the data and check it against our template
        data = river.getData()
        self.assertEquals(out_data, data, 'getData() formatting failed')


    def test_addDataRow(self):
        """Test adding a new row to 'main' data."""
        # Create a factory and load the river unit
        ifactory = FmpUnitFactory()       
        i, river = ifactory.createUnitFromFile(self.input_contents, 0, 'RIVER', 1, 1)
        
        # Add with required only args
        args = {rdt.CHAINAGE: 6.0, rdt.ELEVATION: 37.2}
        river.addRow(args, index=1)
        row = river.row_data['main'].rowAsList(1)
        testrow = [6.0, 37.2, 0.039, False, 1.0, '', 0.0, 0.0, '', '~']
        self.assertListEqual(testrow, row)
        
        # Add with all args
        args = {rdt.CHAINAGE: 6.1, rdt.ELEVATION: 37.4, rdt.ROUGHNESS: 0.06,
                rdt.PANEL_MARKER: True, rdt.RPL: 1.1, rdt.BANKMARKER: 'BED',
                rdt.EASTING: 22.5, rdt.NORTHING: 32.5, rdt.DEACTIVATION: 'RIGHT',
                rdt.SPECIAL: '16'}
        river.addRow(args, index=2)
        row = river.row_data['main'].rowAsList(2)
        testrow = [6.1, 37.4, 0.06, True, 1.1, 'BED', 22.5, 32.5, 'RIGHT', '16']
        self.assertListEqual(testrow, row)
        
        # Check it fails without required args
        args = {rdt.CHAINAGE: 6.2}
        with self.assertRaises(AttributeError):
            river.addRow(args, index=3)
        args = {rdt.ELEVATION: 36.2}
        with self.assertRaises(AttributeError):
            river.addRow(args, index=3)
            
        # Check we catch non increasing chainage
        args = {rdt.CHAINAGE: 5.0, rdt.ELEVATION: 37.2}
        with self.assertRaises(ValueError):
            river.addRow(args, index=3)


        

         