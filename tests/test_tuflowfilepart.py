from __future__ import unicode_literals

import os
import unittest

from ship.tuflow import tuflowfilepart as tfp
from ship.tuflow.tuflowfilepart import TuflowPart
from ship.tuflow import FILEPART_TYPES as ft
from ship.tuflow import tuflowfactory as f


class TuflowFilePartTests(unittest.TestCase):
    '''Tests TuflowPart's and subclasses.

    Note:
        These test look at the general behaviour of TuflowPart's. Including the
        methods within TuflowPart itself and the main subclasses, like
        ATuflowVariable and TuflowFile.

        Tests within test_tuflowfactor.py provide decent coverage of creating
        new instances of specific TuflowPart's and checking that they have
        been instanciated properly. If you need to add tests to check that
        they have been created properly they should probably go in the factory
        tests.
    '''

    def setUp(self):

        # Setup a main .tcf file
        self.prefix = '/'
        if os.name != 'posix':
            self.prefix = 'c:' + os.sep
        self.fake_root = os.path.join(self.prefix, 'path', 'to', 'fake')
        self.tcf = tfp.ModelFile(None, **{'path': 'tcffile.tcf', 'command': None,
                                          'comment': None, 'model_type': 'TCF',
                                          'root': self.fake_root})

        # Setup a tgc file with tcf parent
        tgc_line = "Geometry Control File == {} ! A tgc comment".format(
            os.path.join('..', 'model', 'tgcfile.tgc')
        )
        self.tgc = f.TuflowFactory.getTuflowPart(tgc_line, self.tcf)[0]

        # Setup a gis file with tgc parent
        gis_line = "Read Gis Z Shape == {} ! A gis comment".format(
            os.path.join('gis', 'gisfile.shp')
        )
        self.gis = f.TuflowFactory.getTuflowPart(gis_line, self.tgc)[0]
        var_line = "Timestep == 2 ! A var comment"
        self.var = f.TuflowFactory.getTuflowPart(var_line, self.tgc)[0]
        gis_line2 = "Read Gis Z Shape == {} ! A gis 2 comment".format(
            os.path.join('gis', 'gisfile2.shp')
        )
        self.gis2 = f.TuflowFactory.getTuflowPart(gis_line2, self.tgc)[0]

        # For the evt testing stuff
        line_evt = "Read Gis Z Shape == {} ! A gis 3 comment".format(
            os.path.join('gis', 'gisfile_evt.shp')
        )
        self.gis_evt = f.TuflowFactory.getTuflowPart(line_evt, self.tgc)[0]
        linevar_evt = "Timestep == 6 ! A var evt comment"
        self.var_evt = f.TuflowFactory.getTuflowPart(linevar_evt, self.tgc)[0]
        # For the scenario testing stuff
        line_scen = "Read Gis Z Shape == {} ! A gis 3 comment".format(
            os.path.join('gis', 'gisfile_evt.shp')
        )
        self.gis_scen = f.TuflowFactory.getTuflowPart(line_scen, self.tgc)[0]
        linevar_scen = "Timestep == 6 ! A var scen comment"
        self.var_scen = f.TuflowFactory.getTuflowPart(linevar_scen, self.tgc)[0]

        if_args = {
            'commands': ['If Scenario', 'Else'], 'terms': [['scen1', 'scen2'], []],
            'comments': ['', '']
        }
        self.iflogic = f.TuflowFactory.createIfLogic(self.tgc, if_args['commands'],
                                                     if_args['terms'],
                                                     if_args['comments'])
        self.iflogic.add_callback = self.fakeCallbackfunc
        self.iflogic.remove_callback = self.fakeCallbackfunc

        evt_args = {
            'commands': 'Define Event', 'terms': ['event1', 'event2'],
            'comments': ''
        }
        self.evtlogic = f.TuflowFactory.createBlockLogic(self.tgc, evt_args['commands'],
                                                         evt_args['terms'],
                                                         evt_args['comments'])
        self.evtlogic.add_callback = self.fakeCallbackfunc
        self.evtlogic.remove_callback = self.fakeCallbackfunc

        self.iflogic.addPart(self.gis, 0)
        self.iflogic.addPart(self.var, 0)
        self.iflogic.addPart(self.gis2, 1)

        # Not needed now as it's done automatically in TuflowLogic.addPart()
