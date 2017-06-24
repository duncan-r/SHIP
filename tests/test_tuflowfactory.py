from __future__ import unicode_literals

import os
import unittest

from ship.tuflow import tuflowfilepart as tfp
from ship.tuflow.tuflowfilepart import *  # TuflowPart, TuflowVariable, TuflowFile, TuflowKeyValue
from ship.tuflow import FILEPART_TYPES as ft
from ship.tuflow import tuflowfactory as f


class TuflowFilePartTests(unittest.TestCase):
    """Test the setup of TuflowPart's in the tuflowfactory module."""

    def setUp(self):
        """Setup and global variables."""
        self.fake_root = 'c:/path/to/fake/'
        main_file = tfp.ModelFile(None, **{'path': 'tcffile.tcf', 'command': None,
                                           'comment': None, 'model_type': 'TCF',
                                           'root': self.fake_root})
        self.parent = main_file

    def test_getTuflowPart(self):
        """Check that the factory is producing the correct file types."""
        scen_line = "Model Scenarios == scen1 | scen2 | scen3 ! A comment"
        event_line = "Model Events == evt1 | evt2 | evt3 ! A comment"
        uservar_line = "Set Variable myvar == 2.0 ! A comment"
        bcname_line = "BC Event Name == evtname"
        bctext_line = "BC Event Text == evttext"
        bcsource_line = "BC Event Source == evtname | evttext"
        variable_line = "Timestep == 2.5 ! A comment"
        data_line = "Read Materials File == materials.csv"
        output_line = "Output Folder == ..\\results\\"
        check_line = "Write Check Files == ..\\checks\\"
        log_line = "Log Folder == log"
        gis_line = "Read GIS Z Shape == ..\gis\somefile.shp"
        model_line = "Geometry Control File == ..\\model\\tgcfile.tgc"

        self.assertIsInstance(f.TuflowFactory.getTuflowPart(scen_line, self.parent)[0], TuflowModelVariable)
        self.assertIsInstance(f.TuflowFactory.getTuflowPart(event_line, self.parent)[0], TuflowModelVariable)
        self.assertIsInstance(f.TuflowFactory.getTuflowPart(uservar_line, self.parent)[0], TuflowUserVariable)
        self.assertIsInstance(f.TuflowFactory.getTuflowPart(bcname_line, self.parent)[0], TuflowVariable)
        self.assertIsInstance(f.TuflowFactory.getTuflowPart(bctext_line, self.parent)[0], TuflowVariable)
        self.assertIsInstance(f.TuflowFactory.getTuflowPart(bcsource_line, self.parent)[0], TuflowKeyValue)
        self.assertIsInstance(f.TuflowFactory.getTuflowPart(variable_line, self.parent)[0], TuflowVariable)
        self.assertIsInstance(f.TuflowFactory.getTuflowPart(data_line, self.parent)[0], DataFile)
        self.assertIsInstance(f.TuflowFactory.getTuflowPart(output_line, self.parent)[0], ResultFile)
        self.assertIsInstance(f.TuflowFactory.getTuflowPart(check_line, self.parent)[0], ResultFile)
        self.assertIsInstance(f.TuflowFactory.getTuflowPart(log_line, self.parent)[0], ResultFile)
        self.assertIsInstance(f.TuflowFactory.getTuflowPart(gis_line, self.parent)[0], GisFile)
        self.assertIsInstance(f.TuflowFactory.getTuflowPart(model_line, self.parent)[0], ModelFile)

    def test_createModelVariableType(self):
        """Test construction of TuflowModelVariable."""
        line = "Model Scenarios == scen1 | scen2 | scen3 ! A comment"
        scenarios = f.TuflowFactory.createModelVariableType(line, self.parent)
        vtypes = ['scen1', 'scen2', 'scen3']
        vnames = ['s1', 's2', 's3']
        for i, s in enumerate(scenarios):
            self.assertIsInstance(s, TuflowPart)
            self.assertEqual(s._variable_type, 'scenario')
            self.assertEqual(s.obj_type, 'modelvariable')
            self.assertEqual(s.variable_name, vnames[i])
            self.assertEqual(s.variable, vtypes[i])
            self.assertEqual(s.command, 'Model Scenarios')
            self.assertEqual(s.associates.parent.hash, self.parent.hash)

        line = "Model Events == evt1 | evt2 | evt3 ! A comment"
        events = f.TuflowFactory.createModelVariableType(line, self.parent)
        vtypes = ['evt1', 'evt2', 'evt3']
        vnames = ['e1', 'e2', 'e3']
        for i, e in enumerate(events):
            self.assertIsInstance(e, TuflowPart)
            self.assertEqual(e._variable_type, 'event')
            self.assertEqual(e.obj_type, 'modelvariable')
            self.assertEqual(e.variable_name, vnames[i])
            self.assertEqual(e.variable, vtypes[i])
            self.assertEqual(e.command, 'Model Events')
            self.assertEqual(e.associates.parent.hash, self.parent.hash)

    def test_createUserVariableType(self):
        """Test contruction of TuflowUserVariable."""
        line = "Set Variable myvar == 2.0 ! A comment"
        var = f.TuflowFactory.createUserVariableType(line, self.parent)[0]
        self.assertIsInstance(var, TuflowPart)
        self.assertEqual(var.obj_type, 'uservariable')
        self.assertEqual(var.variable_name, 'myvar')
        self.assertEqual(var.variable, '2.0')
        self.assertEqual(var.command, 'Set Variable myvar')
        self.assertEqual(var.associates.parent.hash, self.parent.hash)

    def test_createBcEventVariable(self):
        """Test contruction of a BC event variable."""
        line = "BC Event Name == evtname"
        var = f.TuflowFactory.createBcEventVariable(line, self.parent)[0]
        self.assertIsInstance(var, TuflowPart)
        self.assertIsInstance(var, TuflowVariable)
        self.assertEqual(var.obj_type, 'variable')
        self.assertEqual(var.variable, 'evtname')
        self.assertEqual(var.command, 'BC Event Name')
        self.assertEqual(var.associates.parent.hash, self.parent.hash)

        line = "BC Event Text == evttext"
        var = f.TuflowFactory.createBcEventVariable(line, self.parent)[0]
        self.assertIsInstance(var, TuflowPart)
        self.assertIsInstance(var, TuflowVariable)
        self.assertEqual(var.obj_type, 'variable')
        self.assertEqual(var.variable, 'evttext')
        self.assertEqual(var.command, 'BC Event Text')
        self.assertEqual(var.associates.parent.hash, self.parent.hash)

        line = "BC Event Source == evtname | evttext"
        var = f.TuflowFactory.createBcEventVariable(line, self.parent)[0]
        self.assertIsInstance(var, TuflowPart)
        self.assertIsInstance(var, TuflowKeyValue)
        self.assertEqual(var.obj_type, 'keyvalue')
        self.assertEqual(var.variable, 'evtname | evttext')
        self.assertEqual(var.key, 'evtname')
        self.assertEqual(var.value, 'evttext')
        self.assertEqual(var.command, 'BC Event Source')
        self.assertEqual(var.associates.parent.hash, self.parent.hash)

    def test_createVariableType(self):
        """Test construction of TuflowVariable type."""
        line = "Timestep == 2.5 ! A comment"
        var = f.TuflowFactory.createVariableType(line, self.parent)[0]
        self.assertIsInstance(var, TuflowPart)
        self.assertIsInstance(var, TuflowVariable)
        self.assertEqual(var.obj_type, 'variable')
        self.assertEqual(var.variable, '2.5')
        self.assertEqual(var.split_variable, ['2.5'])
        self.assertEqual(var.command, 'Timestep')
        self.assertEqual(var.associates.parent.hash, self.parent.hash)

    def test_createDataType(self):
        """Test construction of DataFile type."""
        line = "Read Materials File == materials.csv"
        data = f.TuflowFactory.createDataType(line, self.parent)[0]
        self.assertIsInstance(data, TuflowPart)
        self.assertIsInstance(data, TuflowFile)
        self.assertIsInstance(data, DataFile)
        self.assertEqual(data.path_as_read, 'materials.csv')
        self.assertEqual(data.filename, 'materials')
        self.assertEqual(data.extension, 'csv')
        self.assertEqual(data.relative_root, '')
        self.assertEqual(data.root, self.fake_root)
        self.assertEqual(data.filenameAndExtension(), 'materials.csv')

    def test_createResultType(self):
        """Test construction of ResultFile type."""
        line = "Output Folder == ..\\results\\"
        data = f.TuflowFactory.createResultType(line, self.parent)[0]
        self.assertIsInstance(data, TuflowPart)
        self.assertIsInstance(data, TuflowFile)
        self.assertIsInstance(data, ResultFile)
        self.assertEqual(data.obj_type, 'result')
        self.assertEqual(data.filename, '')
        self.assertEqual(data.extension, '')
        self.assertEqual(data.relative_root, '..\\results\\')
        self.assertEqual(data.root, self.fake_root)
        self.assertEqual(data.filenameAndExtension(), '')

        line = "Write Check Files == ..\\checks\\"
        data = f.TuflowFactory.createResultType(line, self.parent)[0]
        self.assertIsInstance(data, TuflowPart)
        self.assertIsInstance(data, TuflowFile)
        self.assertIsInstance(data, ResultFile)
        self.assertEqual(data.obj_type, 'result')
        self.assertEqual(data.filename, '')
        self.assertEqual(data.extension, '')
        self.assertEqual(data.relative_root, '..\\checks\\')
        self.assertEqual(data.root, self.fake_root)
        self.assertEqual(data.filenameAndExtension(), '')
