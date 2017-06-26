from __future__ import unicode_literals

import os
import copy

from ship.utils.fileloaders import fileloader
from ship.tuflow import tuflowfactory as factory
from ship.utils.fileloaders.tuflowloader import TuflowLoader
from integration_tests import utils


class UpdateTcfModelFile(object):

    def runTests(self):
        self.loadTuflowModel()
        self.test_addTcfModelFile()
        self.test_replaceTcfModelFile()
        self.test_removeTcfModelFile()


    def loadTuflowModel(self):
        print ('Loading tuflow model...')
        path = "integration_tests/test_data/model1/tuflow/runs/test_run1.tcf"
        path = os.path.normpath(os.path.join(os.getcwd(), path))
        loader = fileloader.FileLoader()
        self.tuflow = loader.loadFile(path)
        utils.softAssertion(self.tuflow.missing_model_files, [])
        print ('Tuflow model load complete.')

    def test_addTcfModelFile(self):
        """Check that we can add a new file to the TCF properly.

        Involves adding the part to the TCF ControlFile, loading the contents
        of the actual control file on disk, and putting the contents in the
        corrent location.
        """
        print ('Testing add tcf ModelFile...')

        tuflow = copy.deepcopy(self.tuflow)
        loader = TuflowLoader()
        tcf = tuflow.control_files['TCF']
        geom = tcf.contains(command='Geometry Control')[0]

        line = "Geometry Control File == ..\\model\\test_tgc2.tgc"
        tgc_part = factory.getTuflowPart(line, tcf.mainfile)[0]
        tgc_control = loader.loadControlFile(tgc_part)
        tcf.addControlFile(tgc_part, tgc_control, after=geom)

        utils.softAssertionIn(tgc_part, tuflow.control_files['TGC'].control_files)

        test_part = tuflow.control_files['TGC'].contains(filename='shiptest_tgc2_v1_DTM_2m')
        utils.softAssertion(len(test_part), 1)

        index = tcf.parts.index(tgc_part)
        utils.softAssertion(index, tcf.parts.index(geom) + 1)
        del tuflow

        print ('Done')

    def test_removeTcfModelFile(self):
        print ('Testing delete tcf ModelFile...')

        tuflow = copy.deepcopy(self.tuflow)
        loader = TuflowLoader()
        tcf = tuflow.control_files['TCF']
        geom = tcf.contains(command='Geometry Control')[0]

        tcf.removeControlFile(geom)

        utils.softAssertion(len(tuflow.control_files['TGC'].parts.parts), 0)
        utils.softAssertion(len(tuflow.control_files['TGC'].control_files), 0)
        utils.softAssertion(len(tuflow.control_files['TGC'].logic.parts), 0)

        print ('Done')


    def test_replaceTcfModelFile(self):
        print ('Testing replace tcf ModelFile...')

        tuflow = copy.deepcopy(self.tuflow)
        loader = TuflowLoader()
        tcf = tuflow.control_files['TCF']
        geom = tcf.contains(command='Geometry Control')[0]

        line = "Geometry Control File == ..\\model\\test_tgc2.tgc"
        tgc_part = factory.getTuflowPart(line, tcf.mainfile)[0]
        tgc_control = loader.loadControlFile(tgc_part)

        tcf.replaceControlFile(tgc_part, tgc_control, geom)

        utils.softAssertionIn(geom, tuflow.control_files['TGC'].control_files, False)
        utils.softAssertionIn(tgc_part, tuflow.control_files['TGC'].control_files)

        print ('Done')

