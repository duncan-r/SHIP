from __future__ import unicode_literals

import os
import unittest
from ship.fmp.datcollection import DatCollection
from ship.fmp import fmpunitfactory as iuf
from ship.fmp.datunits import riverunit
from ship.fmp.datunits import ROW_DATA_TYPES as rdt
from ship.utils.filetools import PathHolder


class IsisUnitCollectionTest(unittest.TestCase):
    '''Test for the IsisUnitCollection class.
    '''

    def setUp(self):
        '''Set up stuff that will be used throughout the class.
        '''
        self.prefix = '/'
        if os.name != 'posix':
            self.prefix = 'c:' + os.sep
        self.fake_path = os.path.join(self.prefix, 'fake', 'path', 'to', 'datfile.dat')
        self.path_holder = PathHolder(self.fake_path)

        # Setup some data to create units with
        self.riv1_head = {'distance': 10}
        self.riv1_row = {
            'main': [
                {rdt.CHAINAGE: 0.0, rdt.ELEVATION: 20.0, rdt.ROUGHNESS: 0.04},
                {rdt.CHAINAGE: 2.0, rdt.ELEVATION: 10.0, rdt.ROUGHNESS: 0.04},
                {rdt.CHAINAGE: 4.0, rdt.ELEVATION: 10.0, rdt.ROUGHNESS: 0.04},
                {rdt.CHAINAGE: 6.0, rdt.ELEVATION: 10.0, rdt.ROUGHNESS: 0.04},
                {rdt.CHAINAGE: 8.0, rdt.ELEVATION: 20.0, rdt.ROUGHNESS: 0.04},
            ]
        }
        self.riv2_head = {'distance': 12}
        self.riv2_row = {
            'main': [
                {rdt.CHAINAGE: 0.0, rdt.ELEVATION: 20.0, rdt.ROUGHNESS: 0.04},
                {rdt.CHAINAGE: 2.0, rdt.ELEVATION: 10.0, rdt.ROUGHNESS: 0.04},
                {rdt.CHAINAGE: 4.0, rdt.ELEVATION: 10.0, rdt.ROUGHNESS: 0.04},
                {rdt.CHAINAGE: 6.0, rdt.ELEVATION: 10.0, rdt.ROUGHNESS: 0.04},
                {rdt.CHAINAGE: 8.0, rdt.ELEVATION: 20.0, rdt.ROUGHNESS: 0.04},
            ]
        }
        self.riv3_head = {'distance': 14}
        self.riv3_row = {
            'main': [
                {rdt.CHAINAGE: 0.0, rdt.ELEVATION: 20.0, rdt.ROUGHNESS: 0.04},
                {rdt.CHAINAGE: 2.0, rdt.ELEVATION: 10.0, rdt.ROUGHNESS: 0.04},
                {rdt.CHAINAGE: 4.0, rdt.ELEVATION: 10.0, rdt.ROUGHNESS: 0.04},
                {rdt.CHAINAGE: 6.0, rdt.ELEVATION: 10.0, rdt.ROUGHNESS: 0.04},
                {rdt.CHAINAGE: 8.0, rdt.ELEVATION: 20.0, rdt.ROUGHNESS: 0.04},
            ]
        }
        self.brg1_row = {
            'main': [
                {rdt.CHAINAGE: 0.0, rdt.ELEVATION: 20.0},
                {rdt.CHAINAGE: 2.0, rdt.ELEVATION: 10.0},
                {rdt.CHAINAGE: 4.0, rdt.ELEVATION: 10.0},
                {rdt.CHAINAGE: 6.0, rdt.ELEVATION: 20.0},
            ],
            'opening': [
                {rdt.OPEN_START: 0.0, rdt.OPEN_END: 2.0},
                {rdt.OPEN_START: 4.0, rdt.OPEN_END: 6.0}
            ]
        }
        # Create a new IsisUnitCollection object
        self.dat = DatCollection.initialisedDat(self.fake_path)

        self.riv1 = iuf.FmpUnitFactory.createUnit('river', name='riv1',
                                                  head_data=self.riv1_head,
                                                  row_data=self.riv1_row)
        self.riv2 = iuf.FmpUnitFactory.createUnit('river', name='riv2',
                                                  head_data=self.riv2_head,
                                                  row_data=self.riv2_row)
        self.riv3 = iuf.FmpUnitFactory.createUnit('river', name='riv3',
                                                  head_data=self.riv3_head,
                                                  row_data=self.riv3_row)
        self.brg1 = iuf.FmpUnitFactory.createUnit('arch', name='brg1',
                                                  name_ds='brg1ds',
                                                  row_data=self.brg1_row)
        self.brg2 = iuf.FmpUnitFactory.createUnit('arch', name='brg2',
                                                  name_ds='brg2ds',
                                                  row_data=self.brg1_row)
        self.brg3 = iuf.FmpUnitFactory.createUnit('usbpr', name='brg3',
                                                  name_ds='brg3ds',
                                                  row_data=self.brg1_row)

    def test_pathHolder(self):
        """Make sure the PathHolder has been setup properly."""
        p = self.dat.path_holder
        self.assertEqual(p.filename, 'datfile')
        self.assertEqual(p.extension, 'dat')
        self.assertEqual(p.relative_root, None)
        self.assertEqual(p.root, os.path.dirname(self.fake_path))

    def test_initialisedDat(self):
        """Make sure we're creating default setup collections properly."""

        # No units given to setup
        dat = DatCollection.initialisedDat(self.fake_path)
        self.assertTrue(dat[0].UNIT_TYPE == 'header')
        self.assertTrue(dat[1].UNIT_TYPE == 'comment')
        self.assertTrue(dat[2].UNIT_TYPE == 'initial_conditions')

    def test_addUnit(self):
        """Add new units to the collection."""
        self.dat.addUnit(self.riv1, ics={rdt.ELEVATION: 10.0, rdt.FLOW: 3.0})
        self.dat.addUnit(self.riv2)
        self.dat.addUnit(self.riv3)
        self.assertEqual(self.dat.numberOfUnits(), 6)
        rivers = self.dat.unitsByType('river')
        self.assertEqual(len(rivers), 3)

        redherring = {}
        with self.assertRaises(AttributeError):
            self.dat.addUnit(redherring)

        # Make sure initial conditions have been updated
        ic = self.dat.unit('initial_conditions')
        ic_label = ic.row_data['main'].dataObjectAsList(rdt.LABEL)
        ic_elev = ic.row_data['main'].dataObjectAsList(rdt.ELEVATION)
        ic_flow = ic.row_data['main'].dataObjectAsList(rdt.FLOW)
        self.assertListEqual(ic_label, ['riv1', 'riv2', 'riv3'], 'Initial conditions label update error')
        self.assertListEqual(ic_flow, [3.0, 0.0, 0.0], 'Initial conditions flow update error')
        self.assertListEqual(ic_elev, [10.0, 0.0, 0.0], 'Initial conditions elevation update error')

    def test_removeUnit(self):
        """Delete units from the collection."""
        self.dat.addUnit(self.riv1)
        self.dat.addUnit(self.riv2)
        self.dat.addUnit(self.riv3)
        self.assertEqual(self.dat.numberOfUnits(), 6)

        '''
            Do the actual removing
        '''
        # Make sure we can't remove without a type
        with self.assertRaises(AttributeError):
            self.dat.removeUnit('riv2')

        # Remove by unit
        test_unames = ['riv1', 'riv3']
        self.dat.removeUnit(self.riv2)
        self.assertEqual(self.dat.numberOfUnits(), 5)
        rivers = self.dat.unitsByType('river')
        self.assertEqual(len(rivers), 2)
        for r in rivers:
            self.assertIn(r._name, test_unames)
        ic = self.dat.unit('initial_conditions')
        ic_label = ic.row_data['main'].dataObjectAsList(rdt.LABEL)
        self.assertListEqual(ic_label, ['riv1', 'riv3'])

        # Remove by name
        test_unames = ['riv1']
        self.dat.removeUnit('riv3', 'river')
        self.assertEqual(self.dat.numberOfUnits(), 4)
        rivers = self.dat.unitsByType('river')
        self.assertEqual(len(rivers), 1)
        for r in rivers:
            self.assertIn(r._name, test_unames)
        ic = self.dat.unit('initial_conditions')
        ic_label = ic.row_data['main'].dataObjectAsList(rdt.LABEL)
        self.assertListEqual(ic_label, ['riv1'])

    def test_setUnit(self):
        """Replace an existing unit."""
        self.dat.addUnit(self.brg1)
        self.dat.addUnit(self.brg2)

        brg = self.dat.unit('brg1')
        brg.name_ds = 'newname'
        self.dat.setUnit(brg)

    def test_unitsByType(self):
        """Test retrieving units by type."""
        self.dat.addUnit(self.riv1)
        self.dat.addUnit(self.riv2)
        self.dat.addUnit(self.riv3)
        self.dat.addUnit(self.brg1)
        self.dat.addUnit(self.brg2)
        self.assertEqual(self.dat.numberOfUnits(), 8)

        rivers = self.dat.unitsByType('river')
        test_unames = ['riv1', 'riv2', 'riv3']
        for r in rivers:
            self.assertIn(r._name, test_unames)

        brgs = self.dat.unitsByType('arch')
        test_unames = ['brg1', 'brg2']
        for b in brgs:
            self.assertIn(b._name, test_unames)

        brgs2 = self.dat.unitsByType('usbpr')
        brg2_names = ['brg3']
        for b in brgs2:
            self.assertIn(b._name, brg2_names)

        # Multiple types
        mix = self.dat.unitsByType(['river', 'usbpr'])
        mix_names = ['riv1', 'riv2', 'riv3', 'brg3']
        for m in mix:
            self.assertIn(m._name, mix_names)

        # What happens if we give it a category
        cat_brg = self.dat.unitsByType('bridge')
        self.assertEqual(cat_brg, [])

    def test_unitsByCategory(self):
        """Test retrieving units by category."""
        self.dat.addUnit(self.riv1)
        self.dat.addUnit(self.riv2)
        self.dat.addUnit(self.riv3)
        self.dat.addUnit(self.brg1)
        self.dat.addUnit(self.brg2)
        self.assertEqual(self.dat.numberOfUnits(), 8)

        brgs = self.dat.unitsByCategory('bridge')
        test_unames = ['brg1', 'brg2']
        for b in brgs:
            self.assertIn(b._name, test_unames)

        unit_brgs = self.dat.unitsByCategory('arch')
        self.assertEqual(unit_brgs, [])

        mix = self.dat.unitsByCategory(['bridge', 'river'])
        mix_names = ['riv1', 'riv2', 'riv3', 'brg1', 'brg2']
        for m in mix:
            self.assertIn(b._name, mix_names)

    def test_unit(self):
        """Test getting a specific unit."""
        self.dat.addUnit(self.riv1)
        self.dat.addUnit(self.riv2)
        self.dat.addUnit(self.riv3)
        self.dat.addUnit(self.brg1)
        self.dat.addUnit(self.brg2)

        riv = self.dat.unit('riv1')
        self.assertEqual(riv.name, 'riv1')

    def test_linkedUnits(self):
        """Test getting all of the linked units."""
        dat = DatCollection.initialisedDat(self.fake_path)
        riv1 = iuf.FmpUnitFactory.createUnit('river', name='riv1')
        riv2 = iuf.FmpUnitFactory.createUnit('river', name='riv2')
        riv3 = iuf.FmpUnitFactory.createUnit('river', name='riv3')
        riv4 = iuf.FmpUnitFactory.createUnit('river', name='riv4')
        riv5 = iuf.FmpUnitFactory.createUnit('river', name='riv5')
        riv6 = iuf.FmpUnitFactory.createUnit('river', name='riv6')
        riv7 = iuf.FmpUnitFactory.createUnit('river', name='riv7')

        brg1 = iuf.FmpUnitFactory.createUnit('arch', name='brg1_us',
                                             name_ds='brg1_ds')
        brg1.head_data['remote_us'].value = 'riv3'
        brg1.head_data['remote_ds'].value = 'riv4'

        spill1 = iuf.FmpUnitFactory.createUnit('spill', name='spill1_us',
                                               name_ds='spill1_ds')

        junc1 = iuf.FmpUnitFactory.createUnit('junction', name='riv3')
        junc1.head_data['names'].append('brg1_us')
        junc1.head_data['names'].append('spill1_us')
        junc2 = iuf.FmpUnitFactory.createUnit('junction', name='riv4')
        junc2.head_data['names'].append('brg1_ds')
        junc2.head_data['names'].append('spill1_ds')

        dat.addUnit(riv1)
        dat.addUnit(riv2)
        dat.addUnit(riv3)
        dat.addUnit(junc1)
        dat.addUnit(brg1)
        dat.addUnit(spill1)
        dat.addUnit(junc2)
        dat.addUnit(riv4)
        dat.addUnit(riv5)
        dat.addUnit(riv6)
        dat.addUnit(riv7)

        # Check for brg1 which should include everything
        links = dat.linkedUnits(brg1)
        self.assertEqual(links.junctions[0][0], junc1)
        self.assertSetEqual(set(links.junctions[0][1]), set([riv3, spill1, brg1]))
        self.assertEqual(links.junctions[1][0], junc2)
        self.assertSetEqual(set(links.junctions[1][1]), set([riv4, spill1, brg1]))
        self.assertSetEqual(set(links.named_units), set([riv3, riv4]))
        self.assertEqual(links.main_unit, brg1)
        self.assertEqual(links.us_unit, junc1)
        self.assertEqual(links.ds_unit, spill1)

        # Check for riv4 which should only include one junction and named_unit
        links2 = dat.linkedUnits(riv4)
        self.assertEqual(links2.junctions[0][0], junc2)
        self.assertSetEqual(set(links2.junctions[0][1]), set([riv4, spill1, brg1]))
        self.assertSetEqual(set(links2.named_units), set([brg1]))
        self.assertEqual(links2.main_unit, riv4)
        self.assertEqual(links2.us_unit, junc2)
        self.assertEqual(links2.ds_unit, riv5)

        # Check for riv6 which should only have us/ds unit
        links3 = dat.linkedUnits(riv6)
        self.assertEqual(links3.junctions, [])
        self.assertEqual(links3.named_units, [])
        self.assertEqual(links3.main_unit, riv6)
        self.assertEqual(links3.us_unit, riv5)
        self.assertEqual(links3.ds_unit, riv7)