#         self.assertTrue(data.filename_is_prefix)

        line = "Log Folder == log"
        data = f.TuflowFactory.createResultType(line, self.parent)[0]
        self.assertIsInstance(data, TuflowPart)
        self.assertIsInstance(data, TuflowFile)
        self.assertIsInstance(data, ResultFile)
        self.assertEqual(data.obj_type, 'result')
        self.assertEqual(data.filename, '')
        self.assertEqual(data.extension, '')
        self.assertEqual(data.relative_root, 'log\\')
        self.assertEqual(data.root, self.fake_root)
        self.assertEqual(data.filenameAndExtension(), '')

    def test_createGisType(self):
        """Test construction of GisFile type."""
        line = "Read GIS Z Shape == ..\gis\somefile.shp"
        data = f.TuflowFactory.createGisType(line, self.parent)[0]
        self.assertIsInstance(data, TuflowPart)
        self.assertIsInstance(data, TuflowFile)
        self.assertIsInstance(data, GisFile)
        self.assertEqual(data.filename, 'somefile')
        self.assertEqual(data.extension, 'shp')
        self.assertEqual(data.relative_root, '..\gis')
        self.assertEqual(data.root, self.fake_root)
        self.assertEqual(data.filenameAndExtension(), 'somefile.shp')
        self.assertEqual(data.gis_type, 'shp')
        self.assertTupleEqual(('shp', 'shx', 'dbf'), data.all_types)

        line = "Read GIS Z Shape == ..\gis\somefile.mif"
        data = f.TuflowFactory.createGisType(line, self.parent)[0]
        self.assertIsInstance(data, TuflowPart)
        self.assertIsInstance(data, TuflowFile)
        self.assertIsInstance(data, GisFile)
        self.assertEqual(data.filename, 'somefile')
        self.assertEqual(data.extension, 'mif')
        self.assertEqual(data.relative_root, '..\gis')
        self.assertEqual(data.root, self.fake_root)
        self.assertEqual(data.filenameAndExtension(), 'somefile.mif')
        self.assertEqual(data.gis_type, 'mi')
        self.assertTupleEqual(('mif', 'mid'), data.all_types)

        line = "Read GIS Z Shape == ..\gis\somefile"
        data = f.TuflowFactory.createGisType(line, self.parent, test='mif')[0]
        self.assertIsInstance(data, TuflowPart)
        self.assertIsInstance(data, TuflowFile)
        self.assertIsInstance(data, GisFile)
        self.assertEqual(data.filename, 'somefile')
        self.assertEqual(data.extension, 'mif')
        self.assertEqual(data.relative_root, '..\gis')
        self.assertEqual(data.root, self.fake_root)
        self.assertEqual(data.filenameAndExtension(), 'somefile.mif')
        self.assertEqual(data.gis_type, 'mi')
        self.assertTupleEqual(('mif', 'mid'), data.all_types)

    def test_createModelType(self):
        """Test construction of ModelFile type."""
        line = "Geometry Control File == ..\\model\\tgcfile.tgc"
        data = f.TuflowFactory.createModelType(line, self.parent, model_type='TGC')[0]
        self.assertIsInstance(data, TuflowPart)
        self.assertIsInstance(data, TuflowFile)
        self.assertIsInstance(data, ModelFile)
        self.assertEqual(data.obj_type, 'model')
        self.assertEqual(data.filename, 'tgcfile')
        self.assertEqual(data.extension, 'tgc')
        self.assertEqual(data.relative_root, '..\model')
        self.assertEqual(data.root, self.fake_root)
        self.assertEqual(data.filenameAndExtension(), 'tgcfile.tgc')
        self.assertEqual(data.model_type, 'TGC')

    def test_createGisTypeWithPipes(self):
        line = "Read GIS Z Shape == gis\somefile_R.shp | gis\\somefile_L.shp | gis\\somefile_P.shp"
        data = f.TuflowFactory.createGisType(line, self.parent)
        self.assertEqual(len(data), 3)

        names = ['somefile_R', 'somefile_L', 'somefile_P']
        for i, d in enumerate(data):
            self.assertIsInstance(d, TuflowPart)
            self.assertIsInstance(d, TuflowFile)
            self.assertIsInstance(d, GisFile)
            self.assertEqual(d.filename, names[i])
            self.assertEqual(d.extension, 'shp')
            self.assertEqual(d.relative_root, 'gis')
            self.assertEqual(d.root, self.fake_root)
            self.assertEqual(d.filenameAndExtension(), names[i] + '.shp')
            self.assertEqual(d.gis_type, 'shp')
            self.assertTupleEqual(('shp', 'shx', 'dbf'), d.all_types)

            if i > 0:
                self.assertEqual(d.associates.sibling_prev.filename, data[i - 1].filename)
            if i < 2:
                self.assertEqual(d.associates.sibling_next.filename, data[i + 1].filename)

    def test_partsFromPipedFiles(self):
        """Check partsFromPipedFiles."""
