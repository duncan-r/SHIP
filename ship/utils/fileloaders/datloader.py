"""

 Summary:
    Factory class for building the AUnits from an ISIS data file.
    This is used to read and build the parts of the ISIS dat file.

 Author:
     Duncan Runnacles

  Created:
     01 Apr 2016

 Copyright:
     Duncan Runnacles 2016

 TODO:
    There are a few functions in here that should be made protected. This
    doesn't really make much difference in Python in terms of encapsulation,
    but it makes it a bit clearer to any calling scripts that they might be
    messing with something that they probablly shouldn't be messing with.

    Comments are a bit over the top in this file. Need to go through and
    decide what is helpful and what is just getting in the way.

 Updates:

"""
from __future__ import unicode_literals

import os

from ship.utils.atool import ATool
from ship.utils.fileloaders.loader import ALoader
from ship.utils import filetools as ftools
from ship.fmp.fmpunitfactory import FmpUnitFactory
from ship.utils import utilfunctions as uf
from ship.fmp.datunits.isisunit import UnknownUnit
from ship.fmp.datcollection import DatCollection

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class DatLoader(ATool, ALoader):
    """
    Isis data file (.DAT) I/O methods.

    Factory for creating the .DAT file objects.
    Identifies different section of the .DAT file and creates objects of
    the different units. Also saves updated file.

    All unknown data within the file is contained within UnkownSection units.
    These read in the text as found and write out as found, with no knowledge
    of the contents. Effectively bypassing the need to worry about parts that
    aren't being used yet.
    """

    def __init__(self):
        """Constructor."""

        ATool.__init__(self)
        ALoader.__init__(self)
        logger.debug('Instantiating DatLoader')

        self.cur_no_of_units = 0
        self.contents = []          # Contents of dat file
        self.temp_unit = None       # AUnit
        self.is_ied = False         # If used to load an .ied file
        self._ic_name_types = {}

        # reach_info dictionary. Keeps track of the information needed to identify
        # reach status. Contains:
        # [0] = counter - iterated every time a new reach is started.
        # [1] = same reach status - keeps track of whether it's in an existing
        #       reach or starting a new one.
        self.reach_info = {'reach_number': 0, 'same_reach': False}

    def loadFile(self, file_path, arg_dict={}):
        """Loads the ISIS .DAT file.

        Splits it into objects for each unit type, initial conditions etc.

        This is an epic if-else section for each unit type currently
        represented.

        Needs cleaning up and writing with a bit more style.

        Easy to add another unit type, if it's not currently covered then it
        will just be collected in the universal 'UnknownUnit' and printed
        back out the same as it came in.

        Args:
            file_path (str): path to the .dat file to load.

        Returns:
            units - UnitCollection containing the dat file units or False if
                they couldn't be loaded.

        Raises:
            IOError: If the file cannot be loaded or is empty.
            AttributeError: if the file is not of an expected type (.dat/.ief).

        See Also:
            IsisUnitCollection
            FactoryClasses

        TODO: Decide if the observer style calls are ever going to be needed.
                If they aren't then remove them rather than have them
                cluttering up the file.
        """
        line = ''
        # Used to populate the data for the UnknownUnit
        self.unknown_data = []
        # Composite for all dat units
        path_holder = ftools.PathHolder(file_path)
        self.units = DatCollection(path_holder)
