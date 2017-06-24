from __future__ import unicode_literals

from ship.utils import utilfunctions as uf

"""Enum for accessing categories of TuflowFilePart types."""
FILEPART_TYPES = uf.enum('MODEL', 'RESULT', 'GIS', 'DATA', 'VARIABLE',
                         'UNKNOWN_FILE', 'UNKNOWN', 'IF_LOGIC', 'EVENT_LOGIC',
                         'USER_VARIABLE', 'EVENT_VARIABLE', 'MODEL_VARIABLE',
                         'SECTION_LOGIC')
