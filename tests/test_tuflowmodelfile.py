
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
    

class TuflowModelFileTests(unittest.TestCase):
    """Tests the TuflowModel class"""
    
    def setUp(self):
        """Setup global test values"""
        
        self.tuflowmodelfile = TuflowModelFile('tcf', 'b93yey483yrhfheu33', 'b93yey763yrhfheu33')
        self.fake_root = 'c:\\some\\fake\\root'
        
        # MODEL type
        tgcpath = 'c:\\some\\fake\\root\\model.tgc'
        self.tgc_hex_hash = _encodeHash(tgcpath)
        mfileTgc = TuflowFile(1, tgcpath, self.tgc_hex_hash, ft.MODEL, 'READ GEOMETRY FILE', self.fake_root, 'tgc')
        
        # GIS type
        gfilepath = '..\\madeuppath\\file.shp'
        self.gis_hex_hash = _encodeHash(gfilepath)
        gfile = GisFile(1, gfilepath, self.gis_hex_hash, ft.GIS, 'Read GIS', self.fake_root)
        
        gfilepath2 = '..\\madeuppath\\file2.mif'
        self.gis_hex_hash2 = _encodeHash(gfilepath2)
        gfile2 = GisFile(1, gfilepath2, self.gis_hex_hash2, ft.GIS, 'Read GIS', self.fake_root)

        # RESULTS type
        dfilepath = '..\\madeuppath\\2d\\results'
        self.result_hex_hash = _encodeHash(dfilepath)
        dfile = TuflowFile(1, dfilepath, self.result_hex_hash, ft.RESULT, 'OUTPUT FOLDER', self.fake_root)

        # VARIABLE type
        vinput = 'h v q d MB1 ZUK0  ! Output: Levels, Velocities, Unit Flows, Depths, Mass Error & Hazard'
        self.vars_hex_hash = _encodeHash(vinput)
        vfile = ModelVariables(1, vinput, self.vars_hex_hash, ft.VARIABLE, 'Map Output Data Types')
        
        self.tuflowmodelfile.addContent(ft.MODEL, mfileTgc)
        self.tuflowmodelfile.addContent(ft.GIS, gfile)
        self.tuflowmodelfile.addContent(ft.GIS, gfile2)
        self.tuflowmodelfile.addContent(ft.RESULT, dfile)
        self.tuflowmodelfile.addContent(ft.VARIABLE, vfile)
        
    
    def test_addContent(self):
        """Make sure that adding different types of content works.
        
        If this doesn't work it will probably throw an error anyway because the
        setup uses it to make default values.
        
        This test just makes sure it's doing exactly what we think.
        """
        tbcpath = '..\\madeuppath\\file2.mif'
        local_hash = _encodeHash(tbcpath)
        mfileTbc = TuflowFile(11, tbcpath, local_hash, ft.MODEL, 'READ BC FILE', self.fake_root, 'tbc')
        self.tuflowmodelfile.addContent(ft.GIS, mfileTbc)
        
        self.assertEqual(self.tuflowmodelfile.contents[-1][0], 2, 'Added content gis FILEPART_TYPE fail')
        self.assertEqual(self.tuflowmodelfile.contents[-1][1].hex_hash, local_hash, 'Added content gis hash fail')

        unknown_contents = '''!Probably a comment or something\n
                          \n
                          # Broken over multiple lines\n'
                          \n'''
        
        local_hash = _encodeHash(unknown_contents)
        self.tuflowmodelfile.addContent(ft.UNKNOWN, unknown_contents)
        
        self.assertEqual(self.tuflowmodelfile.contents[-1][0], 6, 'Added unknown content type not found')
        self.assertEqual(self.tuflowmodelfile.contents[-1][1], unknown_contents, 'Added unknown content details not found')
        
    
    def test_getEntryByHash(self):
        """Check we get the right entry when searching by hex hash code."""
        
        # TuflowFile instance
        hex = self.tuflowmodelfile.getEntryByHash(self.gis_hex_hash).hex_hash
        self.assertEqual(hex, self.gis_hex_hash, 'Get entry by hash GIS fail: ' + hex)
        # ModelVaraiables instance
        hex = self.tuflowmodelfile.getEntryByHash(self.vars_hex_hash).hex_hash
        self.assertEqual(hex, self.vars_hex_hash, 'Get entry by hash VARIABLE fail: ' + hex)
        
    
    def test_getFiles(self):
        """Check we get the right files based on certain parameters."""
        
        # Default params
        files = self.tuflowmodelfile.getFiles()
        files = [f.hex_hash for f in files]
        testfile_hashes = [self.tgc_hex_hash, self.gis_hex_hash, self.gis_hex_hash2, self.result_hex_hash]
        self.assertListEqual(testfile_hashes, files, 'Default params fail: ' + str(files))
        
        # No result params
        files = self.tuflowmodelfile.getFiles(include_results=False)
        files = [f.hex_hash for f in files]
        testfile_hashes = [self.tgc_hex_hash, self.gis_hex_hash, self.gis_hex_hash2]
        self.assertListEqual(testfile_hashes, files, 'Default params fail: ' + str(files))
        
        # file_type arg
        files = self.tuflowmodelfile.getFiles(file_type=ft.GIS)
        files = [f.hex_hash for f in files]
        testfile_hashes = [self.gis_hex_hash, self.gis_hex_hash2]
        self.assertListEqual(testfile_hashes, files, 'file_type params fail: ' + str(files))
        
        # file_type and extension args
        files = self.tuflowmodelfile.getFiles(file_type=ft.GIS, extensions=['mif'])
        files = [f.hex_hash for f in files]
        testfile_hashes = [self.gis_hex_hash2]
        self.assertListEqual(testfile_hashes, files, 'file_type params fail: ' + str(files))
        
    
    def test_getFileNames(self):
        """Check that we return the right file names."""
        
        # Default params
        names = self.tuflowmodelfile.getFileNames()
        testnames = ['model.tgc', 'file.shp', 'file2.mif', '']
        self.assertListEqual(testnames, names, 'Default params fail: ' + str(names))
        
        # No result
        names = self.tuflowmodelfile.getFileNames(include_results=False)
        testnames = ['model.tgc', 'file.shp', 'file2.mif']
        self.assertListEqual(testnames, names, 'no results params fail: ' + str(names))
        
        # file_type
        names = self.tuflowmodelfile.getFileNames(file_type=ft.GIS)
        testnames = ['file.shp', 'file2.mif']
        self.assertListEqual(testnames, names, 'file_type params fail: ' + str(names))
        
        # Extensions
        names = self.tuflowmodelfile.getFileNames(extensions=['shp'])
        testnames = ['file.shp']
        self.assertListEqual(testnames, names, 'file_type params fail: ' + str(names))
        
        # with_extension
        names = self.tuflowmodelfile.getFileNames(with_extension=False)
        testnames = ['model', 'file', 'file2', '']
        self.assertListEqual(testnames, names, 'with_extension params fail: ' + str(names))
       
        # all_types
        names = self.tuflowmodelfile.getFileNames(all_types=True, extensions=['shp'], include_results=False)
        testnames = ['file.shp', 'file.shx', 'file.dbf', 'file.prj']
        self.assertListEqual(testnames, names, 'with_extension params fail: ' + str(names))
        
    
    def test_getVariables(self):
        """Check that we only get ModelVariables objects."""
        
        vars = self.tuflowmodelfile.getVariables()
        vars = [v.hex_hash for v in vars]
        testvar_hashes = [self.vars_hex_hash]
        self.assertListEqual(testvar_hashes, vars, 'ModelVariables hash match fail: ' + str(vars))
       
       
       
       
       
       
       
       
       