
import os
import unittest

from ship.utils.filetools import PathHolder
from ship.utils import filetools


class PathHolderTests(unittest.TestCase):
    '''Tests the function and setup of the PathHolder object. 
    
    '''
    
    def setUp(self):
        self.fake_root = 'c:\\some\\fake\\root'
        self.fake_abs_path = 'c:\\first\\second\\third\\fourth\\somefile.txt'
        self.fake_relative_path = '..\\relative\\somefile.txt'
        self.no_relative_path = '..\\relative'
        self.path_with_comment = 'relative\\file.txt ! Some comment'
        
        
    def test_setupVars(self):
        '''Test the _setupVars method.
        This protected method is called by the constructor when a new file path
        is handed to the newly created object. It should then set everything up
        for later access.
        '''        
        # Check that it loads an absolute path properly
        ph = PathHolder(self.fake_abs_path)
        self.assertEqual('c:\\first\\second\\third\\fourth', ph.root, 'roots do not match')
        self.assertEqual('somefile', ph.file_name, 'filenames do not match')
        self.assertEqual('txt', ph.extension, 'extensions do not match')
        self.assertIsNone(ph.relative_root, 'relative root should be None')
        
        # Check that it loads a relative path properly
        ph = PathHolder(self.fake_relative_path)
        self.assertEqual('..\\relative', ph.relative_root, 'relative roots do not match')
        self.assertEqual('somefile', ph.file_name, 'filenames do not match')
        self.assertEqual('txt', ph.extension, 'extensions do not match')
        self.assertIsNone(ph.root, 'root should be None')
        
        
    def test_getFinalFolder(self):
        '''Check that it does actually return the final folder in the stack
        '''
        ph = PathHolder(self.fake_abs_path)
        self.assertEqual('fourth', ph.getFinalFolder(), 'final folder is not correct')
        
        ph = PathHolder(self.fake_relative_path)
        self.assertEqual('relative', ph.getFinalFolder(), 'final folder is not correct')

        
    def test_setFinalFolder(self):
        '''Check that the new final folder is set properly.
        '''
        ph = PathHolder(self.fake_abs_path)
        ph.setFinalFolder('fifth')
        self.assertEqual('c:\\first\\second\\third\\fifth', ph.root, 'set absolute final folder fail')
        
        ph = PathHolder(self.fake_relative_path)
        ph.setFinalFolder('fifth')
        self.assertEqual('..\\fifth', ph.relative_root, 'set relative final folder fail')
        
    
    def test_getAbsolutePath(self):
        '''Test that the absolute path is returned correctly.
        '''
        ph = PathHolder(self.fake_abs_path)
        abs_path = ph.getAbsolutePath()
        self.assertEqual(self.fake_abs_path, abs_path, 'getAbsolutePath() fail')
        
        ph = PathHolder(self.fake_relative_path)
        self.assertFalse(ph.getAbsolutePath(), 'getAbsolutePath() with relative root does not return False')
        
        ph = PathHolder(self.fake_relative_path, self.fake_root)
        q = ph.getAbsolutePath()
        self.assertEqual('c:\\some\\fake\\root\\..\\relative\\somefile.txt', ph.getAbsolutePath(), 'getAbsolutePath() with root and relative root fail')
        
        
    def test_getDirectory(self):
        '''Check that the function returns the directory properly.
        '''
        pass
        
        
        