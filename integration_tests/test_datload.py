from __future__ import unicode_literals

import os
import copy

from ship.utils.fileloaders import fileloader
from ship.utils import filetools as ft
from integration_tests import utils


class DatLoadTests(object):
    
    def runTests(self):
        
        cwd = os.getcwd()
        path = "integration_tests/test_data/model1/fmp/ship_test_v1-1.DAT"
        main_path = os.path.normpath(os.path.join(cwd, path))

        self.loadDatModel(main_path)
        self.test_unitCounts()
        self.test_icsSetup()
        self.test_datWrite()
    
    def loadDatModel(self, path):
        print ('Loading FMP .dat model...')
        loader = fileloader.FileLoader()
        self.dat = loader.loadFile(path)
        print ('FMP model load complete.')
        
    def test_unitCounts(self):

        print ('Test unit counts...')
        assert(len(self.dat.units) == 18)

        headers = self.dat.unitsByType('header')
        comments = self.dat.unitsByType('comment')
        refhs = self.dat.unitsByType('refh')
        rivers = self.dat.unitsByType('river')
        bridges = self.dat.unitsByCategory('bridge')
        junctions = self.dat.unitsByType('junction')
        spills = self.dat.unitsByType('spill')
        htbdys = self.dat.unitsByType('htbdy')
        unknowns = self.dat.unitsByType('unknown')
        ics = self.dat.unitsByType('initial_conditions')
        gis = self.dat.unitsByType('gis_info')
        
        utils.softAssertion(len(headers), 1)
        utils.softAssertion(len(comments), 1)
        utils.softAssertion(len(refhs), 1)
        utils.softAssertion(len(rivers), 6)
        utils.softAssertion(len(bridges), 2)
        utils.softAssertion(len(junctions), 2)
        utils.softAssertion(len(spills), 1)
        utils.softAssertion(len(htbdys), 1)
        utils.softAssertion(len(unknowns), 1)
        utils.softAssertion(len(ics), 1)
        utils.softAssertion(len(gis), 1)
        
        print ('Done')
    
    def test_icsSetup(self):
        print ('Test ics setup...')
        ics = self.dat.unit('initial_conditions')
        utils.softAssertion(len(ics.row_data['main']._collection[0].data_collection), 14)
        print('Done')
        
    
    def test_datWrite(self):
        print ('Test writing DatCollection model...')
        cwd = os.path.join(os.getcwd(), 'integration_tests', 'test_output')
        need_dirs = [cwd,
                     os.path.join(cwd, 'asread'), 
                     os.path.join(cwd, 'asread/model1'),
                     os.path.join(cwd, 'asread/model1/fmp'),
                    ]
        try:
            for n in need_dirs:
                if not os.path.isdir(n):
                    os.mkdir(n)
        except IOError:
            print ('\t Could not make test directeries - aborting test')
            print ('\nFail!\n')
        
        outpath = os.path.join(need_dirs[-1], self.dat.path_holder.filenameAndExtension()) 
        

        # Write the dat file once to start with - use overwrite in case it exists
        self.dat.write(outpath, overwrite=True)

        # Then hopefully this fails without overwrite set to true
        error_raised = False
        try:
            self.dat.write(outpath)
        except IOError:
            error_raised = True
        utils.softAssertion(error_raised, True) 
        
        # Then a final check to make sure overwrite is working
        self.dat.write(outpath, overwrite=True)
        
        print ('Done')
        
        
        
