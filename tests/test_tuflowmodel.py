
import os
import unittest
import hashlib

from ship.tuflow.tuflowmodel import *
from ship.tuflow.tuflowmodelfile import *
from ship.tuflow.tuflowfilepart import *


def _encodeHash(salt):
    """Generate hash codes"""
    hex_hash = hashlib.md5(salt.encode())
    hex_hash = hex_hash.hexdigest()
    return hex_hash
    

class TuflowModelTests(unittest.TestCase):
    """Tests the TuflowModel class"""
    
    def setUp(self):
        """Setup global test values"""
        
        self.tuflow_model = TuflowModel()
        
        self.fake_root = 'c:\\some\\fake\\root'
        
        self.tuflow_model.model_order = ModelOrder()
        
        # MODEL type
        tcfpath = 'c:\\some\\fake\\root\\main.tcf'
        self.tcf_hex_hash = _encodeHash(tcfpath)
        tcf_part = SomeFile(1, tcfpath, self.tcf_hex_hash, 0, 'tcf', self.fake_root, 'tcf')
        self.tuflow_model.file_parts[self.tcf_hex_hash] = ModelFileEntry(tcf_part, 0, self.tcf_hex_hash)
        model_file = TuflowModelFile('tcf', '3hh3h43ykjdhakjhf')
        self.tuflow_model.files['tcf'][self.tcf_hex_hash] = model_file
        self.tuflow_model.model_order.addRef(ModelRef(self.tcf_hex_hash, 'tcf'), True)
        
        # GIS type
        gfilepath = '..\\madeuppath\\file.shp'
        self.gis_hex_hash = _encodeHash(gfilepath)
        gfile = GisFile(1, gfilepath, self.gis_hex_hash, 2, 'Read GIS', self.fake_root)
        model_file.addContent(2, self.gis_hex_hash)
        self.tuflow_model.file_parts[self.gis_hex_hash] = ModelFileEntry(gfile, 2, self.gis_hex_hash)

        # RESULTS type
        dfilepath = '..\\madeuppath\\2d\\results'
        self.result_hex_hash = _encodeHash(dfilepath)
        dfile = SomeFile(1, dfilepath, self.result_hex_hash, 1, 'OUTPUT FOLDER', self.fake_root)
        model_file.addContent(1, self.result_hex_hash)
        self.tuflow_model.file_parts[self.result_hex_hash] = ModelFileEntry(dfile, 1, self.result_hex_hash)

        # VARIABLE type
        vinput = 'h v q d MB1 ZUK0  ! Output: Levels, Velocities, Unit Flows, Depths, Mass Error & Hazard'
        self.vars_hex_hash = _encodeHash(vinput)
        vinput = ModelVariables(1, vinput, self.vars_hex_hash, 4, 'Map Output Data Types')
        model_file.addContent(4, self.vars_hex_hash)
        self.tuflow_model.file_parts[self.vars_hex_hash] = ModelFileEntry(vinput, 4, self.vars_hex_hash)
        
    
    def test_defaultValues(self):
        """Check that default values are correct"""
        self.assertTrue(self.tuflow_model.MODEL == 0, 'Default MODEL value fail')
        self.assertTrue(self.tuflow_model.RESULT == 1, 'Default RESULT value fail')
        self.assertTrue(self.tuflow_model.GIS == 2, 'Default GIS value fail')
        self.assertTrue(self.tuflow_model.DATA == 3, 'Default DATA value fail')
        self.assertTrue(self.tuflow_model.VARIABLE == 4, 'Default VARIABLE value fail')
        self.assertTrue(self.tuflow_model.UNKNOWN_FILE == 5, 'Default UNKNOWN_FILE value fail')
        self.assertTrue(self.tuflow_model.UNKNOWN == 6, 'Default UNKNOWN value fail')
        self.assertTrue(self.tuflow_model.COMMENT == 7, 'Default COMMENT value fail')
        self.assertTrue(self.tuflow_model.has_estry_auto == False, 'Default COMMENT value fail')
        
    
    def test_changeRoot(self):
        """Ensure that the file path root is properly updated."""
        new_root = r'c:\new\path\testroot'
        self.tuflow_model.changeRoot(new_root)
        self.assertTrue(self.tuflow_model.file_parts[self.gis_hex_hash].filepart.root == new_root, 'Update root path fail')
        self.assertTrue(self.tuflow_model.file_parts[self.result_hex_hash].filepart.root == new_root, 'Update root path fail')
        self.assertTrue(self.tuflow_model.file_parts[self.tcf_hex_hash].filepart.root == new_root, 'Update root path fail')
    
    
    def test_getPrintableContents(self):
        """Check that the contents are returned correctly"""
        contents = self.tuflow_model.getPrintableContents()
        
        test_dict = {'c:\\some\\fake\\root\\main.tcf': 
                     ['Read GIS == ..\\madeuppath\\file.shp\n',
                     'OUTPUT FOLDER == ..\\madeuppath\\2d\\\n',
                     'Map Output Data Types == h v q d MB1 ZUK0 ! Output: Levels, Velocities, Unit Flows, Depths, Mass Error & Hazard\n'
                     ]
                     }
        self.assertDictEqual(contents, test_dict, 'Contents dict match fail')
        

    def test_testExists(self):
        """Check the test exists works properly"""
        missing_tcf = ('8707338802f0a1d1c77ffd03d4f661d7', 'file.shp', 'c:\\some\\fake\\root')
        missing_gis = ('aa30168421c3c035ced927454f532b82', 'main.tcf', 'c:\\some\\fake\\root')
        
        missing_files = self.tuflow_model.testExists()
        self.assertTupleEqual(missing_files[0], missing_tcf, 'Missing Tcf fail')
        self.assertTupleEqual(missing_files[1], missing_gis, 'Missing Gis fail')
        
    
    def test_getFilenames(self):
        """Make sure the correct file names are returned
        
        At the moment this is a bit of a catch-all as it deals with the 
        contents() function as well. Probably should check that directly at
        some point to have slighlty finer grained reporting.
        """
        
        # Using default args
        testnames = ['file.shp', 'main.tcf']
        filenames = self.tuflow_model.getFileNames(FilesFilter())
        self.assertListEqual(testnames, filenames, 'filenames check fail')
        
        # Using content types
        testnames = ['file.shp']
        filenames = self.tuflow_model.getFileNames(FilesFilter(content_type=self.tuflow_model.GIS))
        self.assertListEqual(testnames, filenames, 'filenames GIS only check fail')
        
        # Using file types
        testnames = ['file.shp']
        filenames = self.tuflow_model.getFileNames(FilesFilter(modelfile_type=['tcf']))
        self.assertListEqual(testnames, filenames, 'filenames tcf only check fail')
        
        # Using a empty file type
        testnames = []
        filenames = self.tuflow_model.getFileNames(FilesFilter(modelfile_type=['tbc']))
        self.assertListEqual(testnames, filenames, 'filenames empty check fail')
        
        # Using content types and file types
        testnames = ['file.shp']
        filenames = self.tuflow_model.getFileNames(FilesFilter(content_type=self.tuflow_model.GIS, modelfile_type=['tcf']))
        self.assertListEqual(testnames, filenames, 'filenames GIS and tcf only check fail')
        
        
