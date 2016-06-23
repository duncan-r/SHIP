
import os
import unittest
import hashlib

from ship.tuflow.tuflowmodel import *
from ship.tuflow.tuflowmodelfile import *
from ship.tuflow.tuflowfilepart import *
from ship.tuflow import FILEPART_TYPES as ft


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
        self.mfileTcf = ModelFile(1, tcfpath, self.tcf_hex_hash, ft.MODEL, 'tcf', 'tcf', 
                                   root=self.fake_root, category='tcf', tmf_hash=self.tcf_hex_hash)
        self.tuflowmodelfile = TuflowModelFile('tcf', self.mfileTcf.hex_hash, None, 'main.tcf')

        tgcpath = 'c:\\some\\fake\\root\\model.tgc'
        self.tgc_hex_hash = _encodeHash(tgcpath)
        mfileTgc = TuflowFile(1, tgcpath, self.tgc_hex_hash, ft.MODEL, 'READ GEOMETRY FILE', 
                              'tgc', root=self.fake_root, category='tgc')
        
        # GIS type
        gfilepath = '..\\madeuppath\\file.shp'
        self.gis_hex_hash = _encodeHash(gfilepath)
        gfile = GisFile(1, gfilepath, self.gis_hex_hash, ft.GIS, 'Read GIS', 'tcf', 
                        root=self.fake_root)

        # RESULTS type
        dfilepath = '..\\madeuppath\\2d\\results'
        self.result_hex_hash = _encodeHash(dfilepath)
        dfile = TuflowFile(1, dfilepath, self.result_hex_hash, ft.RESULT, 'OUTPUT FOLDER', 'tcf', root=self.fake_root)

        # VARIABLE type
        vinput = 'h v q d MB1 ZUK0  ! Output: Levels, Velocities, Unit Flows, Depths, Mass Error & Hazard'
        self.vars_hex_hash = _encodeHash(vinput)
        vfile = ModelVariables(1, vinput, self.vars_hex_hash, ft.VARIABLE, 'Map Output Data Types', 'tcf')
        
        self.tuflowmodelfile.addContent(ft.MODEL, mfileTgc)
        self.tuflowmodelfile.addContent(ft.GIS, gfile)
        self.tuflowmodelfile.addContent(ft.RESULT, dfile)
        self.tuflowmodelfile.addContent(ft.VARIABLE, vfile)
        self.tuflow_model.files['tcf'][self.tcf_hex_hash] = self.tuflowmodelfile
        self.tuflow_model.model_order.addRef(ModelRef(self.tcf_hex_hash, 'tcf'), True)
        self.tuflow_model.mainfile = self.mfileTcf

    
    def test_defaultValues(self):
        """Check that default values are correct"""
        self.assertTrue(self.tuflow_model.has_estry_auto == False, 'Default COMMENT value fail')
        
    
    def test_changeRoot(self):
        """Ensure that the file path root is properly updated."""
        new_root = r'c:\new\path\testroot'
        self.tuflow_model.changeRoot(new_root)
        
        for c in self.tuflow_model.files['tcf']['aa30168421c3c035ced927454f532b82'].contents:
            if not isinstance(c[1], ModelVariables):
                self.assertTrue(c[1].root == new_root, 'Update root path fail')
            
        
    def test_getPrintableContents(self):
        """Check that the contents are returned correctly"""
        contents = self.tuflow_model.getPrintableContents()
        
        test_dict = {'c:\\some\\fake\\root\\main.tcf': 
                        ['READ GEOMETRY FILE == c:\\some\\fake\\root\\model.tgc', 
                         'Read GIS == ..\\madeuppath\\file.shp', 'OUTPUT FOLDER == ..\\madeuppath\\2d\\', 
                         'Map Output Data Types == h v q d MB1 ZUK0 ! Output: Levels, Velocities, Unit Flows, Depths, Mass Error & Hazard'
                        ]
                    }
        self.assertDictEqual(contents, test_dict, 'Contents dict match fail: \n' + str(contents))
        

    def test_testExists(self):
        """Check the test exists works properly"""
        missing_tgc = ['model.tgc', 'c:\\some\\fake\\root\\model.tgc']
        missing_gis = ['file.shp', 'c:\\some\\fake\\madeuppath\\file.shp']
        
        missing_files = self.tuflow_model.testExists()
        self.assertListEqual(missing_files[0], missing_tgc, 'Missing Tgc fail: ' + str(missing_files[0]))
        self.assertListEqual(missing_files[1], missing_gis, 'Missing Gis fail: ' + str(missing_files[1]))
        
    
    def test_getFilenames(self):
        """Make sure the correct file names are returned
        
        At the moment this is a bit of a catch-all as it deals with the 
        contents() function as well. Probably should check that directly at
        some point to have slighlty finer grained reporting.
        """
        
        # Using default args
        testnames = ['model.tgc', 'file.shp']
        filenames = self.tuflow_model.getFilePaths(name_only=True, include_results=False)
        self.assertListEqual(testnames, filenames, 'filenames check fail: ' + str(filenames))
        
        # Using content types
        testnames = ['file.shp']
        filenames = self.tuflow_model.getFilePaths(file_type=ft.GIS, name_only=True)
        self.assertListEqual(testnames, filenames, 'filenames GIS only check fail: ' + str(filenames))
    
    
    def test_getModelFiles(self):
        """Check that we get all of the TuflowFile ft.MODEL objects."""
        
        model_files = self.tuflow_model.getModelFiles()
        tcf_hex = model_files['tcf'][0].hex_hash
        tgc_hex = model_files['tgc'][0].hex_hash
        self.assertEqual(len(model_files['tcf']), 1, 'tcf length fail: Length = ' + str(len(model_files['tcf'])))
        self.assertEqual(len(model_files['ecf']), 0, 'ecf length fail: Length = ' + str(len(model_files['ecf'])))
        self.assertEqual(len(model_files['tgc']), 1, 'tgc length fail: Length = ' + str(len(model_files['tgc'])))
        self.assertEqual(len(model_files['tbc']), 0, 'tbc length fail: Length = ' + str(len(model_files['tbc'])))
        self.assertEqual(tcf_hex, self.tcf_hex_hash, 'getModelFiles tcf hex fail: ' + tcf_hex)
        self.assertEqual(tgc_hex, self.tgc_hex_hash, 'getModelFiles tgc hex fail: ' + tgc_hex)
        
    
    def test_getTMFFromTuflowFile(self):
        """Check we get the right TuflowModelFile from a TuflowFile."""
        
        model = self.tuflow_model.getTMFFromTuflowFile(self.mfileTcf)
        test_hex = self.tuflowmodelfile.hex_hash
        self.assertEqual(model.hex_hash, test_hex, 'getTMF hash fail: ' + model.hex_hash)
        

