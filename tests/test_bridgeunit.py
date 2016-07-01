import unittest

from ship.isis.datunits import bridgeunit

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
            
        
        self.arch_header_vars = \
        {'calibration_coef': '1.000',
         'comment': 'Main Road bridge - Trimmed to BT',
         'ds_label': '1.056_BD',
         'dual_distance': '0.000',
         'no_of_orifices': '',
         'op_cd': '1',
         'op_lower': '0.1',
         'op_upper': '0.1',
         'orifice_flag': 'ORIFICE',
         'remote_ds': '1.056_DS',
         'remote_us': '1.056_US',
         'roughness_type': 'MANNING',
         'row_count_additional': {'Opening': 1},
         'rowcount': 15,
         'skew_angle': '40.000',
         'section_label': '1.056_BU',
         'width': '0.000'}
        
        self.usbpr_header_vars = \
        {'abutment_align': 'ALIGNED',
         'abutment_type': '3',
         'calibration_coef': '1.000',
         'comment': 'Bridge over the weir at bend in river based on section 1.042',
         'ds_label': '1.042_BD',
         'dual_distance': '0.000',
         'no_arches': 0,
         'no_culverts': 0,
         'no_of_orifices': '0',
         'no_of_piers': '0',
         'op_cd': '1',
         'op_lower': '0.1',
         'op_upper': '0.1',
         'orifice_flag': 'ORIFICE',
         'pier_calibration_coeff': '',
         'pier_faces': '',
         'pier_shape': 'FLAT',
         'pier_shape_2': '',
         'pier_width': 0,
         'remote_ds': '1.042_DS',
         'remote_us': '1.042_US',
         'roughness_type': 'MANNING',
         'row_count_additional': {'Opening': 1, 'Orifice': 0},
         'rowcount': 11,
         'skew_angle': '0.000',
         'section_label': '1.042_BU',
         'width': '0.000'}
        

    def test_readUnitDataArch(self):
        """
        """
        # Lists for each of the data objects that are created when reading the file
        arch_rows = \
        [
        [0.000, 0.065, 0.137, 0.391, 0.650, 0.710, 1.618, 2.694, 3.729, 4.408, 5.306, 6.441, 6.459, 6.478, 6.557],
        [37.651, 36.161, 36.122, 34.171, 34.125, 33.743, 33.543, 33.598, 33.513, 33.519, 33.553, 33.758, 34.954, 36.174, 36.229],
        [0.025, 0.025, 0.025, 0.025, 0.040, 0.040, 0.040, 0.040, 0.040, 0.040, 0.040, 0.040, 0.040, 0.025, 0.025],
        [False, False, False, False, 'L', False, False, False, False, False, False, False, False, 'R', False] 
        ]
        arch_openings = [[0.71], [6.441], [34.47], [36.0]]

        arch = bridgeunit.BridgeUnitArch()
        arch.readUnitData(self.arch_unitdata, 0)
        row_data = arch.row_collection.getRowDataAsList()
        self.assertListEqual(arch_rows, row_data)
        self.assertDictEqual(self.arch_header_vars, arch.head_data, 'Arch head data match fail')
    
        opening_data = arch.additional_row_collections['Opening'].getRowDataAsList()
        self.assertListEqual(arch_openings, opening_data, 'Usbpr opening data match fail')

    
    def test_readUnitDataUsbpr(self):
        """
        """
        # Lists for each of the data objects that are created when reading the file
        usbpr_rows = \
        [[11.562, 11.587, 11.692, 12.03, 12.579, 13.475, 14.452, 15.127, 15.231, 15.256, 15.267],
        [33.961, 33.667, 32.418, 32.417, 32.426, 32.419, 32.422, 32.425, 33.667, 33.969, 34.096],
        [0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04],
        ['L', False, False, False, False, False, False, False, False, False, 'R']]
        
        usbpr_openings = [[11.587], [15.231], [33.680], [33.680]]
        usbpr_orifice = [[], [], [], [], [], []]


        usbpr = bridgeunit.BridgeUnitUsbpr()
        usbpr.readUnitData(self.usbpr_unitdata, 0)
        row_data = usbpr.row_collection.getRowDataAsList()
        self.assertListEqual(usbpr_rows, row_data)
        self.assertDictEqual(self.usbpr_header_vars, usbpr.head_data, 'Usbpr head data match fail')
        
        opening_data = usbpr.additional_row_collections['Opening'].getRowDataAsList()
        self.assertListEqual(usbpr_openings, opening_data, 'Usbpr opening data match fail')
        
        orifice_data = usbpr.additional_row_collections['Orifice'].getRowDataAsList()
        self.assertListEqual(usbpr_orifice, orifice_data, 'Usbpr orifice data match fail')
        
    
    def test_getUnitDataArch(self):
        """Check it's returning the correctly formatted data"""
        test_output = ['BRIDGE Main Road bridge - Trimmed to BT',
                         'ARCH',
                         '1.056_BU    1.056_BD    1.056_US    1.056_DS    ',
                         'MANNING',
                         '     1.000    40.000     0.000     0.000             ORIFICE     0.100     0.100     1.000',
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
        arch = bridgeunit.BridgeUnitArch()
        arch.readUnitData(self.arch_unitdata, 0)
        output = arch.getData()

        self.assertListEqual(test_output, output)

    
    def test_getUnitDataUsbpr(self):
        """Check it's returning the correctly formatted data"""
        test_output = ['BRIDGE Bridge over the weir at bend in river based on section 1.042',
                         'USBPR1978',
                         '1.042_BU    1.042_BD    1.042_US    1.042_DS    ',
                         'MANNING',
                         '     1.000     0.000     0.000     0.000         0   ORIFICE     0.100     0.100     1.000',
                         '         3',
                         '         0FLAT                          ',
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
        usbpr = bridgeunit.BridgeUnitUsbpr()
        usbpr.readUnitData(self.usbpr_unitdata, 0)
        output = usbpr.getData()

        self.assertListEqual(test_output, output)
 
 