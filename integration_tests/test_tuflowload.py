from __future__ import unicode_literals

import os

from ship.utils.fileloaders import fileloader


class TuflowLoadTests(object):
    
    def runTests(self):

        self.loadTuflowModel()
        self.test_controlFileTypes()
        self.test_allFilepaths()
        self.test_variables()
        self.test_files()
        self.test_seVals()
    
    def loadTuflowModel(self):
        print ('Loading tuflow model...')
        path = "integration_tests/test_data/model1/tuflow/runs/test_run1.tcf"
        path = os.path.normpath(os.path.join(os.getcwd(), path))
        loader = fileloader.FileLoader()
        self.tuflow = loader.loadFile(path)
        assert(self.tuflow.missing_model_files == [])
        print ('Tuflow model load complete.')

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
            '2d_zln_shiptest_red_v2_P.shp',
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
            'ECF': 3,
            'TGC': 14,
            'TBC': 2,
        }
        for key, c in self.tuflow.control_files.items():
            print ('Checking model_type: ' + key + '...')
            vars = c.files()
            assert(len(vars) == test_filecounts[key])
        print ('pass')

        print ('Testing no_duplicates=False files count...')
        test_filecounts = {
            'TCF': 14,
            'ECF': 3,
            'TGC': 23,
            'TBC': 4,
        }
        for key, c in self.tuflow.control_files.items():
            print ('Checking model_type: ' + key + '...')
            vars = c.files(no_duplicates=False)
            assert(len(vars) == test_filecounts[key])
        print ('pass')

    
    def test_variables(self):
        print ('Testing no_duplicates=True variables count...')
        test_varcounts = {
            'TCF': 16,
            'ECF': 7,
            'TGC': 6,
            'TBC': 0,
        }
        for key, c in self.tuflow.control_files.items():
            print ('Checking model_type: ' + key + '...')
            vars = c.variables()
            assert(len(vars) == test_varcounts[key])
        print ('pass')

        print ('Testing no_duplciates=False variables count...')
        test_varcounts = {
            'TCF': 18,
            'ECF': 7,
            'TGC': 9,
            'TBC': 0,
        }
        for key, c in self.tuflow.control_files.items():
            print ('Checking model_type: ' + key + '...')
            vars = c.variables(no_duplicates=False)
            assert(len(vars) == test_varcounts[key])
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
                        '2d_zln_shiptest_red_v2_P.shp',
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
            assert(set(test_paths[key]) == set(filepaths))
        print ('pass')
