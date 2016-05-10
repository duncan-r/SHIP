from ship.utils import utilfunctions as uf

"""Enum for accessing categories of TuflowFilePart types."""
FILEPART_TYPES = uf.enum('MODEL', 'RESULT', 'GIS', 'DATA', 'VARIABLE', 
                         'UNKNOWN_FILE', 'UNKNOWN', 'COMMENT')


"""Enum for all row data keys used in Isis units"""
# ROW_DATA_TYPES = uf.enum('CHAINAGE', 'ELEVATION', 'ROUGHNESS', 'PANEL_MARKER',
#                          'RPL', 'BANKMARKER', 'EASTING', 'NORTHING', 
#                          'DEACTIVATION', 'SPECIAL', 'EMBANKMENT', 'OPEN_START',
#                          'OPEN_END', 'SPRINGING_LEVEL', 'SOFFIT_LEVEL', 
#                          'CULVERT_INVERT', 'CULVERT_SOFFIT', 'CULVERT_AREA',
#                          'CULVERT_CD_PART', 'CULVERT_CD_FULL', 
#                          'CULVERT_DROWNING') 