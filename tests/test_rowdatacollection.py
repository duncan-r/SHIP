
from __future__ import unicode_literals

import unittest

from ship.datastructures import rowdatacollection as rdc
from ship.datastructures import dataobject as do
from ship.fmp.datunits import ROW_DATA_TYPES as rdt


class RowDataCollectionTests(unittest.TestCase):

    def setUp(self):
        # Create some object to use and add a couple of rows
        # create chainage in position 1
        self.obj1 = do.FloatData(rdt.CHAINAGE, format_str='{:>10}', default=None, no_of_dps=3)
        self.obj1.data_collection.append(0.00)
        self.obj1.data_collection.append(3.65)
        # Create elevation in position 2
        self.obj2 = do.FloatData(rdt.ELEVATION, format_str='{:>10}', default=None, no_of_dps=3)
        self.obj2.data_collection.append(32.345)
        self.obj2.data_collection.append(33.45)
        # Create roughness in position 3
        self.obj3 = do.FloatData(rdt.ROUGHNESS, format_str='{:>10}', default=None, no_of_dps=3)
        self.obj3.data_collection.append(0.035)
        self.obj3.data_collection.append(0.035)

        self.testcol = rdc.RowDataCollection()
        self.testcol._collection.append(self.obj1)
        self.testcol._collection.append(self.obj2)
        self.testcol._collection.append(self.obj3)

    def test_initCollection(self):
        '''
        '''
        # Create a dummy collection
        obj1 = do.FloatData(rdt.CHAINAGE, format_str='{:>10}', default=None, no_of_dps=3)
        obj2 = do.FloatData(rdt.ELEVATION, format_str='{:>10}', default=None, no_of_dps=3)
        obj3 = do.FloatData(rdt.ROUGHNESS, format_str='{:>10}', default=0.0, no_of_dps=3)
        localcol = rdc.RowDataCollection()
        localcol._collection.append(obj1)
        localcol._collection.append(obj2)
        localcol._collection.append(obj3)

        # Initiliase a real collection
        col = rdc.RowDataCollection()
        col.addToCollection(do.FloatData(rdt.CHAINAGE, format_str='{:>10}', default=None, no_of_dps=3))
        col.addToCollection(do.FloatData(rdt.ELEVATION, format_str='{:>10}', default=None, no_of_dps=3))
        col.addToCollection(do.FloatData(rdt.ROUGHNESS, format_str='{:>10}', default=0.0, no_of_dps=3))

        # Check that they're the same
        col_eq, msg = self.checkCollectionEqual(localcol, col)
        self.assertTrue(col_eq, 'rdc.RowDataCollection initialisation fail - ' + msg)

    def test_bulkInitCollection(self):
        objs = [
            do.FloatData(rdt.CHAINAGE, format_str='{:>10}', default=None, no_of_dps=3),
            do.FloatData(rdt.ELEVATION, format_str='{:>10}', default=None, no_of_dps=3),
            do.FloatData(rdt.ROUGHNESS, format_str='{:>10}', default=0.0, no_of_dps=3),
        ]
        col = rdc.RowDataCollection.bulkInitCollection(objs)

        localcol = rdc.RowDataCollection()
        localcol._collection.append(objs[0])
        localcol._collection.append(objs[1])
        localcol._collection.append(objs[2])

        # Check they're the same
        col_eq, msg = self.checkCollectionEqual(localcol, col)
        self.assertTrue(col_eq, 'rdc.RowDataCollection initialisation fail - ' + msg)

    def checkCollectionEqual(self, c1, c2):
        '''Check the two given collections to make sure that they contain the same data.
        @param c1: First rdc.RowDataCollection object
        @param c2: Second rdc.RowDataCollection object 
        @return: True if they're equal False and reason if not.
        '''
        if not len(c1._collection) == len(c2._collection):
            return False, 'Collections are different lengths'

        for i in range(0, len(c1._collection)):
            if not c1._collection[i].data_type == c2._collection[i].data_type:
                return False, 'Collections have different data_types'

            if not c1._collection[i].format_str == c2._collection[i].format_str:
                return False, 'Collections have different format_str'

            if not c1._collection[i].default == c2._collection[i].default:
                return False, 'Collections have different default'

            for j in range(0, len(c1._collection[i].data_collection)):
                if not c1._collection[i].data_collection[j] == c1._collection[i].data_collection[j]:
                    return False, 'Collections have different data'

        return True, ''

    def test_indexOfDataObject(self):
        """Should return the corrent index of a particular ADataObject in colleciton."""
        index1 = self.testcol.indexOfDataObject(rdt.CHAINAGE)
        index2 = self.testcol.indexOfDataObject(rdt.ELEVATION)
        index3 = self.testcol.indexOfDataObject(rdt.ROUGHNESS)
        self.assertEquals(index1, 0)
        self.assertEquals(index2, 1)
        self.assertEquals(index3, 2)

    def test_iterateRows(self):
        """Test generator for complete row as a list"""
        testrows = [
            [0.00, 32.345, 0.035],
            [3.65, 33.45, 0.035],
        ]
        i = 0
        for row in self.testcol.iterateRows():
            self.assertListEqual(row, testrows[i])
            i += 1

    def test_iterateRowsWithKey(self):
        """Test generator for a single DataObject"""
        testrows = [
            32.345,
            33.45,
        ]
        i = 0
        for row in self.testcol.iterateRows(rdt.ELEVATION):
            self.assertEqual(row, testrows[i])
            i += 1

    def test_rowAsDict(self):
        """Shoud return a row as a dict of single values."""
        test_dict = {rdt.CHAINAGE: 0.00, rdt.ELEVATION: 32.345, rdt.ROUGHNESS: 0.035}
        row = self.testcol.rowAsDict(0)
        self.assertDictEqual(row, test_dict)

    def test_rowAsList(self):
        test_list = [0.00, 32.345, 0.035]
        row = self.testcol.rowAsList(0)
        self.assertListEqual(row, test_list)

    def test_dataObject(self):
        """Should return the correct ADataObject."""
        test_vals = [0.00, 3.65]
        obj = self.testcol.dataObject(rdt.CHAINAGE)

        self.assertEqual(obj.data_type, rdt.CHAINAGE)
        for i, o in enumerate(obj):
            self.assertEqual(o, test_vals[i])

    def test_dataObjectAsList(self):
        """Should return the contents of a DataObject as a list."""
        test_list = [0.00, 3.65]
        obj_list = self.testcol.dataObjectAsList(rdt.CHAINAGE)
        self.assertListEqual(obj_list, test_list)

    def test_toList(self):
        test_list = [
            [0.00, 3.65],
            [32.345, 33.45],
            [0.035, 0.035]
        ]
        row_list = self.testcol.toList()
        self.assertListEqual(row_list, test_list)

    def test_toDict(self):
        test_dict = {
            rdt.CHAINAGE: [0.00, 3.65],
            rdt.ELEVATION: [32.345, 33.45],
            rdt.ROUGHNESS: [0.035, 0.035],
        }
        row_dict = self.testcol.toDict()
        self.assertDictEqual(row_dict, test_dict)

    def test_addValue(self):
        # Initiliase a real collection
        col = rdc.RowDataCollection()
        col.addToCollection(do.FloatData(rdt.CHAINAGE, format_str='{:>10}', default=None, no_of_dps=3))
        col.addToCollection(do.FloatData(rdt.ELEVATION, format_str='{:>10}', default=None, no_of_dps=3))
        col.addToCollection(do.FloatData(rdt.ROUGHNESS, format_str='{:>10}', default=0.0, no_of_dps=3))

        col._addValue(rdt.CHAINAGE, 2.5)
        self.assertEqual(col._collection[0][0], 2.5)

    def test_setValue(self):
        # Initiliase a real collection
        col = rdc.RowDataCollection()
        col.addToCollection(do.FloatData(rdt.CHAINAGE, format_str='{:>10}', default=None, no_of_dps=3))
        col.addToCollection(do.FloatData(rdt.ELEVATION, format_str='{:>10}', default=None, no_of_dps=3))
        col.addToCollection(do.FloatData(rdt.ROUGHNESS, format_str='{:>10}', default=0.0, no_of_dps=3))

        col._collection[0].addValue(2.5)
        self.assertEqual(col._collection[0][0], 2.5)
        col._setValue(rdt.CHAINAGE, 3.5, 0)
        self.assertEqual(col._collection[0][0], 3.5)

    def test_getPrintableRow(self):
        test_row = '     0.000    32.345     0.035'
        row = self.testcol.getPrintableRow(0)
        self.assertEqual(row, test_row)

    def test_updateRow(self):
        new_row = {rdt.CHAINAGE: 0.1, rdt.ELEVATION: 40, rdt.ROUGHNESS: 0.06}
        self.testcol.updateRow(new_row, 0)
        row = self.testcol.rowAsDict(0)
        self.assertDictEqual(row, new_row)

        with self.assertRaises(IndexError):
            self.testcol.updateRow(new_row, 3)

        fake_row = {'fakekey': 4.3, 'andagain': 3454}
        with self.assertRaises(KeyError):
            self.testcol.updateRow(fake_row, 0)

    def test_addRow(self):
        # Initiliase a real collection
        col = rdc.RowDataCollection()
        col.addToCollection(do.FloatData(rdt.CHAINAGE, format_str='{:>10}', default=None, no_of_dps=3))
        col.addToCollection(do.FloatData(rdt.ELEVATION, format_str='{:>10}', default=None, no_of_dps=3))
        col.addToCollection(do.FloatData(rdt.ROUGHNESS, format_str='{:>10}', default=0.0, no_of_dps=3))

        new_row = {rdt.CHAINAGE: 3.0, rdt.ELEVATION: 41, rdt.ROUGHNESS: 0.06}
        new_row2 = {rdt.CHAINAGE: 6.0, rdt.ELEVATION: 42, rdt.ROUGHNESS: 0.07}
        new_row3 = {rdt.CHAINAGE: 10.0, rdt.ELEVATION: 43, rdt.ROUGHNESS: 0.08}
        new_row4 = {rdt.CHAINAGE: 20.0, rdt.ELEVATION: 44, rdt.ROUGHNESS: 0.09}

        # append and insert rows
        col.addRow(new_row2)
        col.addRow(new_row, 0)
        # append and insert again
        col.addRow(new_row4)
        col.addRow(new_row3, 2)

        row = col.rowAsDict(0)
        row2 = col.rowAsDict(1)
        row3 = col.rowAsDict(2)
        row4 = col.rowAsDict(3)
        self.assertDictEqual(row, new_row)
        self.assertDictEqual(row2, new_row2)

        fake_row = {59: 4.3}
        with self.assertRaises(KeyError):
            col.addRow(fake_row)

    def test_numberOfRows(self):
        self.assertEqual(self.testcol.numberOfRows(), 2)

    def test_deleteRow(self):

        test_list = [3.65, 33.45, 0.035]
        self.testcol.deleteRow(0)
        self.assertEqual(self.testcol.numberOfRows(), 1)
        row = self.testcol.rowAsList(0)
        self.assertListEqual(row, test_list)
