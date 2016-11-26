from __future__ import unicode_literals

import unittest
 
from ship.fmp.datunits import bridgeunit
from ship.fmp.datunits import ROW_DATA_TYPES as rdt
 
class BridgeUnitTests(unittest.TestCase): 
    """
    """
     
    def setUp(self):
        """
        """
         
        self.arch_unitdata = \
            ['BRIDGE Main Road bridge - Trimmed to BT',
             'ARCH',
             '1.056_BU    1.056_BD    1.056_US    1.056_DS',
             'MANNING',
             '     1.000    40.000     0.000     0.000             ORIFICE       0.1       0.1         1',
             '        15',
             '     0.000    37.651     0.025',
             '     0.065    36.161     0.025',
             '     0.137    36.122     0.025',
             '     0.391    34.171     0.025',
             '     0.650    34.125     0.040          L',
             '     0.710    33.743     0.040',
             '     1.618    33.543     0.040',
             '     2.694    33.598     0.040',
             '     3.729    33.513     0.040',
             '     4.408    33.519     0.040',
             '     5.306    33.553     0.040',
             '     6.441    33.758     0.040',
             '     6.459    34.954     0.040',
             '     6.478    36.174     0.025          R',
             '     6.557    36.229     0.025',
             '         1',
             '     0.710     6.441    34.470    36.000']
             
        self.usbpr_unitdata = \
            ['BRIDGE Bridge over the weir at bend in river based on section 1.042',
             'USBPR1978',
             '1.042_BU    1.042_BD    1.042_US    1.042_DS',
             'MANNING',
             '     1.000     0.000     0.000     0.000         0   ORIFICE       0.1       0.1         1',
             '         3',
             '         0FLAT      ',
             'ALIGNED',
             '        11',
             '    11.562    33.961     0.040          L',
             '    11.587    33.667     0.040',
             '    11.692    32.418     0.040',
             '    12.030    32.417     0.040',
             '    12.579    32.426     0.040',
             '    13.475    32.419     0.040',
             '    14.452    32.422     0.040',
             '    15.127    32.425     0.040',
             '    15.231    33.667     0.040',
             '    15.256    33.969     0.040',
             '    15.267    34.096     0.040          R',
             '         1',
             '    11.587    15.231    33.680    33.680',
             '         0']


    def test_readHeadDataArch(self):
        """Check that the HeadDataItem's get read in ok."""
        # create a unloaded river unit to just check the readHeadData() method.
        b = bridgeunit.BridgeUnitArch()
        # Put the test data into the method
        b._readHeadData(self.arch_unitdata, 0)
        
        self.assertEqual(b._name, '1.056_BU')
        self.assertEqual(b._name_ds, '1.056_BD')
        self.assertEqual(b.head_data['comment'].value, 'Main Road bridge - Trimmed to BT')
        self.assertEqual(b.head_data['remote_us'].value, '1.056_US')
        self.assertEqual(b.head_data['remote_ds'].value, '1.056_DS')
        self.assertEqual(b.head_data['roughness_type'].value, 'MANNING')
        self.assertEqual(b.head_data['calibration_coef'].value, 1.000)
        self.assertEqual(b.head_data['skew_angle'].value, 40.000)
        self.assertEqual(b.head_data['width'].value, 0.000)
        self.assertEqual(b.head_data['dual_distance'].value, 0.000)
        self.assertEqual(b.head_data['orifice_flag'].value, 'ORIFICE')
        self.assertEqual(b.head_data['op_lower'].value, 0.1)
        self.assertEqual(b.head_data['op_upper'].value, 0.1)
        self.assertEqual(b.head_data['op_cd'].value, 1.0)
        
    def test_readHeadDataUsbpr(self):
        """Check that the HeadDataItem's get read in ok."""
        # create a unloaded river unit to just check the readHeadData() method.
        b = bridgeunit.BridgeUnitUsbpr()
        # Put the test data into the method
        b._readHeadData(self.usbpr_unitdata, 0)
        
        self.assertEqual(b._name, '1.042_BU')
        self.assertEqual(b._name_ds, '1.042_BD')
        self.assertEqual(b.head_data['remote_us'].value, '1.042_US')
        self.assertEqual(b.head_data['remote_ds'].value, '1.042_DS')
        self.assertEqual(b.head_data['calibration_coef'].value, 1.000)
        self.assertEqual(b.head_data['skew_angle'].value, 0.000)
        self.assertEqual(b.head_data['width'].value, 0.000)
        self.assertEqual(b.head_data['dual_distance'].value, 0.000 )
        self.assertEqual(b.head_data['num_of_orifices'].value, 0)
        self.assertEqual(b.head_data['orifice_flag'].value, 'ORIFICE')
        self.assertEqual(b.head_data['op_lower'].value, 0.1)
        self.assertEqual(b.head_data['op_upper'].value, 0.1)
        self.assertEqual(b.head_data['op_cd'].value, 1)
        self.assertEqual(b.head_data['abutment_type'].value, '3')
        self.assertEqual(b.head_data['num_of_piers'].value, 0)
        self.assertEqual(b.head_data['pier_shape'].value, 'FLAT')
        self.assertEqual(b.head_data['pier_shape_2'].value, '')
        self.assertEqual(b.head_data['pier_calibration_coef'].value, '')
        self.assertEqual(b.head_data['abutment_align'].value, 'ALIGNED')


    def test_readRowDataArch(self):
        """Check that BridgeUnitArch row data is ok"""
        # create a unloaded river unit to just check the readHeadData() method.
        b = bridgeunit.BridgeUnitArch()
        # Put the test data into the method
        b.readUnitData(self.arch_unitdata, 0)
        
        # Lists for each of the data objects that are created when reading the file
        chainage = [0.000, 0.065, 0.137, 0.391, 0.650, 0.710, 1.618, 2.694, 3.729, 4.408, 5.306, 6.441, 6.459, 6.478, 6.557]
        elevation = [37.651, 36.161, 36.122, 34.171, 34.125, 33.743, 33.543, 33.598, 33.513, 33.519, 33.553, 33.758, 34.954, 36.174, 36.229]
        roughness = [0.025, 0.025, 0.025, 0.025, 0.040, 0.040, 0.040, 0.040, 0.040, 0.040, 0.040, 0.040, 0.040, 0.025, 0.025]
        marker = [False, False, False, False, 'L', False, False, False, False, False, False, False, False, 'R', False]

        self.assertListEqual(b.row_data['main'].DataObjectAsList(rdt.CHAINAGE), chainage)
        self.assertListEqual(b.row_data['main'].DataObjectAsList(rdt.ELEVATION), elevation)
        self.assertListEqual(b.row_data['main'].DataObjectAsList(rdt.ROUGHNESS), roughness)
        self.assertListEqual(b.row_data['main'].DataObjectAsList(rdt.EMBANKMENT), marker)

        open_start = [0.71]
        open_end = [6.441]
        spring = [34.47]
        soffit = [36.0]
        self.assertListEqual(b.row_data['opening'].DataObjectAsList(rdt.OPEN_START), open_start)
        self.assertListEqual(b.row_data['opening'].DataObjectAsList(rdt.OPEN_END), open_end)
        self.assertListEqual(b.row_data['opening'].DataObjectAsList(rdt.SPRINGING_LEVEL), spring)
        self.assertListEqual(b.row_data['opening'].DataObjectAsList(rdt.SOFFIT_LEVEL), soffit)
        

    def test_readUnitDataUsbpr(self):
        """
        """
        # create a unloaded river unit to just check the readHeadData() method.
        b = bridgeunit.BridgeUnitUsbpr()
        # Put the test data into the method
        b.readUnitData(self.usbpr_unitdata, 0)

        # Lists for each of the data objects that are created when reading the file
        chainage = [11.562, 11.587, 11.692, 12.03, 12.579, 13.475, 14.452, 15.127, 15.231, 15.256, 15.267]
        elevation = [33.961, 33.667, 32.418, 32.417, 32.426, 32.419, 32.422, 32.425, 33.667, 33.969, 34.096]
        roughness = [0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04]
        marker = ['L', False, False, False, False, False, False, False, False, False, 'R']

        self.assertListEqual(b.row_data['main'].DataObjectAsList(rdt.CHAINAGE), chainage)
        self.assertListEqual(b.row_data['main'].DataObjectAsList(rdt.ELEVATION), elevation)
        self.assertListEqual(b.row_data['main'].DataObjectAsList(rdt.ROUGHNESS), roughness)
        self.assertListEqual(b.row_data['main'].DataObjectAsList(rdt.EMBANKMENT), marker)

        open_start = [11.587]
        open_end = [15.231]
        spring = [33.68]
        soffit = [33.68]
        self.assertListEqual(b.row_data['opening'].DataObjectAsList(rdt.OPEN_START), open_start)
        self.assertListEqual(b.row_data['opening'].DataObjectAsList(rdt.OPEN_END), open_end)
        self.assertListEqual(b.row_data['opening'].DataObjectAsList(rdt.SPRINGING_LEVEL), spring)
        self.assertListEqual(b.row_data['opening'].DataObjectAsList(rdt.SOFFIT_LEVEL), soffit)

        # TODO - Need to add a test for culvert here

     
    def test_getUnitDataArch(self):
        
        # create a unloaded river unit to just check the readHeadData() method.
        b = bridgeunit.BridgeUnitArch()
        # Put the test data into the method
        b.readUnitData(self.arch_unitdata, 0)
        
        """Check it's returning the correctly formatted data"""
        test_output = ['BRIDGE Main Road bridge - Trimmed to BT',
                         'ARCH',
                         '1.056_BU    1.056_BD    1.056_US    1.056_DS    ',
                         'MANNING',
                         '     1.000    40.000     0.000     0.000         0   ORIFICE     0.100     0.100     1.000',
                         '        15',
                         '     0.000    37.651     0.025           ',
                         '     0.065    36.161     0.025           ',
                         '     0.137    36.122     0.025           ',
                         '     0.391    34.171     0.025           ',
                         '     0.650    34.125     0.040          L',
                         '     0.710    33.743     0.040           ',
                         '     1.618    33.543     0.040           ',
                         '     2.694    33.598     0.040           ',
                         '     3.729    33.513     0.040           ',
                         '     4.408    33.519     0.040           ',
                         '     5.306    33.553     0.040           ',
                         '     6.441    33.758     0.040           ',
                         '     6.459    34.954     0.040           ',
                         '     6.478    36.174     0.025          R',
                         '     6.557    36.229     0.025           ',
                         '         1',
                         '     0.710     6.441    34.470    36.000'] 

        output = b.getData()
        self.assertListEqual(test_output, output)
 
     
    def test_getUnitDataUsbpr(self):
        """Check it's returning the correctly formatted data"""
        # create a unloaded river unit to just check the readHeadData() method.
        b = bridgeunit.BridgeUnitUsbpr()
        # Put the test data into the method
        b.readUnitData(self.usbpr_unitdata, 0)
        
        test_output = ['BRIDGE Bridge over the weir at bend in river based on section 1.042',
                         'USBPR1978',
                         '1.042_BU    1.042_BD    1.042_US    1.042_DS    ',
                         'MANNING',
                         '     1.000     0.000     0.000     0.000         0   ORIFICE     0.100     0.100     1.000',
                         '         3',
                         '         0FLAT      ',
                         '   ALIGNED',
                         '        11',
                         '    11.562    33.961     0.040          L',
                         '    11.587    33.667     0.040           ',
                         '    11.692    32.418     0.040           ',
                         '    12.030    32.417     0.040           ',
                         '    12.579    32.426     0.040           ',
                         '    13.475    32.419     0.040           ',
                         '    14.452    32.422     0.040           ',
                         '    15.127    32.425     0.040           ',
                         '    15.231    33.667     0.040           ',
                         '    15.256    33.969     0.040           ',
                         '    15.267    34.096     0.040          R',
                         '         1',
                         '    11.587    15.231    33.680    33.680',
                         '         0']

        output = b.getData()
        self.assertListEqual(test_output, output)
  