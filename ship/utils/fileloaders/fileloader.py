"""

 Summary:
     Main file loader for the API. This offers convenience methods to make it
     simple to load any type of file from one place.

 Author:
     Duncan Runnacles

 Created:
     01 Apr 2016

 Copyright:
     Duncan Runnacles 2016

 TODO:

 Updates:

"""
from __future__ import unicode_literals

from ship.utils import utilfunctions as uuf
from ship.utils.fileloaders import tuflowloader
from ship.utils.fileloaders import iefloader
from ship.utils.fileloaders import datloader

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class FileLoader(object):
    """
    """

    def __init__(self):
        """
        """
        self._known_files = {'ief': iefloader.IefLoader,
                             'tcf': tuflowloader.TuflowLoader,
                             'dat': datloader.DatLoader,
                             'ied': datloader.DatLoader}

        self.warnings = []


    def loadFile(self, filepath, arg_dict={}):
        """Load a file from disk.

        Args:
            filepath (str): the path to the file to load.
            arg_dict={}(Dict): contains keyword referenced arguments needed by
                any of the loaders. E.g. the TuflowLoader can take some
                scenario values.

        Returns:
            The object created by the individual file loaders. E.g. for .dat
            files this will be an IsisUnitCollection. See the individual
            ALoader implementations for details of return types.

        Raises:
            AttributeError: if the file type is not tcf/dat/ief/ied.

        See Also:
            :class:'ALoader'
            :class:'IefLoader'
            :class:'TuflowLoader'
            :class:'DatLoader'

        """
        ext = uuf.fileExtensionWithoutPeriod(filepath)
        if not ext.lower() in self._known_files:
            logger.error('File type %s is not currently supported for loading' % ext)
            raise AttributeError ('File type %s is not currently supported for loading' % ext)

        loader = self._known_files[ext]()
        contents = loader.loadFile(filepath, arg_dict)
        self.warnings = loader.warnings

        del loader
        return contents