#         self.units.file_dir, self.units.filename = os.path.split(file_path)
#         self.units.filename = os.path.splitext(self.units.filename)[0]

        if not uf.checkFileType(file_path, ext=['.dat', '.DAT']):
            if not uf.checkFileType(file_path, ext=['.ied', '.IED']):
                logger.error('Illegal File Error: ' + file_path + '\nDoes not have extension (.dat, .DAT, .ied, .IED)')
                raise AttributeError('Illegal File Error: ' + file_path + '\nDoes not have extension (.dat, .DAT, .ied, .IED)')
            else:
                self.is_ied = True

        contents = self.__loadFile(file_path)
        if(contents == False):
            raise IOError('Unable to load file at: ' + file_path)

        return self.buildDat(contents, arg_dict)

    def buildDat(self, contents, arg_dict={}):
        """
        """
        self.contents = contents

        # Counter for the number of rows that have been read from the
        # file contents list.
        i = 0
        # Get an instance of the unit factory with the number of nodes in the file.
        unit_factory = FmpUnitFactory()

        # Dictionary containing the keys to identify units in the dat file
        unit_vars = unit_factory.getUnitIdentifiers()

        # Create a unit from the header data in the first few lines of the dat file.
        if not self.is_ied:
            i, self.temp_unit = unit_factory.createUnitFromFile(self.contents, 0, 'HEADER', 0)
            in_unknown_section = False

            # Now we can update the HeaderUnit subContents
            self.updateSubContents()

        in_unknown_section = False
        while i < len(self.contents):

            # Get the line and then split it to retrieve the first word.
            # Check this word against the # unit_type keys we set above to see
            line = self.contents[i]
            temp_line = line.strip()
            if temp_line:
                first_word = line.split()[0].strip()
            else:
                first_word = 'Nothing'

            if first_word in unit_vars:

                # If building an UnknownUnit then create and reset
                if(in_unknown_section == True):
                    self.createUnknownSection()
                    self.updateSubContents()

                    # Reset the reach for the UnknownUnit
                    unit_factory.same_reach = False

                '''Call the unit creator function and get back the unit and the
                updated contents list index.
                Most of these variables are self explanatory, but
                unit_vars[first_word] is the key for the unit type to make.
                '''
#                 i, self.temp_unit = unit_factory.createUnit(self.contents, i,
#                         unit_vars[first_word], self.cur_no_of_units)
                i, self.temp_unit = unit_factory.createUnitFromFile(self.contents, i,
                                                                    first_word,
                                                                    self.cur_no_of_units)

                '''In case we got in but found something wasn't supported.
                it's i-1 because we can't return onto the same line that was
                read or it will loop forever, so store it here and move on
                '''
                if self.temp_unit == False:
                    self.unknown_data.append(self.contents[i].rstrip('\n'))
                    i += 1
                    self.unknown_data.append(self.contents[i].rstrip('\n'))
                    in_unknown_section = True
                else:
                    self.updateSubContents()
                    in_unknown_section = False

            else:
                in_unknown_section = True
                self.unknown_data.append(self.contents[i].rstrip('\n'))

            i += 1

        line = None
        del self.unknown_data
        return self.units

    def createUnknownSection(self):
        """Builds unidentified sections from the .DAT file.

        All currently un-dealt-with sections of the .DAT file are
        incorporated into this.
        Loads in chunks of the file 'as-is' and prints them out the same way.
        """
#         logger.debug('Creating UnknownUnit - Unit No:  ' + str(self.cur_no_of_units))
        self.temp_unit = UnknownUnit()
        self.temp_unit.readUnitData(self.unknown_data)

    def getUnits(self):
        """Getter for imported units

        Note:
            Deprecated: Will be removed. Please use self.units directly.

        Returns:
            IsisUnitCollection - The units loaded from the dat file.
        """
        return self.units

    def updateSubContents(self):
        """Updates the self.units.

        Appends the new temp_unit to list of units and resets all the
        variables.
        """
        #logger.debug('In updateSubContents')
        # Don't update node count here as we aren't adding any 'new' nodes
        self.units.addUnit(self.temp_unit, update_node_count=False, no_copy=True)
        self.cur_no_of_units += 1
        del self.temp_unit
        self.unknown_data = []

    def __loadFile(self, filepath):
        """Load the .dat file into the contents list.

        Args:
            filepath: Path to the required DAT file.

        Returns:
            True if loaded ok, False otherwise.
        """
        logger.info('loading File: ' + filepath)
        contents = []
        try:
            contents = ftools.getFile(filepath)
        except IOError:
            logger.error('IOError - Unable to load file')
            return False

        if(contents == None):
            logger.error('.DAT file is empty at: ' + filepath)
            return False

        return contents
