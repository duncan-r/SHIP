from __future__ import unicode_literals

import unittest

from ship.datastructures import dataobject as do
from ship.datastructures.dataobject import ADataRowObject
from ship.fmp.datunits import ROW_DATA_TYPES as rdt


class DataObjectsTest(unittest.TestCase):

    def setUp(self):

        self.flt = do.FloatData(rdt.CHAINAGE, format_str='{:>10}', no_of_dps=3)
        self.sym = do.SymbolData(rdt.PANEL_MARKER, '*', format_str='{:<5}', default=False)
        self.con = do.ConstantData(rdt.BANKMARKER, ('', 'LEFT', 'RIGHT', 'BED'), format_str='{:<10}', default='')
        self.con_nodefault = do.ConstantData(rdt.BANKMARKER, ('', 'LEFT', 'RIGHT', 'BED'), format_str='{:<10}')
        self.txt = do.StringData(rdt.SPECIAL, format_str='{:<10}', default='~')

        self.data_objects = [self.flt, self.sym, self.con, self.txt]

    def test_float_addValue(self):

        self.flt = self.flt
        self.flt.addValue(4.33)
        self.assertTrue(self.flt.data_collection[0] == 4.33, str(self.flt.data_type) + 'addValue(no index) fail')
        self.flt.addValue('4.32')
        self.assertTrue(self.flt.data_collection[1] == 4.32, str(self.flt.data_type) + 'addValue(no index) fail')
        self.flt.addValue(4)
        self.assertTrue(self.flt.data_collection[2] == 4.0, str(self.flt.data_type) + 'addValue(no index) fail')
        self.failUnlessRaises(ValueError, lambda: self.flt.addValue('trick'))
        self.failUnlessRaises(IndexError, lambda: self.flt.addValue(5.1, 10))

    def test_Symbol_addValue(self):

        self.sym.addValue('*')
        self.assertTrue(self.sym.data_collection[0] == True, 'Symbol object add value fail')
        self.sym.addValue(True)
        self.assertTrue(self.sym.data_collection[1] == True, 'Symbol object add value fail')
        self.sym.addValue(False)
        self.assertFalse(self.sym.data_collection[2] == True, 'Symbol object add value fail')
        self.failUnlessRaises(IndexError, lambda: self.sym.addValue(True, 4))
        self.failUnlessRaises(ValueError, lambda: self.sym.addValue(14, 4))

    def test_constant_addValue(self):
        self.con.addValue('LEFT')
        self.assertTrue(self.con.data_collection[0] == 'LEFT', 'BankMarker object addValue() fail')
        self.con.addValue('RIGHT')
        self.assertTrue(self.con.data_collection[1] == 'RIGHT', 'BankMarker object addValue() fail')
        self.con.addValue('BED')
        self.assertTrue(self.con.data_collection[2] == 'BED', 'BankMarker object addValue() fail')
        self.con.addValue('')
        self.assertTrue(self.con.data_collection[3] == '', 'BankMarker object addValue() fail')
        with self.assertRaises(ValueError):
            self.con_nodefault.addValue(5)
        with self.assertRaises(ValueError):
            self.con_nodefault.addValue('random$%%&_string')
        with self.assertRaises(IndexError):
            self.con.addValue('LEFT', 7)

    def test_float_setValue(self):

        self.flt.data_collection.append(3.14)
        self.flt.data_collection.append('3.14')
        self.flt.setValue(2.12, 1)
        self.assertTrue(self.flt.data_collection[0] == 3.14, 'FloatDataObject (' + str(self.flt.data_type) + ') setValue() failure')
        self.failUnlessRaises(ValueError, lambda: self.flt.setValue('trick', 1))
        self.failUnlessRaises(IndexError, lambda: self.flt.setValue(2.12, 3))

    def test_symbol_setValue(self):

        self.sym.data_collection.append('*')
        self.sym.data_collection.append(False)

        self.sym.setValue('*', 1)
        self.assertTrue(self.sym.data_collection[1] == True, 'Symbol setValue() failure')
        self.sym.setValue(False, 0)
        self.assertTrue(self.sym.data_collection[0] == False, 'Symbol setValue() failure')
        self.failUnlessRaises(IndexError, lambda: self.sym.setValue(True, 3))
        self.failUnlessRaises(ValueError, lambda: self.sym.setValue('rnd%$_string', 1))

    def test_constant_setValue(self):

        self.con.data_collection.append('LEFT')
        self.con.data_collection.append('')

        self.con.setValue('', 0)
        self.assertFalse(self.con.data_collection[0], 'Constant setValue() failure')
#         self.assertTrue(self.con.data_collection[0] == False, 'Constant setValue() failure')
        self.con.setValue('RIGHT', 1)
        self.assertTrue(self.con.data_collection[1] == 'RIGHT', 'Constant setValue() failure')
        self.con.setValue('LEFT', 1)
        self.assertTrue(self.con.data_collection[1] == 'LEFT', 'Constant setValue() failure')
        self.con.setValue('BED', 1)
        self.assertTrue(self.con.data_collection[1] == 'BED', 'Constant setValue() failure')
        self.failUnlessRaises(IndexError, lambda: self.con.setValue('LEFT', 3))

    def test_float_printValue(self):
        self.flt.data_collection.append(103.142)
        expected_output = '   103.142'
        self.assertEqual(self.flt.getPrintableValue(0), expected_output, 'Chainage getPrintableValue() failure')
        self.failUnlessRaises(IndexError, lambda: self.flt.getPrintableValue(1))

    def test_symbol_printValue(self):
        self.sym.data_collection.append(True)
        expected_output = '*    '
        self.assertEqual(self.sym.getPrintableValue(0), expected_output, 'Symbol getPrintableValue() True failure')
        self.sym.data_collection.append(False)
        expected_output = '     '
        self.assertEqual(self.sym.getPrintableValue(1), expected_output, 'Symbol getPrintableValue() False failure')
        self.failUnlessRaises(IndexError, lambda: self.sym.getPrintableValue(3))

    def test_constant_printValue(self):
        self.con.data_collection.append('LEFT')
        expected_output = 'LEFT      '
        self.assertEqual(self.con.getPrintableValue(0), expected_output, 'BankMarker getPrintableValue() 0 failure')
        self.con.data_collection.append('RIGHT')
        expected_output = 'RIGHT     '
        self.assertEqual(self.con.getPrintableValue(1), expected_output, 'BankMarker getPrintableValue() 1 failure')
        self.con.data_collection.append('BED')
        expected_output = 'BED       '
        self.assertEqual(self.con.getPrintableValue(2), expected_output, 'BankMarker getPrintableValue() 2 failure')
        self.con.data_collection.append(False)
        expected_output = '          '
        self.assertEqual(self.con.getPrintableValue(3), expected_output, 'BankMarker getPrintableValue() 3 failure')
        self.failUnlessRaises(IndexError, lambda: self.con.getPrintableValue(5))

    def test_string_printValue(self):
        self.txt.data_collection.append('1435')
        expected_output = '1435      '
        self.assertEqual(self.txt.getPrintableValue(0), expected_output, 'Special getPrintableValue() 0 failure')
        self.txt.data_collection.append('')
        expected_output = ''
        self.assertEqual(self.txt.getPrintableValue(1), expected_output, 'Special getPrintableValue() 1 failure')
        self.failUnlessRaises(IndexError, lambda: self.txt.getPrintableValue(3))
