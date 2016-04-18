
import unittest

from ship.data_structures.rowdatacollection import *
from ship.data_structures import dataobject as do
from ship.isis.datunits import ROW_DATA_TYPES as rdt


class RowDataCollectionTests(unittest.TestCase):
    
    def setUp(self):
        # Create some object to use and add a couple of rows
        # create chainage in position 1
        self.obj1 = do.FloatData(0, rdt.CHAINAGE, format_str='{:>10}', default=None, no_of_dps=3)
        self.obj1.data_collection.append(0.00)
        self.obj1.data_collection.append(3.65)
        self.obj1.record_length = 1
        # Create elevation in position 2
        self.obj2 = do.FloatData(1, rdt.ELEVATION, format_str='{:>10}', default=None, no_of_dps=3)
        self.obj2.data_collection.append(32.345)
        self.obj2.data_collection.append(33.45)
        self.obj2.record_length = 1
        # Create roughness in position 3
        self.obj3 = do.FloatData(2, rdt.ROUGHNESS, format_str='{:>10}', default=None, no_of_dps=3)
        self.obj3.data_collection.append(0.035)
        self.obj3.data_collection.append(0.035)
        self.obj3.record_length = 1
        
        self.testcol = RowDataCollection()
        self.testcol._collection.append(self.obj1)
        self.testcol._collection.append(self.obj2)
        self.testcol._collection.append(self.obj3)

    
    def test_initCollection(self):
        '''
        '''
        # Create a dummy collection
        obj1 = do.FloatData(0, rdt.CHAINAGE, format_str='{:>10}', default=None, no_of_dps=3)
        obj2 = do.FloatData(1, rdt.ELEVATION, format_str='{:>10}', default=None, no_of_dps=3)
        obj3 = do.FloatData(2, rdt.ROUGHNESS, format_str='{:>10}', default=0.0, no_of_dps=3)
        localcol = RowDataCollection()
        localcol._collection.append(obj1)
        localcol._collection.append(obj2)
        localcol._collection.append(obj3)

        # Initiliase a real collection
        col = RowDataCollection()
        col.initCollection(do.FloatData(0, rdt.CHAINAGE, format_str='{:>10}', default=None, no_of_dps=3))
        col.initCollection(do.FloatData(1, rdt.ELEVATION, format_str='{:>10}', default=None, no_of_dps=3))
        col.initCollection(do.FloatData(2, rdt.ROUGHNESS, format_str='{:>10}', default=0.0, no_of_dps=3))
            
        # Check that they're the same
        col_eq, msg = self.checkCollectionEqual(localcol, col)
        self.assertTrue(col_eq, 'RowDataCollection initialisation fail - ' + msg)
        
    
    def checkCollectionEqual(self, c1, c2):
        '''Check the two given collections to make sure that they contain the same data.
        @param c1: First RowDataCollection object
        @param c2: Second RowDataCollection object 
        @return: True if they're equal False and reason if not.
        '''
        if not len(c1._collection) == len(c2._collection):
            return False, 'Collections are different lengths'
        
        for i in range(0, len(c1._collection)):
            if not c1._collection[i].data_type == c2._collection[i].data_type:
                return False, 'Collections have different data_types'
            
            if not c1._collection[i].format_str == c2._collection[i].format_str:
                return False, 'Collections have different format_str'

            if not c1._collection[i].row_pos == c2._collection[i].row_pos:
                return False, 'Collections have different row_pos'

            if not c1._collection[i].default == c2._collection[i].default:
                return False, 'Collections have different default'
            
            for j in range(0, len(c1._collection[i].data_collection)):
                if not c1._collection[i].data_collection[j] == c1._collection[i].data_collection[j]:
                    return False, 'Collections have different data'
            
        return True, '' 
    
    
    def test_addValue(self):
        '''
        '''
        self.testcol.addValue(rdt.CHAINAGE, 14.32)

        self.assertEqual(0.00, self.testcol._collection[0].data_collection[0], 'Collection addValue() fail') 
        self.assertEqual(3.65, self.testcol._collection[0].data_collection[1], 'Collection addValue() fail') 
        self.assertEqual(14.32, self.testcol._collection[0].data_collection[2], 'Collection addValue() fail') 
        
    
    def test_getPrintableRow(self): 
        '''
        '''
        test_row = '     0.000    32.345     0.035'
        printed_row = self.testcol.getPrintableRow(0)
        self.assertEqual(test_row, printed_row, 'Collection getPrintableRow() fail')
        
        
    def test_addNewRow(self):
        '''
        '''
        values = {rdt.CHAINAGE: 1.34, rdt.ELEVATION: 34.54, rdt.ROUGHNESS: 0.035}
        index = 1
        
        self.testcol.addNewRow(values, index)
        self.assertEqual(1.34, self.testcol._collection[0].data_collection[1], 'Collection addNewRow() fail - wrong value') 
        self.assertEqual(34.54, self.testcol._collection[1].data_collection[1], 'Collection addNewRow() fail - wrong value') 
        self.assertEqual(0.035, self.testcol._collection[2].data_collection[1], 'Collection addNewRow() fail - wrong value')
        
        self.failUnlessRaises(IndexError, lambda: self.testcol.addNewRow(values, 3)) 

        values = {'chainage': 1.34, 'elevation': 34.54, 'roughness': 0.035, 'redherring': 39.453}
        self.failUnlessRaises(KeyError, lambda: self.testcol.addNewRow(values, 1)) 
        
        
    def test_getCollectionTypes(self):
        '''
        '''
        types_test = [rdt.CHAINAGE, rdt.ELEVATION, rdt.ROUGHNESS]
        types = self.testcol.getCollectionTypes()
        self.assertListEqual(types_test, types, 'Collection getCollectionTypes() fail')
        

    def test_getDataObject(self): 
        '''
        '''
        new_obj = self.testcol.getDataObject(rdt.CHAINAGE)
        obj = self.testcol._collection[0]
        
        self.assertEqual(obj, new_obj, 'getDataObject() fail')
    
    
    def test_getDataObjectCopy(self):
        '''
        '''
        new_obj = self.testcol.getDataObjectCopy(rdt.CHAINAGE)
        obj = self.testcol._collection[0]

        self.assertNotEqual(new_obj, obj, 'getDataObjectCopy() fail')
        
        
    def test_getDataValue(self):
        '''
        '''
        index = 1
        
        value = self.testcol.getDataValue(rdt.ELEVATION, index)
        self.assertEqual(33.45, value, 'getDataValue() right key fail')
        self.failUnlessRaises(KeyError, lambda: self.testcol.getDataValue('redherring', index)) 
        self.failUnlessRaises(IndexError, lambda: self.testcol.getDataValue(rdt.ELEVATION, 3)) 
        
        
    def test_checkRowsInSync(self):
        '''
        '''
        test_sync = self.testcol.checkRowsInSync()
        self.assertTrue(self.testcol.checkRowsInSync(), 'checkRowsInSync() test true fail')
        
        self.testcol.addValue(rdt.CHAINAGE, 17.343)
        self.assertFalse(self.testcol.checkRowsInSync(), 'checkRowsInSync() test false fail')
        
        
        
        
        