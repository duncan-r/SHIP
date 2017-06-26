from __future__ import unicode_literals

import os
import unittest

from ship.utils.filetools import PathHolder
from ship.utils import filetools

class PathHolderTests(unittest.TestCase):
    '''Tests the function and setup of the PathHolder object.

    '''

    def setUp(self):
        self.prefix = '/'
        if os.name != 'posix':
            self.prefix = 'c:' + os.sep

        self.fake_root = os.path.join(self.prefix, 'some', 'fake', 'root')
        self.fake_abs_path = os.path.join(
            self.prefix, 'first', 'second', 'third', 'fourth', 'TuflowFile.txt')
        self.fake_relative_path = os.path.join('..', 'relative', 'TuflowFile.txt')
        self.no_relative_path = os.path.join('..', 'relative')
        self.path_with_comment = os.path.join('relative', 'file.txt') + ' ! Some comment'

    def test_setupVars(self):
        '''Test the _setupVars method.
        This protected method is called by the constructor when a new file path
        is handed to the newly created object. It should then set everything up
        for later access.
        '''
        # Check that it loads an absolute path properly
        ph = PathHolder(self.fake_abs_path)
        pth = os.path.join(self.prefix, 'first', 'second', 'third', 'fourth' )
        self.assertEqual(pth, ph.root, 'roots do not match')
        self.assertEqual('TuflowFile', ph.filename, 'filenames do not match')
        self.assertEqual('txt', ph.extension, 'extensions do not match')
        self.assertIsNone(ph.relative_root, 'relative root should be None')

        # Check that it loads a relative path properly
        ph = PathHolder(self.fake_relative_path)
        self.assertEqual(os.path.join('..', 'relative'), ph.relative_root, 'relative roots do not match')
        self.assertEqual('TuflowFile', ph.filename, 'filenames do not match')
        self.assertEqual('txt', ph.extension, 'extensions do not match')
        self.assertIsNone(ph.root, 'root should be None')

    def test_finalFolder(self):
        '''Check that it does actually return the final folder in the stack
        '''
        ph = PathHolder(self.fake_abs_path)
        self.assertEqual('fourth', ph.finalFolder(), 'final folder is not correct')

        ph = PathHolder(self.fake_relative_path)
        self.assertEqual('relative', ph.finalFolder(), 'final folder is not correct')

    def test_setFinalFolder(self):
        '''Check that the new final folder is set properly.
        '''
        ph = PathHolder(self.fake_abs_path)
        ph.setFinalFolder('fifth')
        pth = os.path.join(self.prefix, 'first', 'second', 'third', 'fifth')
        self.assertEqual(pth, ph.root, 'set absolute final folder fail')

        ph = PathHolder(self.fake_relative_path)
        ph.setFinalFolder('fifth')
        self.assertEqual(os.path.join('..', 'fifth'), ph.relative_root, 'set relative final folder fail')

    def test_absolutePath(self):
        '''Test that the absolute path is returned correctly.
        '''
        ph = PathHolder(self.fake_abs_path)
        abs_path = ph.absolutePath()
        self.assertEqual(self.fake_abs_path, abs_path, 'absolutePath() fail')

        ph = PathHolder(self.fake_relative_path)
        self.assertFalse(ph.absolutePath(), 'absolutePath() with relative root does not return False')

        ph = PathHolder(self.fake_relative_path, self.fake_root)
        q = ph.absolutePath()
        pth = os.path.join(self.prefix, 'some', 'fake', 'root', 'TuflowFile.txt')
        self.assertEqual(pth, ph.absolutePath(), 'absolutePath() with root and relative root fail')

    def test_getDirectory(self):
        '''Check that the function returns the directory properly.
        '''
        pass