class TuflowModelFileTests(unittest.TestCase):
    """Tests the TuflowModel class"""
    
    def setUp(self):
        """Setup global test values"""
        
        self.tcf_file = TuflowModelFile('tcf', 'b93yey483yrhfheu33')
        
        self.fake_root = 'c:\\some\\fake\\root'
        
        # GIS type
        gfilepath = '..\\madeuppath\\file.shp'
        self.gis_hex_hash = _encodeHash(gfilepath)
        self.tcf_file.addContent(2, self.gis_hex_hash)
        
        # RESULTS type
        dfilepath = '..\\madeuppath\\2d\\results'
        self.result_hex_hash = _encodeHash(dfilepath)
        self.tcf_file.addContent(1, self.result_hex_hash)
        
        # VARIABLE type
        vinput = 'h v q d MB1 ZUK0  ! Output: Levels, Velocities, Unit Flows, Depths, Mass Error & Hazard'
        self.vars_hex_hash = _encodeHash(vinput)
        self.tcf_file.addContent(4, self.vars_hex_hash)
        
    
    def test_addContent(self):
        """Make sure that adding different types of content works.
        
        If this doesn't work it will probably throw an error anyway because the
        setup uses it to make default values.
        
        This test just makes sure it's doing exactly what we think.
        """
        gfilepath = '..\\madeuppath\\file2.mif'
        local_hash = _encodeHash(gfilepath)
        self.tcf_file.addContent(2, local_hash)
        
        self.assertEqual(self.tcf_file.content_order[-1][0], 2, 'Added content hash not found')
        self.assertEqual(self.tcf_file.content_order[-1][1], local_hash, 'Added content hash not found')

        unknown_contents = '''!Probably a comment or something\n
                          \n
                          # Broken over multiple lines\n'
                          \n'''
        
        local_hash = _encodeHash(unknown_contents)
        self.tcf_file.addContent(6, local_hash, unknown_contents)
        
        self.assertEqual(self.tcf_file.content_order[-1][0], 6, 'Added unknown content type not found')
        self.assertEqual(self.tcf_file.content_order[-1][1], local_hash, 'Added unknown content hash not found')
        self.assertEqual(self.tcf_file.content_order[-1][2], unknown_contents, 'Added unknown content details not found')
        
        
    def test_getHashCategory(self):
        """Test access to hash hexes by category"""

        # With no type given
        testlist = ['8707338802f0a1d1c77ffd03d4f661d7',
                    '7e544dd862b6fb14c19bfa2ed41e38d3',
                    '099a63e4d3fa9bbc50ec9c1a006a5ac7']
        hashlist = self.tcf_file.getHashCategory()
        self.assertListEqual(testlist, hashlist, 'No type fail')
        
        # With GIS type given
        testlist = ['8707338802f0a1d1c77ffd03d4f661d7']
        hashlist = self.tcf_file.getHashCategory(2)
        self.assertListEqual(testlist, hashlist, 'GIS type fail')
        
        # With variable type given
        testlist = ['099a63e4d3fa9bbc50ec9c1a006a5ac7']
        hashlist = self.tcf_file.getHashCategory(4)
        self.assertListEqual(testlist, hashlist, 'Variable type fail') 
        

