from __future__ import unicode_literals

import unittest

from ship.fmp.datunits import junctionunit
from ship.fmp.datunits import ROW_DATA_TYPES as rdt
from ship.datastructures import dataobject as do
from ship.fmp.fmpunitfactory import FmpUnitFactory

class JunctionUnitTests(unittest.TestCase):
    '''Tests for all of the methods in the junction class.'''    
     
    def setUp(self):
        '''Sets up everyting that is needed in multiple tests to save too
        much mucking about.
        '''
         
        # Example list as read from the dat file on the readFile() method in FileTools.py
        self.input_contents = \
        ['JUNCTION Some comment stuff\n',
         'OPEN\n',
         'WOOD1530WDXXWOOD1530SUXXWOOD1530BU  WOOD1530CU']
        
        # Data as formatted by setupUnit method (basically the same as above
        # except it's been stripped
        self.unit_data_test = \
        ['JUNCTION Some comment stuff',
         'OPEN',
         'WOOD1530WDXXWOOD1530SUXXWOOD1530BU  WOOD1530CU']
         
     
    def test_readHeadData(self):
        '''Checks that the readHeadData() method works '''
        # create a unloaded river unit to just check the readHeadData() method.
        j = junctionunit.JunctionUnit()
        # Put the test data into the method
        j.readUnitData(self.unit_data_test, 0) 
        
        self.assertEqual(j.name, 'WOOD1530WDXX')
        self.assertEqual(j.name_ds, 'unknown')
        self.assertListEqual(j.head_data['names'], [
            'WOOD1530WDXX', 'WOOD1530SUXX', 'WOOD1530BU', 'WOOD1530CU'
        ])
        self.assertEqual(j.head_data['type'].value, 'OPEN')
    
    
    def test_getData(self):

        out_data = \
        ['JUNCTION Some comment stuff',
         'OPEN',
         'WOOD1530WDXXWOOD1530SUXXWOOD1530BU  WOOD1530CU  ']

        # Create a factory and load the river unit
        ifactory = FmpUnitFactory()       
        i, junction = ifactory.createUnitFromFile(self.input_contents, 0, 'JUNCTION', 1, 1)
            
        # Get the data and check it against our template
        data = junction.getData()
        self.assertEquals(out_data, data, 'getData() formatting failed')
        
        
        