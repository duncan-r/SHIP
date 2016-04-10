
import os
import unittest
import hashlib

from ship.tuflow import tuflowfilepart as tfp


class TuflowFilePartTests(unittest.TestCase):
    '''Tests the function and setup of the SomeFile object and it's subclasses.
    
    TODO:
        Need to to check for the double file command line in the model files.
        This is where two files are "piped" together on a single line. This has
        not been implemented yet, but should be tested carefully when it is.
    '''
    
    def setUp(self):
        self.fake_root = 'c:\\some\\fake\\root'
        self.fake_parent_relative_root = '..\\model\\'
        self.fake_abs_path = 'c:\\first\\second\\third\\fourth\\somefile.mid'
        self.real_relative_path = '..\\testinputdata\\someplace_v2.0.tgc'
        self.path_with_comment = 'mi\someplace_2d_zln_bridge_v1.0.MIF ! Some comment'
        self.real_command = 'Read MI Z Line RIDGE' 
        self.real_double_file = 'mi\\someplace_2d_bc_ALL_v3.0.MIF | mi\\someplace_2d_zpt_rivers_v2.0.MIF'
        
        self.real_variables = 'h v q d MB1 ZUK0  ! Output: Levels, Velocities, Unit Flows, Depths, Mass Error & Hazard'
        self.real_command_var = 'Map Output Data Types'
        
        self.hex_hash = hashlib.md5(self.fake_abs_path.encode())
        self.hex_hash = self.hex_hash.hexdigest()
        
        
    def test_instance(self):
        sf = tfp.SomeFile(1, 'c:\\madeuppath\\file.mif', self.hex_hash, 3, 'Read GIS')
        self.assertIsInstance(sf, tfp.TuflowFilePart, 'SomeFile is not TuflowFilePartInstance')
        mv = tfp.ModelVariables(1, self.real_variables, self.hex_hash, 4, self.real_command_var)
        self.assertIsInstance(mv, tfp.TuflowFilePart, 'ModelVariables is not TuflowFilePartInstance')
        
        
    def test_object_setup(self):
        '''Check that the constructor loads all of the parameters in properly.
        '''
        sf = tfp.SomeFile(1, self.path_with_comment, self.hex_hash, 3, self.real_command, self.fake_root)
        
        # Check that it works to set up with a comment and relative path
        self.assertEqual(sf.comment, 'Some comment', 'Comment does not match')
        self.assertEqual(sf.relative_root, 'mi', 'relative path does not match')
        self.assertEqual(sf.command, 'Read MI Z Line RIDGE', 'Comment not set properly')
        self.assertEqual(sf.file_name, 'someplace_2d_zln_bridge_v1.0', 'fileName does not match')
        self.assertEqual(sf.extension, 'mif', 'extension does not match')
        self.assertEqual(sf.getRelativePath(), 'mi\someplace_2d_zln_bridge_v1.0.mif', 'relative path does not match')
        self.assertEqual(sf.getFileNameAndExtension(), 'someplace_2d_zln_bridge_v1.0.mif', 'name and extension does not match')
        
        # Check that an absolute path works
        sf = None
        sf = tfp.SomeFile(1, self.fake_abs_path, self.hex_hash, 2, self.real_command)
        self.assertEqual(sf.relative_root, None, 'relative root should be None')
        self.assertEqual(sf.comment, None, 'Comment should be None')
        self.assertEqual(sf.command, 'Read MI Z Line RIDGE', 'command was not set properly')
        self.assertEqual(sf.file_name, 'somefile', 'fileName does not match')
        self.assertEqual(sf.extension, 'mid', 'extension does not match')
        self.assertEqual(sf.getFileNameAndExtension(), 'somefile.mid', 'absolute file name does not match')
        self.assertFalse(sf.getRelativePath(), 'relative path is not None')


    def test_getAbsolutePath(self):
        '''Check that we can retrive the absolute path without problems
        '''
        # Check the absolute path is set and returned correctly
        sf = None
        sf = tfp.SomeFile(1, self.path_with_comment, self.hex_hash, 3, self.real_command, self.fake_root, self.fake_parent_relative_root)
        self.assertEqual(os.path.join(self.fake_root, '..\model\mi\someplace_2d_zln_bridge_v1.0.mif'), sf.getAbsolutePath(), 'abspath does not match')
        
        # Check that the root and relative root are set and combined correctly
        sf = None
        sf = tfp.SomeFile(1, self.real_relative_path, self.hex_hash, 3, self.real_command, self.fake_root, self.fake_parent_relative_root)
        self.assertEqual(os.path.join(self.fake_root, self.fake_parent_relative_root, self.real_relative_path), sf.getAbsolutePath(), 'abspath is not root + relative root')
        

    def test_getRelativePath(self):
        '''Check that we can retrieve the relative path without problems
        '''
        # Check that the relative path is set and returned correctly
        sf = None
        sf = tfp.SomeFile(1, self.real_relative_path, self.hex_hash, 3, self.real_command, self.fake_root)
        self.assertEqual(self.real_relative_path, sf.getRelativePath(), 'relative path does not match')
        
        # Check that setting an absolute path sets the relative path to None
        sf = None
        sf = tfp.SomeFile(1, self.fake_abs_path, self.hex_hash, 3, self.real_command )
        self.assertFalse(sf.getRelativePath(), 'relative path is not False')
        
     
    def test_getNameAndExtension(self):
        '''Check that we can get the file name with the extension without problems
        '''
        sf = None
        sf = tfp.SomeFile(1, self.fake_abs_path, self.hex_hash, 3, self.real_command)
        self.assertEqual('somefile.mid', sf.getFileNameAndExtension(), 'name and extension do not match')
        
        
    def test_setPathsWithAbsolutePaths(self):
        '''Check that the path variables can be set properly with a new absolute path. 
        '''
        # Check path setting works without keeping relative path
        sf = None
        path = 'c:\\some\\random\\path\\with\\file.shp'
        sf = tfp.SomeFile(1, self.real_relative_path, self.hex_hash, 3, self.real_command)
        sf.setPathsWithAbsolutePath(path, False)
        self.assertEqual(path, sf.getAbsolutePath(), 'absolute paths do not match')
        self.assertFalse(sf.getRelativePath(), 'relative path does not match')

        # and with keeping the relative path
        sf = None
        sf = tfp.SomeFile(1, self.real_relative_path, self.hex_hash, 3, self.real_command, self.fake_root, self.fake_parent_relative_root)
        sf.setPathsWithAbsolutePath(path, True)
        self.assertEqual(os.path.join('c:\\some\\random\\path\\with', self.fake_parent_relative_root, '..\\testinputdata', 'file.shp'), sf.getAbsolutePath(), 'absolute paths do not match')
       
        
    def test_setFileName(self):
        '''Check that the fileName is set properly.
        '''
        sf = tfp.SomeFile(1, self.fake_abs_path, self.hex_hash, 3, self.real_command)
        sf.setFileName('newfile')
        self.assertEqual('newfile.mid', sf.getFileNameAndExtension(), 'fileName with no extension not set properly')

        sf = tfp.SomeFile(1, self.fake_abs_path, self.hex_hash, 3, self.real_command)
        sf.setFileName('newfile1.shp', True)
        self.assertEqual('newfile1.mid', sf.getFileNameAndExtension(), 'fileName and removed extension not set properly')
       
        sf.setFileName('newfile2.shp', True, True)
        self.assertEqual('newfile2.shp', sf.getFileNameAndExtension(), 'fileName and extension not set properly')
       
        
    def test_getPathExists(self):
        '''Not sure how to test for this at the moment.
        Could use a path to the test files for it. Need to make sure that any
        links to paths in the test folder will hold when packing into egg
        format.
        '''
        pass
        
    
    def test_getPathExistsAllTypes(self):
        '''See notes for test_getPathExists() function above.
        '''
        pass
    
    
    def test_getPrintableContents(self):
        '''Checks that the SomeFile object returns it's contents in a format
        appropriate for writing to a tuflow model file.
        '''
        sf = tfp.SomeFile(1, self.path_with_comment, self.hex_hash, 3, self.real_command, self.fake_root)
        self.assertEqual('Read MI Z Line RIDGE == mi\someplace_2d_zln_bridge_v1.0.mif ! Some comment', sf.getPrintableContents(), 'printable contents do not match')

        sf = None
        sf = tfp.SomeFile(1, self.fake_abs_path, self.hex_hash, 3, self.real_command)
        p = sf.getPrintableContents()
        #print 'printing p: \n' + p
        self.assertEqual('Read MI Z Line RIDGE == c:\\first\\second\\third\\fourth\\somefile.mid', sf.getPrintableContents(), 'printable contents for absolute path do not match')

        mv = tfp.ModelVariables(1, self.real_variables, self.hex_hash, 3, self.real_command_var)
        self.assertEqual('Map Output Data Types == h v q d MB1 ZUK0 ! Output: Levels, Velocities, Unit Flows, Depths, Mass Error & Hazard', mv.getPrintableContents(), 'printable contents do not match')
       
    def test_gisFile_setup(self):
        '''Check that we create a GisFile instance when given the right file name
        '''
        # Check that mapinfo files get recognised
        gf = tfp.GisFile(1, '..\mi\gisMIfileName.mif', self.hex_hash, 2, self.real_command, self.fake_root)
        self.assertIsInstance(gf, tfp.GisFile, 'Did not create GisFile correctly')
        
        gf = tfp.GisFile(1, '..\mi\gisMIfileName.mid', self.hex_hash, 2, self.real_command, self.fake_root)
        self.assertIsInstance(gf, tfp.GisFile, 'Did not create GisFile correctly')

        gf = tfp.GisFile(1, '..\mi\gisShpfileName.shp', self.hex_hash, 2, self.real_command, self.fake_root)
        self.assertIsInstance(gf, tfp.GisFile, 'Did not create GisFile correctly')
        
        
    def test_dataFile_setup(self):
        '''Check that we create a DataFile instance when given the right file name.
        '''
        # Check that materials files get recognised
        df = tfp.DataFile(1, '..\model\materialsfile.tmf', self.hex_hash, 3,  'Read Materials File', self.fake_root)
        self.assertIsInstance(df, tfp.DataFile, 'Did not create DataFile correctly')
    

    
    '''
        Model variable section
    ''' 
    def test_inputVars(self):
        '''Check that all of the variables in the object have been loaded properly
        '''
        mv = tfp.ModelVariables(1, self.real_variables, self.hex_hash, 4, self.real_command)
        self.assertEqual(mv.comment, 'Output: Levels, Velocities, Unit Flows, Depths, Mass Error & Hazard', 'comment does not match')
        self.assertEqual(mv.raw_var, 'h v q d MB1 ZUK0', 'raw_var does not match')

        split_vars = ['h', 'v', 'q', 'd', 'MB1', 'ZUK0']
        multi_var = mv.multi_var
        self.assertListEqual(split_vars, multi_var, 'list variables are not equal')
              
        
         
        