#         self.gis.associates.logic = self.iflogic
#         self.var.associates.logic = self.iflogic
#         self.gis2.associates.logic = self.iflogic

    def test_TPallParents(self):
        """Check that it returns parents properly.

        TuflowPart method.
        """
        tgc_parents = self.tgc.allParents([])
        gis_parents = self.gis.allParents([])

        tgc_hashes = [self.tcf.hash]
        for i, t in enumerate(tgc_parents):
            self.assertEqual(t, tgc_hashes[i])

        gis_hashes = [self.tgc.hash, self.tcf.hash]
        for i, t in enumerate(gis_parents):
            self.assertEqual(t, gis_hashes[i])

    def test_TPisInSeVals(self):
        """Check that parts show up with correct scenario/event values.

        TuflowPart method.
        """
        se_vals = {
            'scenario': ['scen1']
        }
        self.assertTrue(self.gis.isInSeVals(se_vals))
        self.assertTrue(self.var.isInSeVals(se_vals))
        self.assertFalse(self.gis2.isInSeVals(se_vals))

        se_vals = {
            'scenario': ['whatever']
        }
        self.assertFalse(self.gis.isInSeVals(se_vals))
        self.assertFalse(self.var.isInSeVals(se_vals))
        self.assertTrue(self.gis2.isInSeVals(se_vals))

    def test_TPresolvePlaceholder(self):
        """Test return value of resolvePlaceholder in TuflowPart."""
        data_line = "Read Materials File == Materials_<<s1>>.tmf ! A tmf comment"
        vardata = f.TuflowFactory.getTuflowPart(data_line, self.tgc)[0]
        var_line = "Cell Size == <<size>> ! a cell size comment"
        varvar = f.TuflowFactory.getTuflowPart(var_line, self.tgc)[0]

        user_vars = {
            's1': 'scen1', 'size': '10', 'e1': 'event1', 'anothervar': '2.5'
        }
        path = vardata.absolutePath(user_vars=user_vars)
        pth = os.path.join(self.prefix, 'path', 'to', 'model', 'Materials_scen1.tmf')
        self.assertEqual(pth, path)
        var = TuflowPart.resolvePlaceholder(varvar.variable, user_vars)
        var2 = varvar.resolvedVariable(user_vars)
        var3 = varvar.resolvePlaceholder(varvar.variable, user_vars=user_vars)
        self.assertEqual(var, '10')
        self.assertEqual(var2, '10')
        self.assertEqual(var3, '10')

    def test_TFabsolutePath(self):
        """Test return value of absolutePath in TuflowFile."""
        path1 = os.path.join(self.prefix, 'path', 'to', 'model', 'tgcfile.tgc')
        path2 = os.path.join(self.prefix, 'path', 'to', 'model', 'gis', 'gisfile.shp')
        self.assertEqual(path1, self.tgc.absolutePath())
        self.assertEqual(path2, self.gis.absolutePath())

    def test_TFabsolutePathAllTypes(self):
        """Test return all types of absolute path in TuflowFile.

        This will return the same as absolutePath if there is only one associated
        file extension. Otherwise it will return one path for each type.
        """
        paths = [
            os.path.join(self.prefix, 'path', 'to', 'model', 'gis', 'gisfile.shp'),
            os.path.join(self.prefix, 'path', 'to', 'model', 'gis', 'gisfile.shx'),
            os.path.join(self.prefix, 'path', 'to', 'model', 'gis', 'gisfile.dbf')]
        self.assertListEqual(paths, self.gis.absolutePathAllTypes())

    def test_TFrelativePath(self):
        """Test return value of relativePaths in TuflowFile."""
        relpath = os.path.join('..', 'model')
        path1 = [relpath]
        path2 = [relpath, 'gis']
        self.assertListEqual(path1, self.tgc.getRelativeRoots([]))
        self.assertListEqual(path2, self.gis.getRelativeRoots([]))

    def test_TLaddPart(self):
        """Test adding a new part to TuflowLogic."""
        self.evtlogic.addPart(self.gis_evt)
        self.assertIn(self.gis_evt, self.evtlogic.group_parts[0])
        self.assertIn(self.gis_evt.hash, self.evtlogic.parts)

        self.iflogic.addPart(self.gis_scen, 1)
        self.assertIn(self.gis_scen, self.iflogic.group_parts[1])
        self.assertIn(self.gis_scen.hash, self.iflogic.parts)

    def test_TLinsertPart(self):
        """Test inserting a new part to TuflowLogic."""
        self.iflogic.insertPart(self.gis_scen, self.gis)
        self.assertIn(self.gis_scen, self.iflogic.group_parts[0])
        self.iflogic.insertPart(self.var_scen, self.gis2)
        self.assertIn(self.var_scen, self.iflogic.group_parts[1])

    def test_removePart(self):
        self.evtlogic.addPart(self.gis_evt)
        self.evtlogic.removePart(self.gis_evt)
        self.assertEqual(len(self.evtlogic.group_parts[0]), 0)
        self.assertEqual(len(self.evtlogic.parts), 0)

    def test_getAllParts(self):
        self.evtlogic.addPart(self.gis_evt)
        parts = self.evtlogic.getAllParts(hash_only=True)
        self.assertEqual(len(parts), 1)
        self.assertEqual(parts[0], self.gis_evt.hash)

        parts = self.iflogic.getAllParts(hash_only=True)
        self.assertEqual(len(parts), 3)
        testp = [self.gis.hash, self.gis2.hash, self.var.hash]
        self.assertEqual(set(parts), set(testp))

    def test_getGroup(self):
        self.evtlogic.addPart(self.gis_evt)
        g1 = self.evtlogic.getGroup(self.gis_evt)
        g2 = self.evtlogic.getGroup(self.gis)
        self.assertEqual(g1, 0)
        self.assertEqual(g2, -1)

        g1 = self.iflogic.getGroup(self.gis)
        g2 = self.iflogic.getGroup(self.gis2)
        self.assertEqual(g1, 0)
        self.assertEqual(g2, 1)

    def test_isInClause(self):
        self.assertTrue(self.iflogic.isInClause(self.gis, 'scen1'))
        self.assertFalse(self.iflogic.isInClause(self.gis2, 'scen1'))

    def test_allTerms(self):
        self.assertListEqual(self.evtlogic.allTerms(), ['event1', 'event2'])
        self.assertListEqual(self.iflogic.allTerms(), ['scen1', 'scen2'])

    def test_isInTerms(self):
        se_vals = {'scenario': ['scen1'],
                   'event': ['event1'],
                   'variable': {}
                   }
        self.assertTrue(self.iflogic.isInTerms(self.gis, se_vals))
        self.assertFalse(self.iflogic.isInTerms(self.gis2, se_vals))
        se_vals = {'scenario': ['scen122'],
                   'event': ['event122'],
                   'variable': {}
                   }
        self.assertFalse(self.iflogic.isInTerms(self.gis, se_vals))
        self.assertTrue(self.iflogic.isInTerms(self.gis2, se_vals))

    def fakeCallbackfunc(self, new_part, old_part):
        """Used to contain the callback functions in the TuflowLogic."""
        pass
