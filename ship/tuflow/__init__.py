from ship.utils import utilfunctions as uf

"""Enum for accessing categories of TuflowFilePart types."""
FILEPART_TYPES = uf.enum('MODEL', 'RESULT', 'GIS', 'DATA', 'VARIABLE', 
                         'UNKNOWN_FILE', 'UNKNOWN', 'COMMENT',
                         'SCENARIO', 'SCENARIO_END', 'EVENT')

