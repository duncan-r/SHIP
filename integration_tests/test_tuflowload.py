from __future__ import unicode_literals

import os
import copy

from ship.utils.fileloaders import fileloader
from ship.utils import filetools as ft


class TuflowLoadTests(object):

    def runTests(self):

        cwd = os.getcwd()
        path1 = "integration_tests/test_data/model1/tuflow/runs/test_run1.tcf"
        path2 = "integration_tests/test_data/model1/tuflow/runs/test_run_noexist.tcf"
        main_path = os.path.normpath(os.path.join(cwd, path1))
        missing_path = os.path.normpath(os.path.join(cwd, path2))

        self.loadTuflowModel(missing_path)
        self.test_nonExistingControlFiles()
        del self.tuflow

        self.loadTuflowModel(main_path)
        assert(self.tuflow.missing_model_files == [])
#         self.test_deactiveLogic()
        self.test_writeTuflowModel()
        self.test_controlFileTypes()
        self.test_allFilepaths()
        self.test_variables()
        self.test_files()
        self.test_seVals()

    def loadTuflowModel(self, path):
        print ('Loading tuflow model...')
        loader = fileloader.FileLoader()
        self.tuflow = loader.loadFile(path)
        print ('Tuflow model load complete.')

    def test_nonExistingControlFiles(self):
        """Checks that a model still loads and returns the missing files.

        When a TuflowModel is loaded but can't find one or more of the control
        files on disk it should finish the load and set the missing_model_files
        variables to a list with the missing file paths.
        """
        test_files = [
            os.path.normpath(os.path.join(self.tuflow.root, "..\\model\\test_tgc_NOEXIST.tgc")),
            os.path.normpath(os.path.join(self.tuflow.root, "..\\model\\test_tbc_NOEXIST.tbc")),
        ]
        assert(set(self.tuflow.missing_model_files) == set(test_files))

    def test_writeTuflowModel(self):
        """Note this will write the outputs of the tuflow model to disk.

        No comparisons of the data are done here. It's just a convenience so
        that you can check the output files and make sure that they look like
        they should.
        Outputs will be written to SHIP/integration_tests/test_output/asread/
        """
        print ('Test writing tuflow model...')
        cwd = os.path.join(os.getcwd(), 'integration_tests', 'test_output')
        need_dirs = [cwd,
                     os.path.join(cwd, 'asread'),
                     os.path.join(cwd, 'asread/model1'),
                     os.path.join(cwd, 'asread/model1/tuflow'),
                     os.path.join(cwd, 'asread/model1/tuflow/runs'),
                     os.path.join(cwd, 'asread/model1/tuflow/model')
                    ]
        try:
            for n in need_dirs:
                if not os.path.isdir(n):
                    os.mkdir(n)
        except IOError:
            print ('\t Could not make test directeries - aborting test')
            print ('\nFail!\n')
        tuflow = copy.deepcopy(self.tuflow)
        new_root = os.path.normpath(need_dirs[4])       # ending 'runs'
        root_compare = os.path.normpath(need_dirs[3])   # ending 'tuflow'
        tuflow.root = new_root
        contents = {}
        for ckey, cval in tuflow.control_files.items():
            if not ckey in contents.keys():
                contents[ckey] = {}
            temp = cval.getPrintableContents()
            for tkey, tval in temp.items():
#                 print ('root compare: ' + root_compare)
#                 print ('tkey:         ' + tkey)
                assert(root_compare in tkey)
                contents[ckey][tkey] = tval

        for ctype, c in contents.items():
            for pkey, val in c.items():
                ft.writeFile(val, pkey)

        del tuflow
        print ('pass')

    def test_deactiveLogic(self):
        pass
