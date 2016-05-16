import os
import hashlib
import unittest

from ship.utils.fileloaders.tuflowloader import TuflowLoader
from ship.tuflow.tuflowfilepart import TuflowFile


class TuflowModelLoaderTests(unittest.TestCase):
    """Tests the functions in the TuflowModelLoader class."""
    
    def setUp(self):
        '''Set up global test values
        '''
        self.fake_tcf_path = 'c:\user\model\runs\testtcf.tcf'
        self.file_dets = TuflowLoader._FileDetails(self.fake_tcf_path, True)
        self.loader = TuflowLoader()
        
        
    def test_extractExtension(self):
        """Check we can break up lines properly"""
        
        instruction = '..\model\bc_dbase\bc_dbase_TuflowFile.csv ! ydatabase that relates the names of boundary conditions within MapInfo tables to their data (eg hydrographs)'
        self.assertEqual('csv', self.loader.extractExtension(instruction))
    
    
    def test_breakLine(self):
        """Check that we can disect a file line properly"""
        
        gis_line = r'Read MI Network == ..\model\mi\1d_nwk_TuflowFile2.MIF ! 1d network file.'
        results_line = r'Output Folder == ..\Results\1d\Somefolder\Somefolder2\ ! destination of 1d results files'
        data_line = r'BC Database == ..\model\bc_dbase\bc_dbase_TuflowFile.csv ! ydatabase that relates the names of boundary conditions within MapInfo tables to their data (eg hydrographs)'
        variable_line = r'End Time == 20   ! simulation end time (hours)'
        model_line = r'Geometry Control File == ..\model\Some_tgc_v1-0.tgc ! reference to the geometry control file for this simulation'
    
        gis_tuple = ('Read MI Network', r'..\model\mi\1d_nwk_TuflowFile2.MIF ! 1d network file.')
        self.assertTupleEqual(gis_tuple, self.loader._breakLine(gis_line), 'GIS object fail')

        results_tuple = ('Output Folder', r'..\Results\1d\Somefolder\Somefolder2\ ! destination of 1d results files')
        self.assertTupleEqual(results_tuple, self.loader._breakLine(results_line), 'Results object fail')

        data_tuple = ('BC Database', r'..\model\bc_dbase\bc_dbase_TuflowFile.csv ! ydatabase that relates the names of boundary conditions within MapInfo tables to their data (eg hydrographs)')
        self.assertTupleEqual(data_tuple, self.loader._breakLine(data_line), 'Data object fail')

        variable_tuple = ('End Time', r'20   ! simulation end time (hours)')
        self.assertTupleEqual(variable_tuple, self.loader._breakLine(variable_line), 'Variable object fail')

        model_tuple = ('Geometry Control File', r'..\model\Some_tgc_v1-0.tgc ! reference to the geometry control file for this simulation')
        self.assertTupleEqual(model_tuple, self.loader._breakLine(model_line), 'Model file object fail')

        
    def test_breakAuto(self): 
        """Check on ESTRY == Auto fix"""
        
        auto_line = 'ESTRY Control File Auto !looks for an .ecf file with the same name as the .tcf file'
        filename = r'c:\made\up\path\runs\main.tcf'
        output_line = 'ESTRY Control File == c:\\made\\up\\path\\runs\\main.ecf !looks for an .ecf file with the same name as the .tcf file'
        self.assertEqual(output_line, self.loader._breakAuto(auto_line, filename), 'Estry Auto fail')
        
        auto_line = 'ESTRY Control File == Auto !looks for an .ecf file with the same name as the .tcf file'
        filename = r'c:\made\up\path\runs\main.tcf'
        output_line = 'ESTRY Control File == c:\\made\\up\\path\\runs\\main.ecf !looks for an .ecf file with the same name as the .tcf file'
        self.assertEqual(output_line, self.loader._breakAuto(auto_line, filename), 'Estry Auto fail')
    
    
    def test_checkForPipes(self):
        """Check that piped filenames are found properly."""
        
        instruction_single = r'Some command == ..\file_1.mif # Some comment goes here'
        instruction_double = r'Some command == ..\file_1.mif | ..\file_2.mif # Some comment goes here'
        instruction_triple = r'Some command == ..\file_1.mif | ..\file_2.mif | ..\file_3.mif # Some comment goes here'
        instruction_nocomment = r'Some command == ..\file_1.mif'
        
        file_d = TuflowLoader._FileDetails([r'c:\some\fake\path\tofile.mif', None, None, ''] , gen_hash=True)
        hex_hash = file_d.generateHash('random string from creating a hash code')
        
        test_1 = ['Some command == ..\\file_1.mif # Some comment goes here']
        self.assertListEqual(test_1, self.loader.checkForPipes(instruction_single, file_d, hex_hash)[0], 'Pipes test_single fail')
        
        test_2 = ['Some command == ..\\file_1.mif ', ' ..\\file_2.mif # Some comment goes here']
        self.assertListEqual(test_2, self.loader.checkForPipes(instruction_double, file_d, hex_hash)[0], 'Pipes test_double fail')
        
        test_3 = ['Some command == ..\\file_1.mif ', ' ..\\file_2.mif ', ' ..\\file_3.mif # Some comment goes here']
        self.assertListEqual(test_3, self.loader.checkForPipes(instruction_triple, file_d, hex_hash)[0], 'Pipes test_triple fail')

        test_4 = ['Some command == ..\\file_1.mif']
        self.assertListEqual(test_4, self.loader.checkForPipes(instruction_nocomment, file_d, hex_hash)[0], 'Pipes test_nocomment fail')

    
    def test_commentSplit(self):
        """Check that comment is correctly split from the rest of the file line."""
        
        instruction_comment = r'Some command == ..\file_1.mif # Some comment goes here'
        instruction_nocomment = r'Some command == ..\file_1.mif'
        
        test_1 = (True, ['Some command == ..\\file_1.mif ', ' Some comment goes here'], '#')
        com_1 = self.loader.separateComment(instruction_comment)
        self.assertEqual(test_1, self.loader.separateComment(instruction_comment))
    
        test_2 = (False, ['Some command == ..\\file_1.mif'], '')
        com_2 = self.loader.separateComment(instruction_nocomment)
        self.assertEqual(test_2, self.loader.separateComment(instruction_nocomment))
    
    
    def test_resolveResult(self):
        """Check that result file commands can be correctly identified and setup."""
        # Result as folder only
        result_path = 'S:\\007\\tuflow\\results\\2d\\calibration\\'
        hex_hash = hashlib.md5(result_path.encode())
        hex_hash = hex_hash.hexdigest()
        result_file = TuflowFile(0, result_path, hex_hash, 1, 'Output Folder')
        output = self.loader._resolveResult(result_file)
        
        self.assertEqual(output.root, 'S:\\007\\tuflow\\results\\2d\\calibration\\', 'Result root no filename equal fail.')
        self.assertEqual(output.file_name, '', 'Result no filename file_name equal fail.')
        self.assertEqual(output.relative_root, '', 'Result no filename relative_root equal fail.')
        self.assertEqual(output.parent_relative_root, '', 'Result no filename parent_relative_root equal fail.')
        
        # Result relative path
        result_path = '..\\results\\2d\\calibration\\'
        hex_hash = hashlib.md5(result_path.encode())
        hex_hash = hex_hash.hexdigest()
        result_file = TuflowFile(0, result_path, hex_hash, 1, 'Output Folder')
        output = self.loader._resolveResult(result_file)
        
        self.assertEqual(output.root, '', 'Result relative root no filename equal fail.')
        self.assertEqual(output.file_name, '', 'Result relative no filename file_name equal fail.')
        self.assertEqual(output.relative_root, '..\\results\\2d\\calibration\\', 'Result relative filename relative_root equal fail.')
        self.assertEqual(output.parent_relative_root, '', 'Result relative parent_relative_root equal fail.')

        # Check folder setup with prefix
        check_path_prefix = 'S:\\007\\tuflow\\checks\\2d\\calibration'
        hex_hash = hashlib.md5(result_path.encode())
        hex_hash = hex_hash.hexdigest()
        check_file_prefix = TuflowFile(0, check_path_prefix, hex_hash, 1, 'WRITE CHECK FILES')
        output_check_prefix = self.loader._resolveResult(check_file_prefix)
        
        self.assertEqual(output_check_prefix.root, 'S:\\007\\tuflow\\checks\\2d\\', 'Check prefix root equal fail.')
        self.assertEqual(output_check_prefix.file_name, 'calibration', 'Check prefix file_name equal fail.')
        self.assertEqual(output_check_prefix.relative_root, '', 'Check prefix relative_root equal fail.')
        self.assertEqual(output_check_prefix.parent_relative_root, '', 'Check prefix parent_relative_root equal fail.')
        self.assertTrue(output_check_prefix.file_name_is_prefix)

        # Check folder setup with no prefix
        check_path = 'S:\\007\\tuflow\\checks\\2d\\'
        hex_hash = hashlib.md5(result_path.encode())
        hex_hash = hex_hash.hexdigest()
        check_file = TuflowFile(0, check_path, hex_hash, 1, 'WRITE CHECK FILES')
        output_check = self.loader._resolveResult(check_file)
        
        self.assertEqual(output_check.root, 'S:\\007\\tuflow\\checks\\2d\\', 'Check root equal fail.')
        self.assertEqual(output_check.file_name, '', 'Check file_name equal fail.')
        self.assertEqual(output_check.relative_root, '', 'Check relative_root equal fail.')
        self.assertEqual(output_check.parent_relative_root, '', 'Check parent_relative_root equal fail.')
        self.assertFalse(output_check.file_name_is_prefix)
    
    
    def test_breakScenario(self):
        """Check that we can correctly identify and break up a scenario line."""
        
        hash_text = 'Some random test for creating a hash'
        hex_hash = hashlib.md5(hash_text)
        hex_hash = hex_hash.hexdigest()
        
        # Test an opening if
        line = 'IF SCENARIO == SCEN01 | SCEN11'
        return_type, scenario = self.loader.breakScenario(line, hex_hash, 0)
        self.assertEqual(return_type, 'IF', 'IF scenario return type fail: ' + str(return_type))
        self.assertListEqual(scenario.values, ['SCEN01', 'SCEN11'])
        
        # Test an if else
        line = 'ELSE IF SCENARIO == SCEN01 | SCEN11'
        return_type, scenario = self.loader.breakScenario(line, hex_hash, 0)
        self.assertEqual(return_type, 'ELSE', 'ELSE scenario return type fail: ' + str(return_type))
        self.assertListEqual(scenario.values, ['SCEN01', 'SCEN11'])
        
        # Test an end
        line = 'END IF'
        return_type, scenario = self.loader.breakScenario(line, hex_hash, 0)
        self.assertEqual(return_type, 'END', 'END scenario return type fail: ' + str(return_type))
        self.assertEqual(scenario, None, 'END scenario None fail')
        
    
    
    
    
    
    