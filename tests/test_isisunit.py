import unittest

from ship.isis.datunits import isisunit
 
class HeaderUnitTests(unittest.TestCase):
    '''Test class for the HeaderUnit class.
    This is slightly less complicated than most of the classes as it is
    guaranteed to only be called once, at the start of the file read process.
    Therefore it doesn't need a setupUnit() method because that part is done 
    in the DatLoader class so that it can get a few variables that it needs 
    for the loading process (like the number of units).
    '''
     
     
    def setUp(self):
        ''' Setup all the variables needed in the class tests.
        '''
         
        self.input_contents = \
        ['Baseline 1% AEP Run',
         '#REVISION#1',
         '        62     0.750     0.900     0.100     0.002        12',
         '    10.000     0.020     0.010     0.700     0.101     0.701     0.000',
         'RAD FILE',
         '..\\..\\..\\..\\..\\..\\..\\..\\rgh\\roughness.rad'
        ]
     
         
        self.data_object_vars = \
        {'Direct_method': '0.002',
         'Dummy': '0.000',
         'Flow': '0.020',
         'Fr_Upper': '0.900',
         'Fr_lower': '0.750',
         'Head': '0.010',
         'Math_damp': '0.700',
         'Min_depth': '0.100',
         'Name': 'Baseline 1% AEP Run',
         'Pivot': '0.101',
         'Relax': '0.701',
         'Revision': '#REVISION#1',
         'Roughness': '..\\..\\..\\..\\..\\..\\..\\..\\rgh\\roughness.rad',
         'Unknown': '12',
         'Water_temp': '10.000',
         'node_count': '62'
        }
         
     
    def test_superclass_values_from_load_Header(self):
        '''Tests to see if the values that should have been set in the superclass
        after the __init__() and setupUnit() methods are called exist and are 
        correct.
        @note: These tests should be run for every unit created to ensure that
               it properly adheres to the abstract base class conventions.
        '''
        # Create the river unit with a file order and give it a file_line
        # variable and the dat file contents list.
        header = isisunit.HeaderUnit()
        header.readUnitData(self.input_contents, 0) 
         
        self.assertTrue(header.getUnitType() == 'Header', 'Header.unit_type fail:  Header.unit_type = ' + header.unit_type)
        self.assertTrue(header.getUnitUNIT_CATEGORY() == 'Meta', 'Header.unit_UNIT_CATEGORY fail:  Header.unit_UNIT_CATEGORY = ' + header.unit_UNIT_CATEGORY)
        self.assertTrue(header.getName() == 'Header', 'Header.name fail:  Header.name = ' + header.name)
#         self.assertTrue(header.getFileOrder() == 0, 'Header.file_order fail:  Header.file_order = ' + str(header.file_order))
         
     
     
    def test_readUnitData(self): 
        '''Test for the readUnitData() method of the HeaderUnit class.
        Quite simple at the moment. We know what the data_objects dictionary
        should look like after loading so we do a direct compare.
        This test and others should be a lot more comprehensive when the HeaderUnit
        is fully implemented.
        '''
        header = isisunit.HeaderUnit()
        header.readUnitData(self.input_contents, 0)
         
        # Make sure the loaded dictionary matched what we expect.
        self.assertDictEqual(header.head_data, self.data_object_vars, 'Data object dictionary read fail')
                              
         
         