#     def test_getTuflowFileFromTMF(self):
#         """Check we get the right TuflowFile from a TuflowModelFile."""
#         
#         model = self.tuflow_model.getTuflowFileFromTMF(self.tuflowmodelfile)
#         test_hex = self.mfileTcf.hex_hash
#         self.assertEqual(model.hex_hash, test_hex, 'getTuflowFile hash fail: ' + model.hex_hash)
        


class TuflowTypesTests(unittest.TestCase):
    """
    """
    
    def setUp(self):
        """Setup what we need"""
        self.types = TuflowTypes()
        
    
    def test_find(self):
        """Check that the find function works as expected"""
        
        # With no file type
        self.assertTupleEqual((False, None), self.types.find('Mongoose'), 'Non existent variable fail')
        self.assertTupleEqual((True, 0), self.types.find('GEOMETRY CONTROL FILE'), 'MODEL type variable fail')
        self.assertTupleEqual((True, 0), self.types.find('geometry control file'), 'MODEL type variable fail')
        
        # With file type
        self.assertTupleEqual((False, None), self.types.find('GEOMETRY CONTROL FILE', 2), 'Wrong type variable fail')
        self.assertTupleEqual((True, 3), self.types.find('BC DATABASE', 3), 'Correct type variable fail')
        
        
        