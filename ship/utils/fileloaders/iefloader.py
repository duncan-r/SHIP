"""

 Summary:
    Contains the Factory class for loading and building the Ief object from
    an ief file at a given path.

 Author:  
     Duncan Runnacles

  Created:  
     01 Apr 2016
     
 Copyright:  
     Duncan Runnacles 2016

 TODO:

 Updates:

"""


from ship.utils.atool import ATool
from ship.utils import filetools
from ship.utils.fileloaders.loader import ALoader
from ship.fmp.ief import Ief
from ship.utils import utilfunctions as uf

import os

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class IefLoader(ATool, ALoader):
    """Builds an Ief object.

    Contains the details of the ISIS ief file located at the given file path.

    Factory class for reading the ISIS ief file into an Ief object that allows
    for simple access and updating of the ief file.

    See Also:
        atool
    """

    def __init__(self):
        """Constructor."""
        ATool.__init__(self)
        ALoader.__init__(self)
        logger.debug('Initialising IEFLoader')

    def loadFile(self, file_path, arg_dict={}):
        """Loads the ief file at the given path.

        Args:
            file_path (str): The path to the ief file.

        Returns:
            Ief file object containing the contents loaded from file.
        """
        if not uf.checkFileType(file_path, ext=['.ief', '.IEF']):
            logger.error('File: ' + file_path + '\nDoes not match ief extension (*.ief or *.IEF)')
            logger.error('Illegal File Error: %s is not of type ief' % (file_path))
            raise AttributeError('Illegal File Error: %s is not of type ief' % (file_path))

        contents = self._loadFile(file_path)
        # if we couldn't load the file let them know.
        if contents == False:
            raise IOError('Unable to load file at: ' + file_path)

        event_header = {}
        event_details = {}
        snapshot = []
        ied_data = []
        description = []
        in_event_details = False

        index = 0
        while(index < len(contents)):
            c = contents[index]

            # If we're moving into the event details then mark it and skip the
            # next line, which tells us so.
            if c.strip('\n') == '[ISIS Event Details]':
                in_event_details = True
                index += 1
                continue

            # Collect the header data with the name as the key and the variable
            # as the value.
            if not in_event_details:
                if not c.strip('\n') == '[ISIS Event Header]':
                    self._addHeaderLine(event_header, c)

            else:

                # If it's a snapshot then get the time. We know that the next
                # line is a file reference so get that too then skip ahead by
                # one line in the contents.
                if c.split('=')[0] == 'SnapshotTime':
                    index = self._addSnapshotLine(snapshot, contents, index)

                # If the line starts with a ';' then it's an IED file so grab
                # the name and get the file file reference from the next line
                # and skip ahead.
                elif c[:1] == ';':
                    index = self._addIedLine(ied_data, contents, index)

                # Otherwise just populate the event_details.
                else:
                    # If the description bit is included its at the end so just grab the
                    # last few line and put them in it.
                    if c.strip() == '[Description]':
                        index = self._loadDescription(description, contents, index)
                        break
                    else:
                        if not c.strip() == '':
                            self._addDetailsLine(event_details, contents, index)

            index += 1

        path_holder = filetools.PathHolder(file_path)
        ief_file = Ief(path_holder, event_header, event_details, snapshot, ied_data, description)
        return ief_file

    def _addHeaderLine(self, event_header, value):
        """Adds a line from the ief file to the event_header dictionary.

        Args:
            event_header (Dict): The header details.
            value(str): contents of the .ief file line
        """
        splitvals = value.split('=', 1)
        event_header[splitvals[0]] = splitvals[1].rstrip('\n')

    def _addDetailsLine(self, event_details, contents, index):
        """Adds a line from the ief file to the event_details dictionary.

        Args:
            event_details (Dict): The event details.
            contents (List): the lines from the ief file.
            index (int): The current index in the contents list. 
        """
        splitvals = contents[index].split('=', 1)
        event_details[splitvals[0]] = splitvals[1].rstrip('\n')

    def _addSnapshotLine(self, snapshot, contents, index):
        """Adds a line from the ief file to the snapshot list.

        Args:
            snapshot (List): contains dictionaries with the name and filepath
                of all the snapshot files in the ief.
            contents (List): The list containing the lines from the ief file.
            index (int): The current index in the contents list. 
        """
        snaptime = contents[index].split('=', 1)[1].rstrip()
        snapfile = contents[index + 1].split('=', 1)[1].rstrip('\n')
        snapshot.append({'time': snaptime, 'file': snapfile})
        index += 1
        return index

    def _addIedLine(self, ied_data, contents, index):
        """Adds a line from the ief file to the ied_data list.

        Args:
            ied_data (List): dictionaries with the name and filepath of all 
                the ied files in the ief.
            contents (List): containing the lines from the ief file.
            index (int): The current index in the contents list. 

        Returns:
            Int - updated index value.
        """
        event_name = contents[index][1:].strip('\n')
        event_path = contents[index + 1].split('=', 1)[1].rstrip('\n')
        ied_data.append({'name': event_name, 'file': event_path})
        index += 1
        return index

    def _loadDescription(self, description, contents, index):
        """Adds the description line from the ief file into a description list.

        The description is the last section of the ief file so at this point
        grab everything left in the file and return.

        Args:
            description (List): list to append description lines to.
            contents (List): containing the lines from the ief file.
            index (int): The current index in the contents list.

        Returns:
            int - updated list index value.
        """
        index += 1
        while index < len(contents):
            description.append(contents[index].strip())
            index += 1
        return index

    def _loadFile(self, filepath):
        """Load the .ief file into the contents list.

        Args:
            filepath (str): Path to the required IEF file. 

        Returns:
            The file contents as a list if loaded ok; False otherwise.
        """
        logger.info('loading File: ' + filepath)
        contents = None
        try:
            contents = filetools.getFile(filepath)
            return contents
        except IOError:
            logger.error('IOError - Unable to load file')
            return False

        if(contents == None or contents == ''):
            logger.error('.ief file is empty at: ' + filepath)
            return False

        return contents
