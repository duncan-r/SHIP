#  
# from __future__ import unicode_literals
# 
# import unittest
# import os
# import hashlib
#  
# from ship.tuflow.datafiles import datafileloader
# from ship.tuflow.tuflowfilepart import DataFile, GisFile
#  
# class DataFileObjectTests(unittest.TestCase):
#     """
#     """
#      
#     def setUp(self):
#         """
#         """
#         self.curd = os.getcwd()
#         self.comment_types = ['!', '#']
#          
#      
#     def test_BcGetPrintableContents(self):
#         """
#         """
#         bc_path = os.path.join(self.curd, r'tests\test_data\bc_dbase\bc_dbase_test.csv') 
#         hex_hash = hashlib.md5(bc_path.encode())
#         hex_hash = hex_hash.hexdigest()
#         datafile = DataFile(1, bc_path, hex_hash, 3, 'BC Database', 'tcf')
#         bc = datafileloader.loadDataFile(datafile)
#          
#         test_contents = ['Name, Source, Column1_or_Time, Column2_or_Value_or_ID, TimeAdd, ValueMult, ValueAdd, IMultF, IAddF',
#                          'Name1, Name1.csv, time, Downstream, , , , , ',
#                          'Name2, Name2.csv, time, Flow, , , , , ',
#                          'Name3, Name2.csv, time, Dummy, , , , , '
#                          ]
#         contents = bc._getPrintableContents()
#         self.assertListEqual(test_contents, contents, 'Output contents match fail')    
#      
#      
#     def test_TmfGetPrintableContents(self):
#         """
#         """
#         mat_path = os.path.join(self.curd, r'tests\test_data\Materials_TMF.tmf') 
#         hex_hash = hashlib.md5(mat_path.encode())
#         hex_hash = hex_hash.hexdigest()
#         datafile = DataFile(1, mat_path, hex_hash, 3, 'Read Materials File', 'tcf')
#         mat = datafileloader.loadDataFile(datafile)
#          
#         test_contents = ['! Materials file test.',
#                         '!',
#                         '! Some comments at the top',
#                         '',
#                         '1, 0.060, , , , , , , , ,  ! Open pasture',
#                         '2, 0.025, , , , , , , , ,  ! Roads and Paths',
#                         '3, 0.040, , , , , , , , ,  ! Tracks',
#                         '4, 0.080, , , , , , , , ,  ! Trees',
#                         '5, 0.300, , , , , , , , ,  ! Buildings',
#                         '6, 0.100, , , , , , , , ,  ! Inland water',
#                         '7, 0.080, , , , , , , , ,  ! Gardens',
#                         '']
#         contents = mat._getPrintableContents()
#         self.assertListEqual(test_contents, contents, 'Output contents match fail')
#           
#  
#     def test_MatCsvGetPrintableContents(self):
#         """Check the contents of Materials csv file ok"""
#         mat_path = os.path.join(self.curd, r'tests\test_data\materials_csv\Materials_CSV.csv') 
#         hex_hash = hashlib.md5(mat_path.encode())
#         hex_hash = hex_hash.hexdigest()
#         datafile = DataFile(1, mat_path, hex_hash, 3, 'Read Materials File', 'tcf')
#         mat = datafileloader.loadDataFile(datafile)
#          
#         test_contents = ["Material ID, Manning's n, Infiltration Parameters, Land Us Hazard ID, ! Description",
#                          '1,"0.030,0.100,0.100,0.060","5.000, 2.000",,!Pasture',
#                          '2,0.022,"0.000, 2.000",,!Roads',
#                          '3,"0.030,0.020,0.100,3.000","0.000, 2.000",,!Buildings',
#                          '4,0.030,"5.000, 2.000",,!Ponds and other water',
#                          '10,0.080,"5.000, 2.000",,!Vegetated creek',
#                          '11,"0.030,0.100,0.100,0.040","5.000, 2.000",,!Maintained Grass',
#                          '20,Otherfile.csv | Depth | light values,"0.000, 0.000",,!Subfile light test',
#                          '21,Otherfile.csv | Depth | heavy values,"0.000, 0.000",,!Subfile heavy test',
#                          '30,Anotherfile.csv | < 50mm,"0.000, 0.000",,!Anotherfile under 50 test',
#                          '31,Anotherfile.csv | 50mm - 150mm,"0.000, 0.000",,!Anotherfile over 50 test',
#                          '40,Onlyname.csv,"0.000, 0.000",,!Onlyname test']
#         contents = mat._getPrintableContents()
#         self.assertListEqual(test_contents, contents, 'Output contents match fail')
#          
#      
#     def test_MatCsvSubfileGetPrintableContents(self):
#         """Checks the contents of subfile is working properly"""
#         mat_path = os.path.join(self.curd, r'tests\test_data\materials_csv\Materials_CSV.csv') 
#         hex_hash = hashlib.md5(mat_path.encode())
#         hex_hash = hex_hash.hexdigest()
#         datafile = DataFile(1, mat_path, hex_hash, 3, 'Read Materials File', 'tcf')
#         mat = datafileloader.loadDataFile(datafile)
#          
#         test_contents = ['Depth, light values, heavy values, , ',
#                          'y (m) ,      n ,      n ,       ,      ',
#                          ' 0.030000, 0.480000, 0.800000, , ',
#                          ' 0.060000, 0.310000, 0.600000, , Some other text that noone cares about',
#                          ' 0.090000, 0.194000, 0.360000, , ']
#         contents = mat.subfiles[0]._getPrintableContents()
#         self.assertListEqual(test_contents, contents, 'Output contents match fail')
#          
#          
#     def test_XsGetPrintableContents(self):
#         """Check that this is not implemented."""
#         gis_path = os.path.join(self.curd, r'tests\test_data\xs\1d_xs_test.mif') 
#         hex_hash = hashlib.md5(gis_path.encode())
#         hex_hash = hex_hash.hexdigest()
#         datafile = GisFile(1, gis_path, hex_hash, 3, 'Read MI Table Links', 'tgc')
#         gis = datafileloader.loadDataFile(datafile)
#  
#         self.assertRaises(NotImplementedError, lambda: gis._getPrintableContents())
#         self.assertRaises(NotImplementedError, lambda: gis.saveData())
#          
#          
#      
#          