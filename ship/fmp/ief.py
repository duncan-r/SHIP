"""

 Summary:
    Ief file data holder.

    Contains the functionality for loading ISIS .ief files from disk.

 Author:
     Duncan Runnacles

  Created:
     01 Apr 2016

 Copyright:
     Duncan Runnacles 2016

 TODO:

 Updates:

"""


import os

from ship.utils import utilfunctions as uf
from ship.utils import filetools as ft

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class IefDataTypes(object):
    """Enum for the different data types within the Ief class.

    Use these for easy access of the Ief class.
    """
    HEADER, DETAILS, IED_DATA, SNAPSHOTS, DESCRIPTION = range(5)


class Ief(object):
    """Contains the details in the in the IEF file.

    Class data and a methods for accessing and upating the .ief file.
    """

    def __init__(self, path_holder, header, details, snapshots=None,
                 ied_data=None, description=None):
        """Constructor.

        Args:
            path_holder (PathHolder): Object containing the file path to this
                ief file.
            header: The [Event header] section of th ief file. It contains
                data like the title and main filepaths.
            details: The [Event Details] section of the ief file. It
                contains almost all the other data in the ief file, including
                all the flags for the run.
            snapshots: List containing a dictionary in each element that
                has the snapshot time and filepath.
            ied_data: List containing a dictionary in each element that
                contains the title and file path for every ied file referenced
                in the ief file.
            description: List containing the line of the description
                section of the file.
        """
        self.event_header = header
        self.event_details = details
        self.snapshots = snapshots
        self.ied_data = ied_data
        self.description = description
        self.path_holder = path_holder

    def getFilePaths(self):
        """Returns all the file paths that occur in the ief file.

        Most paths are extracted from the head and details data, when they
        exist, and are added to paths_dict. If any ied data or snapshot data
        exists it will be added as a list to the dictionary.

        If a particular path is not found the value will be set to None, unless,
        it's ied or snapshot data in which case it will be an empty list.

        Dict keys are: Datafile, Results, InitialConditions, 2DFile, ied,
        and snapshots.

        Returns:
            dict - containing all of the path data stored by this object.
        """
        paths_dict = {}
        try:
            paths_dict['Datafile'] = self._findVarInDictionary(self.event_header, 'Datafile')
        except:
            paths_dict['Datafile'] = None
        try:
            paths_dict['Results'] = self._findVarInDictionary(self.event_header, 'Results')
        except:
            paths_dict['Results'] = None
        try:
            paths_dict['InitialConditions'] = self._findVarInDictionary(self.event_details, 'InitialConditions')
        except:
            paths_dict['InitialConditions'] = None
        try:
            paths_dict['2DFile'] = self._findVarInDictionary(self.event_details, '2DFile')
        except:
            paths_dict['2DFile'] = None

        if not self.ied_data is None and not self.ied_data == []:
            ied_paths = [ied['file'] for ied in self.ied_data]
            paths_dict['ieds'] = ied_paths
        else:
            paths_dict['ieds'] = []

        if not self.snapshots is None and not self.snapshots == []:
            snapshot_paths = [snap['file'] for snap in self.snapshots]
            paths_dict['snapshots'] = snapshot_paths
        else:
            paths_dict['snapshots'] = []

        return paths_dict

    def getValue(self, key):
        """Get a value from one of the variables dictionaries.

        All single variables (i.e. not lists like ied data) are stored in two
        main dictionaries. This method will return the value associated with
        the given key from whichever dictionary it is stored in.

        Args:
            key(str): dict key for value. For a list of available keys use the
                getAvailableKeys method.

        Return:
            string: value referenced by the given key, in the ief file.

        Raises:
            KeyError: if the given key does not exist.
        """
        if key in self.event_header.keys():
            return self.event_header[key]

        elif key in self.event_details.keys():
            return self.event_details[key]

    def getIedData(self):
        """Get all of the ied data stored in this object.

        There can be multiple ied files referenced by an ief. This will return
        a dictionary containing all of them.

        If no ied files are included in the ief file the returned list will
        be empty.

        Returns:
            dict - containing {ied_name: ied_path} for all ied files referenced.
        """
        if self.ied_data == None:
            return []
        else:
            return self.ied_data

    def getSnapshots(self):
        """Get all of the snapshot data stored in this object.

        There can be multiple snapshot files referenced by an ief. This will return
        a dictionary containing all of them.

        If no snapshots are included in the ief file the returned list will
        be empty.

        Returns:
            dict - containing {snapshot_time: snapshot_path} for all snapshot
                files referenced.
        """
        if self.snapshots == None:
            return []
        else:
            self.snapshots

    def getDescription(self):
        """Returns the description component of the ief."""
        return self.description

    def setValue(self, key, value):
        """Set the value of one of dictionary entries in the ief.

        Args:
            key(str): The key of the value to update.
            value(str(: the value to update.

        Raises:
            KeyError: if given key is not recongised.

        Warning:
            Currently no checks are made on the validity of the the key given
            this is because it may be a legal key, but not yet exist in the
            dictionary. To fix this a list of all valid keys should be created
            and checked here before setting the value. These are the keys used
            in the ief file.
        """
        headlist = ['Title', 'Path', 'Datafile', 'Results']
        if key in headlist:
            self.event_header[key] = value
        else:
            self.event_details[key] = value

    def addIedFile(self, ied_path, name=''):
        """Add a new ied file.

        Args:
            ied_path(str): path to an ied file.
            name=''(str): name for the ied file.
        """
        if self.ied_data is None:
            self.ied_data = []
        self.ied_data.append({'name': name, 'file': ied_path})

    def addSnapshot(self, snapshot_path, time):
        """Add a new snapshot.

        Args:
            snapshot_path(str): the path for the snapshot.
            time(float): the time to assign to the snapshot.
        """
        if self.snapshots is None:
            self.snapshots = []
        if not uf.isNumeric(time):
            raise ValueError('time is not a numeric value')

        self.snapshots.append({'time': time, 'file': snapshot_path})

    def _findVarInDictionary(self, the_dict, key):
        """Returns the variable in a dictionary.

        Tests to see if a variables exists under the given key in the given
        dictionary. If it does it will return it.

        Args:
            the_dict (Dict): Dictionary in which to check the keys existence.
            key (str): Key to look for in the dictionary.

        Returns:
            The requested variable if it exists or False if not.
        """
        try:
            variable = the_dict[key]
        except KeyError:
            logger.debug('No ' + key + ' key found in ief')
            return False

        return variable

    def getPrintableContents(self):
        """Return the contents of the file for printing.

        Formats the contents of this Ief instance ready to be written back
        to file.

        Returns:
            List of the formatted lines for printing to file.

        TODO:
              This function is a bit long and messy at the moment. Could do
              with a good refactoring.
        """
        contents = []

        # Add the header data in a specific order
        headlist = ['Title', 'Path', 'Datafile', 'Results']
        contents.append('[ISIS Event Header]')
        for h in headlist:
            var = self._findVarInDictionary(self.event_header, h)
            if not var == False:
                contents.append(h + '=' + var)

        # Add the top of the event list
        event_start = ['RunType', 'InitialConditions', 'Start', 'Finish',
                       'Timestep', 'SaveInterval']
        contents.append('[ISIS Event Details]')
        for s in event_start:
            var = self._findVarInDictionary(self.event_details, s)
            if not var == False:
                contents.append(s + '=' + var)

        # Add snapshot stuff
        if not self.snapshots == None:
            for s in self.snapshots:
                contents.append('SnapshotTime=' + s['time'])
                contents.append('SnapshotFile=' + s['file'])

        # Add ied stuff
        if not self.ied_data == None:
            for d in self.ied_data:
                contents.append(';' + d['name'])
                contents.append('EventData=' + d['file'])

        # Now throw in everything else
        for key, value in self.event_details.items():
            if not key in event_start:
                contents.append(key + '=' + value)

        # Finally, if there's a description add it on.
        if not self.description == None and not len(self.description) < 1 \
                and not self.description[0] == '':

            contents.append('[Description]')
            for i, d in enumerate(self.description):
                contents.append(d)

        return contents

    def write(self, filepath=None, overwrite=False):
        """Write the contents of this file to disk.

        Writes out to file in the format required for reading by ISIS/FMP.

        Note:
            If a filepath is not provided and the settings in this objects
            PathHolder class have not been updated you will write over the
            file that was loaded.

        Args:
            filepath=None(str): if a filename is provided it the file will be
                written to that location. If not, the current settings in this
                object path_holder object will be used.
            overwrite=False(bool): if the file already exists it will raise
                an IOError.

        Raises:
            IOError - If unable to write to file.
        """
        if filepath is None:
            filepath = self.path_holder.absolutePath()

        if not overwrite and os.path.exists(filepath):
            raise IOError('filepath %s already exists. Set overwrite=True to ignore this warning.' % filepath)

        contents = self.getPrintableContents()
        ft.writeFile(contents, filepath)
