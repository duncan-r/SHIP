from __future__ import unicode_literals
 
import unittest
from ship.fmp.datcollection import DatCollection
from ship.fmp import isisunitfactory as iuf
from ship.fmp.datunits import riverunit
from ship.fmp.datunits import ROW_DATA_TYPES as rdt
from ship.utils.filetools import PathHolder
 
 
class IsisUnitCollectionTest(unittest.TestCase):
    '''Test for the IsisUnitCollection class.
    '''
      
    def setUp(self):
        '''Set up stuff that will be used throughout the class.
        '''
        self.fake_path = 'c:\\fake\\path\\to\\datfile.dat'
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
        
        self.riv1 = iuf.IsisUnitFactory.createUnit('river', name='riv1', 
                                          head_data=self.riv1_head, 
                                          row_data=self.riv1_row)
        self.riv2 = iuf.IsisUnitFactory.createUnit('river', name='riv2', 
                                          head_data=self.riv2_head, 
                                          row_data=self.riv2_row)
        self.riv3 = iuf.IsisUnitFactory.createUnit('river', name='riv3', 
                                          head_data=self.riv3_head, 
                                          row_data=self.riv3_row)
        self.brg1 = iuf.IsisUnitFactory.createUnit('arch', name='brg1',
                                                       name_ds='brg1ds',
                                                       row_data=self.brg1_row)
        self.brg2 = iuf.IsisUnitFactory.createUnit('arch', name='brg2',
                                                       name_ds='brg2ds',
                                                       row_data=self.brg1_row)
        self.brg3 = iuf.IsisUnitFactory.createUnit('usbpr', name='brg3',
                                                       name_ds='brg3ds',
                                                       row_data=self.brg1_row)
    
    def test_pathHolder(self):
        """Make sure the PathHolder has been setup properly."""
        p = self.dat.path_holder
        self.assertEqual(p.filename, 'datfile')
        self.assertEqual(p.extension, 'dat')
        self.assertEqual(p.relative_root, None)
        self.assertEqual(p.root, 'c:\\fake\\path\\to')
         
 
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
        ic_label = ic.row_data['main'].dataObjAsList(rdt.LABEL)
        ic_elev = ic.row_data['main'].dataObjAsList(rdt.ELEVATION)
        ic_flow = ic.row_data['main'].dataObjAsList(rdt.FLOW)
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
        ic_label = ic.row_data['main'].dataObjAsList(rdt.LABEL)
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
        ic_label = ic.row_data['main'].dataObjAsList(rdt.LABEL)
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
    
    