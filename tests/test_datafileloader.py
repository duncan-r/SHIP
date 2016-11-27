# 
# from __future__ import unicode_literals
# 
# import unittest
# import os
#  
# from ship.tuflow.datafiles import datafileloader
# from ship.tuflow.datafiles.datafileobject import TmfDataObject, \
#                                 BcDataObject, MatCsvDataObject, XsDataObject
# from ship.tuflow.tuflowfilepart import DataFile, GisFile
# from ship.datastructures.rowdatacollection import RowDataCollection
# from ship.datastructures import dataobject as do 
#  
#  
# class DataFileLoaderTests(unittest.TestCase):
#     '''Tests the function and setup of the ADataFileComponent_OLD object and it's 
#     subclasses.
#     '''
#      
#     def setUp(self):
#         '''Setup any expensive variables that are needed for all tests.
#         '''
#         self.curd = os.getcwd()
#         self.comment_types = ['!', '#']
#          
#      
#     def test_extractInlineComment(self):
#         """Check that comments are extracted from line correctly"""
#  
#         testline1 = '1,0.06,,,,,,,,,,! Open pasture'
#         testline2 = '1,0.06,,,,,,,,,,# Open pasture'
#         outline = '1,0.06,,,,,,,,,,'
#         outcomment = ' Open pasture'
#          
#         self.assertTupleEqual((outline, outcomment), datafileloader._extractInlineComment(testline1, self.comment_types), 'Inline comment extraction fail for "!"')
#         self.assertTupleEqual((outline, outcomment), datafileloader._extractInlineComment(testline2, self.comment_types), 'Inline comment extraction fail for "#"')
#          
#      
#     def test_hasCommentOnlyLine(self):
#         """Check that we can pick up lines with only comments on"""
#  
#         testline1 = '! Some comment only line'
#         testline2 = '# Some comment only line 2'
#         testline3 = '1,0.06,,,,,,,,,,! Open pasture'
#          
#         self.assertEqual(testline1, datafileloader.hasCommentOnlyLine(testline1, self.comment_types), 'Comment only line fail for "!"')
#         self.assertEqual(testline2, datafileloader.hasCommentOnlyLine(testline2, self.comment_types), 'Comment only line fail for "#"')
#         self.assertFalse(datafileloader.hasCommentOnlyLine(testline3, self.comment_types), 'Not a comment only line fail')
#          
#      
#     def test_createXsDataFileObject_Shp(self):
#         """Loads a 1d cross section gis file and checks the contents get setup."""
#         
#         test_list = [['Section1.csv', 'Section2.csv', 'Section3.csv', 'Section4.csv'],
#                      ['xz', 'xz', 'xz', 'xz'],
#                      ['', '', '', ''],
#                      ['Section1', 'Section2', 'Section3', 'Section4'],
#                      ['', '', '', ''],
#                      ['', '', '', ''],
#                      ['', '', '', ''],
#                      ['', '', '', ''],
#                      ['', '', '', ''],
#                      [0.0, 0.0, 0.0, 0.0],
#                      [0.0, 0.0, 0.0, 0.0],
#                      [0.0, 0.0, 0.0, 0.0],
#                      [0, 1, 2, 3]
#                     ]
#         
#         # First test for Shapefile
#         gis_path = os.path.join(self.curd, r'tests\test_data\xs\1d_xs_test.shp')
#         hex_hash = hashlib.md5(gis_path.encode())
#         hex_hash = hex_hash.hexdigest()
#         datafile = GisFile(1, gis_path, hex_hash, 3, 'Read MI Table Links', 'tgc')
#         gis = datafileloader.loadDataFile(datafile)
#     
#         self.assertIsInstance(gis, XsDataObject, 'Factory create XsDataObject fail - SHP')
#         self.assertEqual(hex_hash, gis.path_holder.hex_hash, 'Hex_hash equality fail - SHP')
#         self.assertEqual('Read MI Table Links', gis.path_holder.command, 'Command equality fail - SHP')
#         
#         row_list = gis.row_collection.getRowDataAsList()
#         self.assertListEqual(test_list, row_list, 'List contents not equal fail - SHP')
#         
#         # Then for MapInfo file
#         gis_path = os.path.join(self.curd, r'tests\test_data\xs\1d_xs_test.mif')
#         hex_hash = hashlib.md5(gis_path.encode())
#         hex_hash = hex_hash.hexdigest()
#         datafile = GisFile(1, gis_path, hex_hash, 3, 'Read MI Table Links', 'tcf')
#         gis = datafileloader.loadDataFile(datafile)
#     
#         self.assertIsInstance(gis, XsDataObject, 'Factory create XsDataObject fail - MIF')
#         self.assertEqual(hex_hash, gis.path_holder.hex_hash, 'Hex_hash equality fail - MIF')
#         self.assertEqual('Read MI Table Links', gis.path_holder.command, 'Command equality fail - MIF')
#         
#         row_list = gis.row_collection.getRowDataAsList()
#         self.assertListEqual(test_list, row_list, 'List contents not equal fail - MIF')
#     
#     
#     def test_createBcDataFileObject(self):
#         """Loads a boundary condition csv file and checks that it is setup properly"""
#               
#         bc_path = os.path.join(self.curd, r'tests\test_data\bc_dbase\bc_dbase_test.csv')
#         hex_hash = hashlib.md5(bc_path.encode())
#         hex_hash = hex_hash.hexdigest()
#         datafile = DataFile(1, bc_path, hex_hash, 3, 'BC Database', 'tcf')
#         bc = datafileloader.loadDataFile(datafile)
#     
#         self.assertIsInstance(bc, BcDataObject, 'Factory create BcDataObject fail')
#         self.assertEqual(hex_hash, bc.path_holder.hex_hash, 'Hex_hash equality fail')
#         self.assertEqual('BC Database', bc.path_holder.command, 'Command equality fail')
#         
#         test_list = [['Name1', 'Name2', 'Name3'],
#                      ['Name1.csv', 'Name2.csv', 'Name2.csv'],
#                      ['time', 'time', 'time'],
#                      ['Downstream', 'Flow', 'Dummy'],
#                      ['', '', ''],
#                      ['', '', ''],
#                      ['', '', ''],
#                      ['', '', ''],
#                      ['', '', ''],
#                      ['Name', 'Source', 'Column1_or_Time', 'Column2_or_Value_or_ID', 
#                       'TimeAdd', 'ValueMult', 'ValueAdd', 'IMultF', 'IAddF'],
#                      [0, 1, 2]
#                     ]
#         
#         row_list = bc.row_collection.getRowDataAsList()
#         self.assertListEqual(test_list, row_list, 'List contents not equal fail')
#         
#     
#     def test_createTmfDataFileObject(self):
#         """Loads a .tmf file and checks that it is setup properly"""
#         
#         mat_path = os.path.join(self.curd, r'tests\test_data\Materials_TMF.tmf')
#         hex_hash = hashlib.md5(mat_path.encode())
#         hex_hash = hex_hash.hexdigest()
#         datafile = DataFile(1, mat_path, hex_hash, 3, 'Read Materials File', 'tcf')
#         mat = datafileloader.loadDataFile(datafile)
#     
#         self.assertIsInstance(mat, TmfDataObject, 'Factory create TmfDataObject fail')
#         self.assertEqual(hex_hash, mat.path_holder.hex_hash, 'Hex_hash equality fail')
#         self.assertEqual('Read Materials File', mat.path_holder.command, 'Command equality fail')
#         
#         test_list = [[1, 2, 3, 4, 5, 6, 7],
#                      [0.06, 0.025, 0.04, 0.08, 0.3, 0.1, 0.08],
#                      ['', '', '', '', '', '', ''],
#                      ['', '', '', '', '', '', ''],
#                      ['', '', '', '', '', '', ''],
#                      ['', '', '', '', '', '', ''],
#                      ['', '', '', '', '', '', ''],
#                      ['', '', '', '', '', '', ''],
#                      ['', '', '', '', '', '', ''],
#                      ['', '', '', '', '', '', ''],
#                      ['', '', '', '', '', '', ''],
#                      ['Open pasture',
#                       'Roads and Paths',
#                       'Tracks',
#                       'Trees',
#                       'Buildings',
#                       'Inland water',
#                       'Gardens'],
#                      [0, 1, 2, 3, 4, 5, 6]]
#         
#         row_list = mat.row_collection.getRowDataAsList()
#         self.assertListEqual(test_list, row_list, 'List contents not equal fail')
#     
#     
#     def test_createMatCsvDataFileObject(self):
#         """Loads a Materials.csv file and checks setup"""
#         
#         mat_path = os.path.join(self.curd, r'tests\test_data\materials_csv\Materials_CSV.csv')
#         hex_hash = hashlib.md5(mat_path.encode())
#         hex_hash = hex_hash.hexdigest()
#         datafile = DataFile(1, mat_path, hex_hash, 3, 'Read Materials File', 'tcf')
#         mat = datafileloader.loadDataFile(datafile)
#     
#         self.assertIsInstance(mat, MatCsvDataObject, 'Factory create MatCsvDataObject fail')
#         self.assertEqual(hex_hash, mat.path_holder.hex_hash, 'Hex_hash equality fail')
#         self.assertEqual('Read Materials File', mat.path_holder.command, 'Command equality fail')
#     
#         test_list = [['1', '2', '3', '4', '10', '11', '20', '21', '30', '31', '40'],
#                      ['', 0.022, '', 0.03, 0.08, '', '', '', '', '', ''],
#                      [0.03, '', 0.03, '', '', 0.03, '', '', '', '', ''],
#                      [0.1, '', 0.02, '', '', 0.1, '', '', '', '', ''],
#                      [0.1, '', 0.1, '', '', 0.1, '', '', '', '', ''],
#                      [0.06, '', 3.0, '', '', 0.04, '', '', '', '', ''],
#                      ['',
#                       '',
#                       '',
#                       '',
#                       '',
#                       '',
#                       'Otherfile.csv',
#                       'Otherfile.csv',
#                       'Anotherfile.csv',
#                       'Anotherfile.csv',
#                       'Onlyname.csv'],
#                      ['', '', '', '', '', '', 'Depth', 'Depth', '< 50mm', '50mm - 150mm', ''],
#                      ['', '', '', '', '', '', 'light values', 'heavy values', '', '', ''],
#                      [5.0, 0.0, 0.0, 5.0, 5.0, 5.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#                      [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#                      ['', '', '', '', '', '', '', '', '', '', ''],
#                      ['! Description',
#                       '!Pasture',
#                       '!Roads',
#                       '!Buildings',
#                       '!Ponds and other water',
#                       '!Vegetated creek',
#                       '!Maintained Grass',
#                       '!Subfile light test',
#                       '!Subfile heavy test',
#                       '!Anotherfile under 50 test',
#                       '!Anotherfile over 50 test',
#                       '!Onlyname test'],
#                      ['Material ID',
#                       "Manning's n",
#                       '',
#                       '',
#                       '',
#                       '',
#                       '',
#                       '',
#                       '',
#                       'Infiltration Parameters',
#                       '',
#                       'Land Us Hazard ID'],
#                      [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]]
#         row_list = mat.row_collection.getRowDataAsList()
#         self.assertListEqual(test_list, row_list, 'List contents not equal fail')
#         
#         
#         '''
#          Check that the sub files loaded properly as well
#         '''
#         sub_extract = {}
#         for sub in mat.subfiles:
#             sub_extract[sub.filename] = sub.row_collection.getRowDataAsList()
#             i=0
#             
#         name1 = 'Otherfile'
#         otherfile_testlist = [[0.03, 0.06, 0.09],
#                              [0.48, 0.31, 0.194],
#                              [0.8, 0.6, 0.36],
#                              ['', '', ''],
#                              ['', 'Some other text that noone cares about', ''],
#                              ['Depth', 'light values', 'heavy values', '', ''],
#                              [0, 1, 2, 3, 4]]
#     
#         name2 = 'Onlyname'
#         onlyname_testlist = [[0.002, 0.00309, 0.00331],
#                              [0.400786, 0.074916, 0.056848],
#                              ['Random header', ''],
#                              [0, 1, 2, 3, 4]]
#         
#         name3 = 'Anotherfile'
#         anotherfile_testlist = [[0.0477, 0.0077, 0.0132, 0.0277, 0.036],
#                                  [0.88, 0.765, 0.666, 0.646, 0.626],
#                                  ['', '', '', '', ''],
#                                  [0.0155, 0.0177, 0.0277, 0.0377, 0.0527],
#                                  [0.753, 0.74, 0.666, 0.631, 0.5947],
#                                  ['< 50mm', '', '', '50mm - 150mm', ''],
#                                  [0, 1, 2, 3, 4, 5, 6]]
#         
#         self.assertListEqual(otherfile_testlist, sub_extract[name1], 'Otherfile data fail')
#         self.assertListEqual(onlyname_testlist, sub_extract[name2], 'Onlyname data fail')
#         self.assertListEqual(anotherfile_testlist, sub_extract[name3], 'Anotherfile data fail')
#     
#     
#     
#     