import unittest

from ship.isis.datunits import riverunit
from ship.isis.datunits import ROW_DATA_TYPES
from ship.data_structures.rowdatacollection import RowDataCollection 
from ship.data_structures.dataobject import *
from ship.isis.isisunitfactory import IsisUnitFactory

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
         '1.069\n',
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
         '15.078            1.111111      1000',
         '18',
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
         
        # Dictionary of header variables that is create by the river unit
        self.header_vars = \
        {'comment': '(Culvert Exit) CH:7932 - Trimmed to BT',
         'density': '1000',
         'distance': '15.078',
         'lateral1': '',
         'lateral2': '',
         'lateral3': '',
         'lateral4': '',
         'rowcount': 18,
         'section_label': '1.069',
         'slope': '1.111111',
         'spill1': '',
         'spill2': ''}
        
        # Lists for each of the data objects that are created when reading the file
        self.bankmarker = ['LEFT', False, False, False, False, 'BED', False, False, False, False, False, False, False, False, False, False, False, 'RIGHT']    
        self.chainage = [5.996, 6.936, 7.446, 7.635, 8.561, 9.551, 10.323, 10.904, 12.542, 13.74, 13.788, 13.944, 15.008, 16.355, 17.424, 18.449, 19.416, 19.420]    
        self.deactivation = ['LEFT', False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, 'RIGHT']    
        self.easting = [291391.67, 291391.43, 291391.3, 291391.25, 291391.01, 291390.75, 291390.55, 291390.4, 291389.98, 291389.67, 291389.66, 291389.62, 291389.34, 291389.0, 291388.72, 291388.46, 291388.21, 291388.21]    
        self.elevation = [37.56, 37.197, 36.726, 35.235, 35.196, 35.19, 35.229, 35.319, 35.637, 35.593, 35.592, 36.148, 36.559, 37.542, 38.518, 39.037, 39.146, 39.133]    
        self.northing = [86582.61, 86581.7, 86581.21, 86581.03, 86580.13, 86579.18, 86578.43, 86577.87, 86576.29, 86575.13, 86575.09, 86574.93, 86573.91, 86572.6, 86571.57, 86570.58, 86569.65, 86569.65]    
        self.panelmarker = [False, True, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False]    
        self.roughness = [0.08, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08]    
        self.rpl = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]    
        self.special = ['16', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '4095']    
         
     

    def test_river_object_vars_from_load(self):
        '''Tests to check whether 
        @note: These tests should be run for every unit created to ensure that
               it properly adheres to the abstract base class conventions and
               that it is properly setup in the IsisUnitFactory.
        '''
        # Create a factory and load the river unit
        ifactory = IsisUnitFactory()       
        i, river = ifactory.createUnit(self.input_contents, 0, 'river', 1, 1)

        self.assertNotEqual(False, river, 'River not equal False fail')
        h = river.getHeadData()
        self.assertDictEqual(self.header_vars, river.getHeadData(), 'River header dicts not equal fail')
        
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.CHAINAGE).data_collection, self.chainage, 'River chainage load fail')
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.ELEVATION).data_collection, self.elevation, 'River elevation load fail')
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.ROUGHNESS).data_collection, self.roughness, 'River roughness load fail')
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.PANEL_MARKER).data_collection, self.panelmarker, 'River panelmarker load fail')
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.RPL).data_collection, self.rpl, 'River rpl load fail')
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.BANKMARKER).data_collection, self.bankmarker, 'River bankmarker load fail')
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.EASTING).data_collection, self.easting, 'River easting load fail')
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.NORTHING).data_collection, self.northing, 'River northing load fail')
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.DEACTIVATION).data_collection, self.deactivation, 'River deactivation load fail')
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.SPECIAL).data_collection, self.special, 'River special load fail')
        
        self.assertTrue(river.getUnitCategory() == 'River', 'River.unit_category fail:  River.unit_category = ' + river.unit_category)
        self.assertTrue(river.getName() == '1.069', 'River.name fail:  River.name = ' + river.name)
        self.assertTrue(river.getFileOrder() == 1, 'River.file_order fail:  River.file_order = ' + str(river.file_order))
         
 
    def test_readHeadData(self):
        '''Checks that the readHeadData() method works individually from the
        factory load in the test_river_object_vars_from_load() test.
        This should help to narrow down the problem if tests fail.
        '''
        # create a unloaded river unit to just check the readHeadData() method.
        r = riverunit.RiverUnit(0, 1)
        # Put the test data into the method
        r._readHeadData(self.unit_data_test, 0) 
        # Need to manually create the rowcount value here as it's not done in this method.
        r.head_data['rowcount'] = 18
        # Make sure they're equal
        self.assertDictEqual(self.header_vars, r.head_data, 'readHeadData() fail') 
 

    def test_readRowData(self):
        '''Checks that the readRowData() method works individually from the
        factory load in the test_river_object_vars_from_load() test.
        This should help to narrow down the problem if tests fail.
        '''
        # create a unloaded river unit to just check the readHeadData() method.
        river = riverunit.RiverUnit(0, 1)
        # Put the test data into the readrowData() method
        river.readUnitData(self.unit_data_test, 0)
       
        # Check that everything matches. 
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.CHAINAGE).data_collection, self.chainage, 'River chainage load fail')
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.ELEVATION).data_collection, self.elevation, 'River elevation load fail')
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.ROUGHNESS).data_collection, self.roughness, 'River roughness load fail')
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.PANEL_MARKER).data_collection, self.panelmarker, 'River panelmarker load fail')
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.RPL).data_collection, self.rpl, 'River rpl load fail')
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.BANKMARKER).data_collection, self.bankmarker, 'River bankmarker load fail')
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.EASTING).data_collection, self.easting, 'River easting load fail')
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.NORTHING).data_collection, self.northing, 'River northing load fail')
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.DEACTIVATION).data_collection, self.deactivation, 'River deactivation load fail')
        self.assertListEqual(river.getRowDataObject(ROW_DATA_TYPES.SPECIAL).data_collection, self.special, 'River special load fail')
        
 
    def test_getData_method(self):
        '''Test to check the suitability of the getData() method.
        '''
        river = riverunit.RiverUnit(1, 1)
        river.head_data = self.header_vars
        river.unit_length = 18
        river.row_collection
        
        # Create some data objects
        objs = []
        objs.append(FloatDataRowObject('chainage', '{:>10}', None, 0, 3))
        objs.append(FloatDataRowObject('elevation', '{:>10}', None, 1, 3))
        objs.append(FloatDataRowObject('roughness', '{:>10}', 0.0, 2, 3)) 
        objs.append(SymbolDataRowObject('panelmarker', '{:<5}', False, 3, '*'))
        objs.append(FloatDataRowObject('rpl', '{:>5}', 1.000, 4, 3))
        objs.append(ConstantDataRowObject('bankmarker', '{:<10}', '', 5, ('LEFT', 'RIGHT', 'BED')))
        objs.append(FloatDataRowObject('easting', '{:>10}', 0.0, 6, 2))
        objs.append(FloatDataRowObject('northing', '{:>10}', 0.0, 7, 2))
        objs.append(ConstantDataRowObject('deactivation', '{:<10}', '', 8, ('LEFT', 'RIGHT')))
        objs.append(StringDataRowObject('special', '{:<10}', '~', 9))
        
        # Populate the data
        objs[0].data_collection = [5.996, 6.936, 7.446, 7.635, 8.561, 9.551, 10.323, 10.904, 12.542, 13.74, 13.788, 13.944, 15.008, 16.355, 17.424, 18.449, 19.416, 19.420]    
        objs[1].data_collection = [37.56, 37.197, 36.726, 35.235, 35.196, 35.19, 35.229, 35.319, 35.637, 35.593, 35.592, 36.148, 36.559, 37.542, 38.518, 39.037, 39.146, 39.133]    
        objs[2].data_collection = [0.08, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08]    
        objs[3].data_collection = [False, True, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False]    
        objs[4].data_collection = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]    
        objs[5].data_collection = ['LEFT', False, False, False, False, 'BED', False, False, False, False, False, False, False, False, False, False, False, 'RIGHT']    
        objs[6].data_collection = [291391.67, 291391.43, 291391.3, 291391.25, 291391.01, 291390.75, 291390.55, 291390.4, 291389.98, 291389.67, 291389.66, 291389.62, 291389.34, 291389.0, 291388.72, 291388.46, 291388.21, 291388.21]    
        objs[7].data_collection = [86582.61, 86581.7, 86581.21, 86581.03, 86580.13, 86579.18, 86578.43, 86577.87, 86576.29, 86575.13, 86575.09, 86574.93, 86573.91, 86572.6, 86571.57, 86570.58, 86569.65, 86569.65]    
        objs[8].data_collection = ['LEFT', False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, 'RIGHT']    
        objs[9].data_collection = ['16', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '4095']    
          
        # Add the data object to the row data collection
        river.row_collection = RowDataCollection()
        for o in objs:
            o.record_length = 18
            river.row_collection._collection.append(o) 
        
        # Setup the list that we expect to be returned from the getData() method 
        out_data = \
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
           
        # Get the data and check it against our template
        data = river.getData()
        self.assertEquals(out_data, data, 'getData() formatting failed')
         
         
    def test_getHeadData_method(self): 
        '''Test the _getHeadData() method.
        This is a protected method that is called by the getData() method to
        format the header data for printing.
        '''
        head_data = \
        ['RIVER (Culvert Exit) CH:7932 - Trimmed to BT',
         'SECTION',
         '1.069',
         '    15.078            1.111111      1000',
         '        18'
        ]
         
        # Get a RiverUnit object
        river = riverunit.RiverUnit(1, 1)
        # Set its header values with list created in setUp() method
        river.head_data = self.header_vars
        # Set the number of rows in the unit attribute
        river.unit_length = 18
         
        # Get the header data
        out_data = [] 
        out_data = river._getHeadData()
         
        # Test the data against our template
        self.assertEqual(head_data, out_data, 'getHeadData format failed')
         
                
    def test_addDataRow_method(self):       
        '''Test adding a new row to the river section
        '''
        river = riverunit.RiverUnit(1, 1)
        river.head_data = self.header_vars
        river.unit_length = 18
        river.row_collection
        
        # Create some data objects
        objs = []
        objs.append(FloatDataRowObject(ROW_DATA_TYPES.CHAINAGE, '{:>10}', None, 0, 3))
        objs.append(FloatDataRowObject(ROW_DATA_TYPES.ELEVATION, '{:>10}', None, 1, 3))
        objs.append(FloatDataRowObject(ROW_DATA_TYPES.ROUGHNESS, '{:>10}', 0.0, 2, 3)) 
        objs.append(SymbolDataRowObject(ROW_DATA_TYPES.PANEL_MARKER, '{:<5}', False, 3, '*'))
        objs.append(FloatDataRowObject(ROW_DATA_TYPES.RPL, '{:>5}', 1.000, 4, 3))
        objs.append(ConstantDataRowObject(ROW_DATA_TYPES.BANKMARKER, '{:<10}', '', 5, ('LEFT', 'RIGHT', 'BED')))
        objs.append(FloatDataRowObject(ROW_DATA_TYPES.EASTING, '{:>10}', 0.0, 6, 2))
        objs.append(FloatDataRowObject(ROW_DATA_TYPES.NORTHING, '{:>10}', 0.0, 7, 2))
        objs.append(ConstantDataRowObject(ROW_DATA_TYPES.DEACTIVATION, '{:<10}', '', 8, ('LEFT', 'RIGHT')))
        objs.append(StringDataRowObject(ROW_DATA_TYPES.SPECIAL, '{:<10}', '~', 9))
        
        # Populate the data
        objs[0].data_collection = [5.996, 6.936, 7.446, 7.635, 8.561, 9.551, 10.323, 10.904, 12.542, 13.74, 13.788, 13.944, 15.008, 16.355, 17.424, 18.449, 19.416, 19.420]    
        objs[1].data_collection = [37.56, 37.197, 36.726, 35.235, 35.196, 35.19, 35.229, 35.319, 35.637, 35.593, 35.592, 36.148, 36.559, 37.542, 38.518, 39.037, 39.146, 39.133]    
        objs[2].data_collection = [0.08, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08]    
        objs[3].data_collection = [False, True, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False]    
        objs[4].data_collection = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]    
        objs[5].data_collection = ['LEFT', False, False, False, False, 'BED', False, False, False, False, False, False, False, False, False, False, False, 'RIGHT']    
        objs[6].data_collection = [291391.67, 291391.43, 291391.3, 291391.25, 291391.01, 291390.75, 291390.55, 291390.4, 291389.98, 291389.67, 291389.66, 291389.62, 291389.34, 291389.0, 291388.72, 291388.46, 291388.21, 291388.21]    
        objs[7].data_collection = [86582.61, 86581.7, 86581.21, 86581.03, 86580.13, 86579.18, 86578.43, 86577.87, 86576.29, 86575.13, 86575.09, 86574.93, 86573.91, 86572.6, 86571.57, 86570.58, 86569.65, 86569.65]    
        objs[8].data_collection = ['LEFT', False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, 'RIGHT']    
        objs[9].data_collection = ['16', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '4095']    
          
        # Add the data object to the row data collection
        col = RowDataCollection() 
        for o in objs:
            o.record_length = 18
            col._collection.append(o) 
        river.row_collection = col
        
        # Add a new row
        river.addDataRow(row_vals={ROW_DATA_TYPES.CHAINAGE: 9.42, ROW_DATA_TYPES.ELEVATION: 35.2,
                                   ROW_DATA_TYPES.ROUGHNESS: 0.035, ROW_DATA_TYPES.SPECIAL: '1264'}, 
                         index=5)
         
        # Make sure that we get back the same values as we set.
        self.assertEqual(9.42, river.row_collection._collection[ROW_DATA_TYPES.CHAINAGE].data_collection[5], 'Add new row - get chainage value failed')
        self.assertEqual(35.2, river.row_collection._collection[ROW_DATA_TYPES.ELEVATION].data_collection[5], 'Add new row - get elevation value failed')
        self.assertEqual(0.035, river.row_collection._collection[ROW_DATA_TYPES.ROUGHNESS].data_collection[5], 'Add new row - get roughness value failed')
        self.assertEqual(False, river.row_collection._collection[ROW_DATA_TYPES.PANEL_MARKER].data_collection[5], 'Add new row - get panelmarker value failed')
        self.assertEqual(1.000, river.row_collection._collection[ROW_DATA_TYPES.RPL].data_collection[5], 'Add new row - get rpl value failed')
        self.assertEqual(False, river.row_collection._collection[ROW_DATA_TYPES.BANKMARKER].data_collection[5], 'Add new row - get bankmarker value failed')
        self.assertEqual(0.00, river.row_collection._collection[ROW_DATA_TYPES.EASTING].data_collection[5], 'Add new row - get easting value failed')
        self.assertEqual(0.00, river.row_collection._collection[ROW_DATA_TYPES.NORTHING].data_collection[5], 'Add new row - get northing value failed')
        self.assertEqual(False, river.row_collection._collection[ROW_DATA_TYPES.DEACTIVATION].data_collection[5], 'Add new row - get deactivation value failed')
        self.assertEqual('1264', river.row_collection._collection[ROW_DATA_TYPES.SPECIAL].data_collection[5], 'Add new row - get special value failed')
         
        # This is how we expect the data to look when we get back out of the addRow() method
        new_chainage = [5.996, 6.936, 7.446, 7.635, 8.561, 9.42, 9.551, 10.323, 10.904, 12.542, 13.74, 13.788, 13.944, 15.008, 16.355, 17.424, 18.449, 19.416, 19.42]    
        new_elevation = [37.56, 37.197, 36.726, 35.235, 35.196, 35.2, 35.19, 35.229, 35.319, 35.637, 35.593, 35.592, 36.148, 36.559, 37.542, 38.518, 39.037, 39.146, 39.133]    
        new_roughness = [0.08, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08]    
        new_panelmarker = [False, True, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False]    
        new_rpl = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        new_bankmarker = ['LEFT', False, False, False, False, False, 'BED', False, False, False, False, False, False, False, False, False, False, False, 'RIGHT']    
        new_easting = [291391.67, 291391.43, 291391.3, 291391.25, 291391.01, 0.00, 291390.75, 291390.55, 291390.4, 291389.98, 291389.67, 291389.66, 291389.62, 291389.34, 291389.0, 291388.72, 291388.46, 291388.21, 291388.21]    
        new_northing = [86582.61, 86581.7, 86581.21, 86581.03, 86580.13, 0.00, 86579.18, 86578.43, 86577.87, 86576.29, 86575.13, 86575.09, 86574.93, 86573.91, 86572.6, 86571.57, 86570.58, 86569.65, 86569.65]    
        new_deactivation = ['LEFT', False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, 'RIGHT']    
        new_special = ['16', '', '', '', '', '1264', '', '', '', '', '', '', '', '', '', '', '', '', '4095'] 
             
        # Make sure that we get back the same values as we set. I.e. the data objects are updated as expected.
        self.assertListEqual(new_chainage, river.row_collection._collection[0].data_collection, 'Chainage list comparison after insertion fail')
        self.assertListEqual(new_elevation, river.row_collection._collection[1].data_collection, 'Elevation list comparison after insertion fail')
        self.assertListEqual(new_roughness, river.row_collection._collection[2].data_collection, 'Roughness list comparison after insertion fail')
        self.assertListEqual(new_panelmarker, river.row_collection._collection[3].data_collection, 'Panelmarker list comparison after insertion fail')
        self.assertListEqual(new_rpl, river.row_collection._collection[4].data_collection, 'Rpl list comparison after insertion fail')
        self.assertListEqual(new_bankmarker, river.row_collection._collection[5].data_collection, 'Bankmarker list comparison after insertion fail')
        self.assertListEqual(new_easting, river.row_collection._collection[6].data_collection, 'Easting list comparison after insertion fail')
        self.assertListEqual(new_northing, river.row_collection._collection[7].data_collection, 'Northing list comparison after insertion fail')
        self.assertListEqual(new_deactivation, river.row_collection._collection[8].data_collection, 'Deactivation list comparison after insertion fail')
        self.assertListEqual(new_special, river.row_collection._collection[9].data_collection, 'Special list comparison after insertion fail')
         
        # Check that it recognises illegal input values
        self.assertRaises(AttributeError, lambda: river.addDataRow({'trick': 39.1}))
        # Check that it recognises when it will cause a negative chainage increase
        self.assertRaises(ValueError, lambda: river.addDataRow({ROW_DATA_TYPES.CHAINAGE: 10.42, 
                                                                ROW_DATA_TYPES.ELEVATION: 35.3},
                                                               5))
         
         
    def test_negativeChainageCheck_method(self):
        '''Tests the negative chainage check method.
        @note: The method doesnot need to check for any index issues because that 
               is done in the calling method.
        '''
        # Create RiverUnit object and give it a chainage object with some data
        river = riverunit.RiverUnit(1, 1)
        chainage = FloatDataRowObject(ROW_DATA_TYPES.CHAINAGE, '{:>10}', None, 0, 3)
        chainage.data_collection = self.chainage
        chainage.record_length = 18
        river.row_collection = RowDataCollection()
        river.row_collection._collection.append(chainage)
          
        # check that we catch a negative chainage increase - > value to the right
        self.assertFalse(river._checkChainageIncreaseNotNegative(6, 10.42), 'Catch negative chainage increase fail (1)')
        # check that we catch a negative chainage increase - < value to the left
        self.assertFalse(river._checkChainageIncreaseNotNegative(5, 8.4), 'Catch negative chainage increase fail (2)')
        # Check that we don't stop a non-negative chainage increase.
        self.assertTrue(river._checkChainageIncreaseNotNegative(7, 10.42), 'Let non-negative increase through fail')
        # check that we can insert at the end.
        self.assertTrue(river._checkChainageIncreaseNotNegative(17, 19.418), 'Let non-negative increase at end of list through fail')
         
         