#         print ('Test deactivation logic...')
#         tuflow = copy.deepcopy(self.tuflow)
#         logic = tuflow.control_files['TGC'].logic[1]
#         logic.active = False
#         trd = tuflow.control_files['TGC'].contains(filename="test_trd2")[0]
#         trd.active = False
#         gis = tuflow.control_files['TGC'].contains(filename="whatevs_shiptest_tgc_v1_P")[0]
#         gis.active = False
#         gis2 = tuflow.control_files['TGC'].contains(filename="whatevs_shiptest_tgc_v2_P")[0]
#         gis2.active = False
#         trd2 = tuflow.control_files['TGC'].contains(filename="test_trd1")[0]
#         trd2.active = False
#         trd2 = tuflow.control_files['TGC'].contains(filename="test_trd3")[0]
#         trd2.active = False
#         del tuflow
#         print ('pass')

    def test_controlFileTypes(self):
        print ('Testing control_files keys...')
        ckeys = self.tuflow.control_files.keys()
        test_keys = ['TCF', 'ECF', 'TGC', 'TBC']
        assert(set(ckeys) == set(test_keys))
        print ('pass')

    def test_seVals(self):
        print ('Testing se_vals filepaths keys...')
        se_vals = self.tuflow.user_variables.seValsToDict()
        test_paths = [
            '2d_loc_shiptest_tgc_v1_L.shp',
            '2d_code_shiptest_tgc_v1_R.shp',
            '2d_bc_hx_shiptest_tgc_v1_R.shp',
            '2d_whatevs_shiptest_tgc_v2_P.shp',
            'test_trd1.trd',
            '2d_zln_shiptest_trd_v1_L.shp',
            '2d_zln_shiptest_trd_v1_P.shp',
            'some_zshp_trd_v1_R.shp',
            'summit_event_zln_trd_v2_L.shp',
            'test_trd2.trd',
            '2d_zln_shiptest_trd_v2_L.shp',
            '2d_zln_shiptest_trd_v2_P.shp',
            'shiptest_tgc_v1_DTM_2m.asc',
            '2d_zln_shiptest_tgc_v1_L.shp',
            '2d_zln_shiptest_tgc_v1_P.shp',
            '2d_zpt_shiptest_tgc_v1_R.shp',
            '2d_mat_shiptest_tgc_v1_R.shp'
        ]
        paths = self.tuflow.control_files['TGC'].filepaths(se_vals=se_vals)
        assert(set(test_paths) == set(paths))
        print ('pass')

        print ('Testing se_vals variables count...')
        vars = self.tuflow.control_files['TGC'].variables(se_vals=se_vals)
        assert(len(vars) == 6)
        print ('pass')


    def test_files(self):
        print ('Testing no_duplicates=True files count...')
        test_filecounts = {
            'TCF': 13,
            'ECF': 4,
            'TGC': 14,
            'TBC': 2,
        }
        for key, c in self.tuflow.control_files.items():
            print ('Checking model_type: ' + key + '...')
            vars = c.files()
            assert(len(vars) == test_filecounts[key]), \
                                    "%s variable lengths differ" % key
        print ('pass')

        print ('Testing no_duplicates=False files count...')
        test_filecounts = {
            'TCF': 14,
            'ECF': 4,
            'TGC': 23,
            'TBC': 4,
        }
        for key, c in self.tuflow.control_files.items():
            print ('Checking model_type: ' + key + '...')
            vars = c.files(no_duplicates=False)
            assert(len(vars) == test_filecounts[key]), \
                                    "%s file lengths differ" % key
        print ('pass')


    def test_variables(self):
        print ('Testing no_duplicates=True variables count...')
        test_varcounts = {
            'TCF': 16,
            'ECF': 6,
            'TGC': 6,
            'TBC': 0,
        }
        for key, c in self.tuflow.control_files.items():
            print ('Checking model_type: ' + key + '...')
            vars = c.variables()
            assert(len(vars) == test_varcounts[key]), \
                                    "%s variable lengths differ" % key
        print ('pass')

        print ('Testing no_duplciates=False variables count...')
        test_varcounts = {
            'TCF': 18,
            'ECF': 6,
            'TGC': 9,
            'TBC': 0,
        }
        for key, c in self.tuflow.control_files.items():
            print ('Checking model_type: ' + key + '...')
            vars = c.variables(no_duplicates=False)
            assert(len(vars) == test_varcounts[key]), \
                                    "%s variable lengths differ" % key
        print ('pass')

    def  test_allFilepaths(self):
        print ('Testing all filepaths...')
        test_paths = {
            'TCF':  [
                        'materials_shiptest_v1.csv',
                        '1d_nodes_shiptest_v1_P.shp',
                        '1d_nwk_shiptest_v1_L.shp',
                        '1d_WLL_shiptest_v1_L.shp',
                        'bc_dbase_shiptest_v1.csv',
                        'test_run1.ecf',
                        'test_tgc1.tgc',
                        'test_tbc1.tbc',
                        'test_tbc2.tbc',
                        '2d_oz_ZoneA_shiptest_v1_R.shp',
                        '2d_po_shiptest_v1_L.shp'
                    ],
            'ECF':  [
                        'Projection.prj',
                        'bc_dbase_shiptest_v1.csv'
                    ],
            'TGC':  [
                        '2d_loc_shiptest_tgc_v1_L.shp',
                        '2d_code_shiptest_tgc_v1_R.shp',
                        '2d_bc_hx_shiptest_tgc_v1_R.shp',
                        '2d_whatevs_shiptest_tgc_v1_P.shp',
                        '2d_whatevs_shiptest_tgc_v2_P.shp',
                        'test_trd1.trd',
                        '2d_zln_shiptest_trd_v1_L.shp',
                        '2d_zln_shiptest_trd_v1_P.shp',
                        'some_zshp_trd_v1_R.shp',
                        'some_zshp_trd_v2_R.shp',
                        'summit_event_zln_trd_v1_L.shp',
                        'summit_event_zln_trd_v2_L.shp',
                        'test_trd2.trd',
                        '2d_zln_shiptest_trd_v2_L.shp',
                        '2d_zln_shiptest_trd_v2_P.shp',
                        'test_trd3.trd',
                        '2d_zln_shiptest_trd_v3_L.shp',
                        '2d_zln_shiptest_trd_v3_P.shp',
                        'shiptest_tgc_v1_DTM_2m.asc',
                        '2d_zln_shiptest_tgc_v1_L.shp',
                        '2d_zln_shiptest_tgc_v1_P.shp',
                        '2d_zpt_shiptest_tgc_v1_R.shp',
                        '2d_mat_shiptest_tgc_v1_R.shp'
                    ],
            'TBC':  [
                        '2d_bc_hx_shiptest_tbc_v1_L.shp',
                        '2d_bc_cn_shiptest_tbc_v1_L.shp',
                        '2d_bc_hx_shiptest_tbc_v2_L.shp',
                        '2d_bc_cn_shiptest_tbc_v2_L.shp'
                    ],
        }
        for key, c in self.tuflow.control_files.items():
            filepaths = c.filepaths()
            print ('Checking model_type: ' + key + '...')
            assert(set(test_paths[key]) == set(filepaths)), \
                                    "%s file sets differ" % key
        print ('pass')
