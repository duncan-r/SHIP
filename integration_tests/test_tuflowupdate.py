from __future__ import unicode_literals

import os
import copy

from ship.utils.fileloaders import fileloader
from ship.tuflow import tuflowfactory as factory
from integration_tests import utils

class TestError(ValueError):
    pass


class TuflowUpdateTests(object):

    def runTests(self):
        self.loadTuflowModel()
        self.test_changeActiveStatus()
        self.test_addPartToPartHolder()
        self.test_removePartFromPartHolder()
        self.test_addPartToLogicHolder()
        self.test_removePartFromLogicHolder()


    def loadTuflowModel(self):
        print ('Loading tuflow model...')
        path = "integration_tests/test_data/model1/tuflow/runs/test_run1.tcf"
        path = os.path.normpath(os.path.join(os.getcwd(), path))
        loader = fileloader.FileLoader()
        self.tuflow = loader.loadFile(path)
        utils.softAssertion(self.tuflow.missing_model_files, [])
        print ('Tuflow model load complete.')

    def test_changeActiveStatus(self):
        print ('Testing update active status...')
        tuflow = copy.deepcopy(self.tuflow)
        control = tuflow.control_files['TGC']

        # Make sure we know what it is before
        zpt_part = control.contains(command="Set Zpts", variable="2",
                                    parent_filename="test_trd2")
        zln_part = control.contains(command="Z Line THIN", filename="zln_shiptest_trd_v2")
        parts = zpt_part + zln_part
        utils.softAssertion(len(parts), 3)

        trd = control.contains(filename="test_trd2")[0]
        trd.active = False

        # Then check after
        zpt_part = control.contains(command="Set Zpts", variable="2",
                                    parent_filename="test_trd2")
        zln_part = control.contains(command="Z Line THIN", filename="zln_shiptest_trd_v2")
        parts = zpt_part + zln_part
        utils.softAssertion(len(parts), 0)

        print ('Done')

    def test_addPartToPartHolder(self):
        print ('Testing add part to PartHolder...')
#         tuflow = copy.deepcopy(self.tuflow)
        tuflow = self.tuflow
        control = tuflow.control_files['TGC']
        tgc = None
        for c in control.control_files:
            if c.filename == 'test_tgc1': tgc = c

        line = "Timestep == 12 ! timestep 12 comment"
        varpart = factory.getTuflowPart(line, tgc)[0]
        line2 = "Timestep == 22 ! timestep 22 comment"
        varpart2 = factory.getTuflowPart(line2, tgc)[0]
        existing_part = control.contains(filename='test_trd2')[0]
        control.parts.add(varpart, after=existing_part)
        control.parts.add(varpart2, before=existing_part)

        line3 = "Timestep == 32 ! timestep 23 comment"
        varpart3 = factory.getTuflowPart(line3, existing_part)[0]
        control.parts.add(varpart3)

        found = False
        for i, p in enumerate(control.parts):
            if p == existing_part:
                found = True
                utils.softAssertion(control.parts[i+1], varpart)
                utils.softAssertion(control.parts[i+1].associates.logic, existing_part.associates.logic)
                utils.softAssertion(control.parts[i-1], varpart2)
                utils.softAssertion(control.parts[i-1].associates.logic, existing_part.associates.logic)
        if not found:
            raise TestError('Failed to add part to PartHolder')


        utils.softAssertion(control.parts[-1] ,varpart3, False)
        utils.softAssertion(varpart3.associates.parent ,tgc, False)

        trd_index = control.parts.lastIndexOfParent(varpart3.associates.parent)
        utils.softAssertion(control.parts[trd_index], varpart3)

        print ('Done')

    def test_removePartFromPartHolder(self):
        print ('Testing remove part to LogicHolder...')

#         tuflow = copy.deepcopy(self.tuflow)
        tuflow = self.tuflow
        control = tuflow.control_files['TGC']

        part1 = control.contains(command='Timestep', variable='12')[0]
        part2 = control.contains(command='Timestep', variable='22')[0]
        part3 = control.contains(command='Timestep', variable='32')[0]
        control.parts.remove(part1)
        control.parts.remove(part2)
        control.parts.remove(part3)

        index = control.parts.index(part1)
        index2 = control.parts.index(part2)
        index3 = control.parts.index(part3)
        utils.softAssertion(index, -1)
        utils.softAssertion(index2, -1)
        utils.softAssertion(index3, -1)

        print ('Done')


    def test_addPartToLogicHolder(self):
        print ('Testing add part to LogicHolder...')

#         tuflow = copy.deepcopy(self.tuflow)
        tuflow = self.tuflow
        control = tuflow.control_files['TGC']
        tgc = None
        for c in control.control_files:
            if c.filename == 'test_tgc1': tgc = c

        part1 = control.contains(filename='whatevs_shiptest_tgc_v1_P')[0]
        logic1 = part1.associates.logic

        line = "Timestep == 12 ! timestep 12 comment"
        varpart = factory.getTuflowPart(line, tgc)[0]
        logic1.insertPart(varpart, part1)

        utils.softAssertion(varpart.associates.logic, part1.associates.logic)

        part1_index = control.parts.index(part1)
        utils.softAssertion(control.parts.index(varpart), part1_index + 1)

        print ('Done')


    def test_removePartFromLogicHolder(self):
        print ('Testing remove part to LogicHolder...')

#         tuflow = copy.deepcopy(self.tuflow)
        tuflow = self.tuflow
        control = tuflow.control_files['TGC']
        tgc = None
        for c in control.control_files:
            if c.filename == 'test_tgc1': tgc = c

        part1 = control.contains(command='Timestep', variable='12')[0]
        logic1 = part1.associates.logic
        group = logic1.getGroup(part1)

        logic1.removePart(part1)

        part1_index = control.parts.index(part1)

        last_part = logic1.group_parts[-1][-1]
        last_index = control.parts.index(last_part)
        utils.softAssertion(logic1.getGroup(part1), -1)
        utils.softAssertion(part1.associates.logic ,logic1, False)
        utils.softAssertion(control.parts[last_index + 1], part1)

        print ('Done')




