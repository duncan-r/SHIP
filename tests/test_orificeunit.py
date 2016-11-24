# import unittest
# 
# from ship.isis.datunits import orificeunit as ou
# 
# class test_SpillUnit(unittest.TestCase):
#     """
#     """
#     
#     def setUp(self):
#         """
#         """
#         self.data = [
#             'ORIFICE some comments',
#             'OPEN',
#             'orif_u      orif_d',
#             '     1.010     2.010     3.010     4.010     5.010',
#             '     1.000     1.100     0.700',
#         ]
#         
#     
#     def test_readUnitData(self):
#         """Check we can read everything in ok."""
#         test_data = {
#             'comment': 'some comments',
#             'type': 'OPEN',
#             'section_label': 'orif_u',
#             'ds_label': 'orif_d',
#             'invert_level': '1.010',
#             'soffit_level': '2.010',
#             'bore_area': '3.010',
#             'us_sill_level': '4.010',
#             'ds_sill_level': '5.010',
#             'weir_flow': '1.000',
#             'surcharged_flow': '1.100',
#             'modular_limit': '0.700',
#         }
#         orifice = ou.OrificeUnit()
#         fline = orifice.readUnitData(self.data, 0)
#         self.assertDictEqual(orifice.head_data, test_data)
#         
#     
#     def test_getData(self):
#         """Check that the correctly formatted text is being returned."""
#         test_data = [
#             'ORIFICE some comments',
#             'OPEN',
#             'orif_u      orif_d      ',
#             '     1.010     2.010     3.010     4.010     5.010',
#             '     1.000     1.100     0.700',
#         ]
#         orifice = ou.OrificeUnit()
#         orifice.readUnitData(self.data, 0)
#         out = orifice.getData()
#         self.assertListEqual(out, test_data)