#         line = "Read GIS Z Shape == gis\somefile_R.shp | gis\\somefile_L.shp | gis\\somefile_P.shp"
        vars = {}
        vars['path'] = "gis\somefile_R.shp | gis\\somefile_L.shp | gis\\somefile_P.shp"
        vars['command'] = 'Read GIS Z Shape'
        vars['comment'] = ''
        vars['root'] = self.fake_root
        parts = f.partsFromPipedFiles(GisFile, self.parent, **vars)
        self.assertEqual(len(parts), 3)

        names = ['somefile_R', 'somefile_L', 'somefile_P']
        for i, d in enumerate(parts):
            self.assertIsInstance(d, TuflowPart)
            self.assertIsInstance(d, TuflowFile)
            self.assertIsInstance(d, GisFile)
            self.assertEqual(d.filename, names[i])
            self.assertEqual(d.extension, 'shp')
            self.assertEqual(d.relative_root, 'gis')
            self.assertEqual(d.root, self.fake_root)
            self.assertEqual(d.filenameAndExtension(), names[i] + '.shp')
            self.assertEqual(d.gis_type, 'shp')
            self.assertTupleEqual(('shp', 'shx', 'dbf'), d.all_types)

            if i > 0:
                self.assertEqual(d.associates.sibling_prev.filename, parts[i - 1].filename)
            if i < 2:
                self.assertEqual(d.associates.sibling_next.filename, parts[i + 1].filename)

    def test_assignSiblings(self):
        """Check that sibling assignments are correct."""
        line1 = "Read GIS Z Shape == gis\somefile_R.shp"
        line2 = "Read GIS Z Shape == gis\\somefile_L.shp"
        line3 = "Read GIS Z Shape == gis\\somefile_P.shp"
        gis1 = f.TuflowFactory.createGisType(line1, self.parent)[0]
        gis2 = f.TuflowFactory.createGisType(line2, self.parent)[0]
        gis3 = f.TuflowFactory.createGisType(line3, self.parent)[0]

        f.assignSiblings([gis1, gis2, gis3])
        self.assertEqual(gis1.hash, gis2.associates.sibling_prev.hash)
        self.assertEqual(gis2.hash, gis3.associates.sibling_prev.hash)
        self.assertEqual(gis2.hash, gis1.associates.sibling_next.hash)
        self.assertEqual(gis3.hash, gis2.associates.sibling_next.hash)
        self.assertIsNone(gis1.associates.sibling_prev)
        self.assertIsNone(gis3.associates.sibling_next)

    def test_checkEstryAuto(self):
        """Check that Estry Auto commands are properly dealt with."""
        line1 = "Estry Control File Auto ! A comment"
        line2 = "Estry Control File == Auto"

        out1, found1 = f.checkEstryAuto(line1, self.parent)
        out2, found2 = f.checkEstryAuto(line2, self.parent)
        correct_line = 'Estry Control File == ' + self.parent.filename + '.ecf'

        self.assertEqual(out1, correct_line)
        self.assertTrue(found1)
        self.assertEqual(out2, correct_line)
        self.assertTrue(found2)

    def test_takeParentType(self):
        """Check that control file types are found properly."""
        p1 = 'somefile.tcf'
        p2 = 'somefile.ecf'
        p3 = 'somefile.tgc'
        p4 = 'somefile.tbc'
        p5 = 'somefile.tef'
        self.assertFalse(f.takeParentType(p1))
        self.assertFalse(f.takeParentType(p2))
        self.assertFalse(f.takeParentType(p3))
        self.assertFalse(f.takeParentType(p4))
        self.assertFalse(f.takeParentType(p5))

    def test_breakLine(self):
        """Check that we can separate a tuflow command line properly."""
        line = "Read GIS Z Shape == somefile.shp ! With a comment"
        line2 = "Read GIS Z Shape == somefile.shp"

        cmd, inst = f.breakLine(line)
        cmd2, inst2 = f.breakLine(line2)

        self.assertEqual(cmd, "Read GIS Z Shape")
        self.assertEqual(cmd2, "Read GIS Z Shape")
        self.assertEqual(inst, "somefile.shp ! With a comment")
        self.assertEqual(inst2, "somefile.shp")

    def test_separateComment(self):
        """Check we can separate out comments properly."""
        line = "somefile.shp ! With a comment"
        line2 = "somefile.shp"

        inst, comment, cchar = f.separateComment(line)
        inst2, comment2, cchar2 = f.separateComment(line2)

        self.assertEqual(inst, 'somefile.shp')
        self.assertEqual(comment, 'With a comment')
        self.assertEqual(cchar, '!')
        self.assertEqual(inst2, 'somefile.shp')
        self.assertEqual(comment2, '')
        self.assertEqual(cchar2, '')

    def test_resolveResult_ResultAndLog(self):
        """Check that we can set up a ResultFile path properly.

        Test the resolveResult function with Output Folder, and Log commands.
        """

        result_vars = {
            'command': 'Output Folder', 'comment': '', 'path': '..\\results',
            'root': self.fake_root
        }
        rpart = ResultFile(self.parent, **result_vars)
        rpart = f.resolveResult(rpart)
        result_vars2 = {
            'command': 'Output Folder', 'comment': '', 'path': '..\\results\\',
            'root': self.fake_root
        }
        rpart2 = ResultFile(self.parent, **result_vars2)
        rpart2 = f.resolveResult(rpart2)
        result_vars3 = {
            'command': 'Output Folder', 'comment': '', 'path': 'c:\\path\\to\\results\\',
            'root': self.fake_root
        }
        rpart3 = ResultFile(self.parent, **result_vars3)
        rpart3 = f.resolveResult(rpart3)

        log_vars = {
            'command': 'Log Folder', 'comment': '', 'path': 'log',
            'root': self.fake_root
        }
        lpart = ResultFile(self.parent, **log_vars)
        lpart = f.resolveResult(lpart)
        log_vars2 = {
            'command': 'Log Folder', 'comment': '', 'path': 'log\\',
            'root': self.fake_root
        }
        lpart2 = ResultFile(self.parent, **log_vars2)
        lpart2 = f.resolveResult(lpart2)
        log_vars3 = {
            'command': 'Log Folder', 'comment': '', 'path': 'c:\\path\\to\\log',
            'root': self.fake_root
        }
        lpart3 = ResultFile(self.parent, **log_vars3)
        lpart3 = f.resolveResult(lpart3)

        self.assertEqual(rpart.result_type, 'output')
        self.assertEqual(rpart2.result_type, 'output')
        self.assertEqual(rpart3.result_type, 'output')
        self.assertEqual(lpart.result_type, 'log')
        self.assertEqual(lpart2.result_type, 'log')
        self.assertEqual(lpart3.result_type, 'log')

        self.assertEqual(rpart.filename, '')
        self.assertEqual(rpart2.filename, '')
        self.assertEqual(rpart3.filename, '')
        self.assertEqual(lpart.filename, '')
        self.assertEqual(lpart2.filename, '')
        self.assertEqual(lpart3.filename, '')

        self.assertEqual(rpart.relative_root, '..\\results\\')
        self.assertEqual(rpart2.relative_root, '..\\results\\')
        self.assertEqual(rpart3.relative_root, '')
        self.assertEqual(lpart.relative_root, 'log\\')
        self.assertEqual(lpart2.relative_root, 'log\\')
        self.assertEqual(lpart3.relative_root, '')

        self.assertFalse(rpart.filename_is_prefix)
        self.assertFalse(rpart2.filename_is_prefix)
        self.assertFalse(rpart3.filename_is_prefix)
        self.assertFalse(lpart.filename_is_prefix)
        self.assertFalse(lpart2.filename_is_prefix)
        self.assertFalse(lpart3.filename_is_prefix)

    def test_resolveResult_Check(self):
        """Check that we can set up a ResultFile path properly.

        Test the resolveResult function with Write Check Files command.
        """
        check_vars = {
            'command': 'Write Check Files', 'comment': '', 'path': '..\\check',
            'root': self.fake_root
        }
        cpart = ResultFile(self.parent, **check_vars)
        cpart = f.resolveResult(cpart)
        check_vars2 = {
            'command': 'Write Check Files', 'comment': '', 'path': '..\\check\\',
            'root': self.fake_root
        }
        cpart2 = ResultFile(self.parent, **check_vars2)
        cpart2 = f.resolveResult(cpart2)
        check_vars3 = {
            'command': 'Write Check Files', 'comment': '', 'path': 'c:\\path\\to\\check',
            'root': self.fake_root
        }
        cpart3 = ResultFile(self.parent, **check_vars3)
        cpart3 = f.resolveResult(cpart3)
        check_vars4 = {
            'command': 'Write Check Files', 'comment': '', 'path': 'c:\\path\\to\\check\\',
            'root': self.fake_root
        }
        cpart4 = ResultFile(self.parent, **check_vars4)
        cpart4 = f.resolveResult(cpart4)

        self.assertEqual(cpart.result_type, 'check')
        self.assertEqual(cpart2.result_type, 'check')
        self.assertEqual(cpart3.result_type, 'check')
        self.assertEqual(cpart4.result_type, 'check')

        self.assertEqual(cpart.filename, 'check')
        self.assertEqual(cpart2.filename, '')
        self.assertEqual(cpart3.filename, 'check')
        self.assertEqual(cpart4.filename, '')

        self.assertEqual(cpart.relative_root, '..\\')
        self.assertEqual(cpart2.relative_root, '..\\check\\')
        self.assertEqual(cpart3.relative_root, '')
        self.assertEqual(cpart4.relative_root, '')

        self.assertTrue(cpart.filename_is_prefix)
        self.assertFalse(cpart2.filename_is_prefix)
        self.assertTrue(cpart3.filename_is_prefix)
        self.assertFalse(cpart4.filename_is_prefix)