class TuflowTypesTests(unittest.TestCase):
    """
    """
    
    def setUp(self):
        """Setup what we need"""
        self.types = TuflowTypes()
        
    
    def test_defaultValues(self):
        """Check that default values are correct
        
        This is important becuase these are declared separately in both the
        TuflowModel class and TuflowTypes class. It's stupid, but at least the
        tests should pick up if either of them change.
        """
        self.assertTrue(self.types.MODEL == 0, 'Default MODEL value fail')
        self.assertTrue(self.types.RESULT == 1, 'Default RESULT value fail')
        self.assertTrue(self.types.GIS == 2, 'Default GIS value fail')
        self.assertTrue(self.types.DATA == 3, 'Default DATA value fail')
        self.assertTrue(self.types.VARIABLE == 4, 'Default VARIABLE value fail')
        self.assertTrue(self.types.UNKNOWN_FILE == 5, 'Default UNKNOWN_FILE value fail')
        self.assertTrue(self.types.UNKNOWN == 6, 'Default UNKNOWN value fail')
        self.assertTrue(self.types.COMMENT == 7, 'Default COMMENT value fail')
        
    
    def test_find(self):
        """Check that the find function works as expected"""
        
        # With no file type
        self.assertTupleEqual((False, None), self.types.find('Mongoose'), 'Non existent variable fail')
        self.assertTupleEqual((True, 0), self.types.find('GEOMETRY CONTROL FILE'), 'MODEL type variable fail')
        self.assertTupleEqual((True, 0), self.types.find('geometry control file'), 'MODEL type variable fail')
        
        # With file type
        self.assertTupleEqual((False, None), self.types.find('GEOMETRY CONTROL FILE', 2), 'Wrong type variable fail')
        self.assertTupleEqual((True, 3), self.types.find('BC DATABASE', 3), 'Correct type variable fail')
        
        
        