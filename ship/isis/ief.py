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
    
    def __init__(self, path_holder, header, details, snapshots = None, 
                                    ied_data = None, description = None):
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
        exist, and are added to paths_dict. 
        
        The ied_data and snapshots lists are returned separately.
        
        Returns:
            tuple containing::

                {
                    'dictionary': the datafile, results, initial conditions 
                        and 2D file paths. if a path doesn't exist it will be 
                        set to False,
                    'list': Each element contains a dict of ied name and file 
                        path. If no .ied files exist this will be None, 
                    'list': Each element contains a dict of snapshot name and
                      file path. This may be None.
                }

        """
        paths_dict = {}
        paths_dict['datafile'] = self._findVarInDictionary(self.event_header, 'Datafile')
        paths_dict['results'] = self._findVarInDictionary(self.event_header, 'Results')
        paths_dict['initialconditions'] = self._findVarInDictionary(self.event_details, 'InitialConditions')
        paths_dict['twodfile'] = self._findVarInDictionary(self.event_details, '2DFile')
        
        return paths_dict, self.ied_data, self.snapshots
    
    
    def setValue(self, data_type, key, value):
        """Set the values in the data_type provided.
        
        Warning:
            This does not check that the key or value are legal for the 
            ief file format, so check that you know what you're adding and 
            that it is allowed in the IEF. 
        
        Args:
            data_type: The data dictionary that should be updated. Use 
                IefDataTypes to reference the data_type.
            key: The dictionary access key.
            value: The value to be added.
        """
        if data_type == IefDataTypes.HEADER:
            if not key in self.event_header:
                raise KeyError ('Key %s not found in event_header dictionary' % (key))
            
            self.event_header[key] = value
            
        elif data_type == IefDataTypes.DETAILS:
            if not key in self.event_details:
                raise KeyError ('Key %s not found in event_details dictionary' % (key))
            
            self.event_details[key] = value
    
    
    def getValue(self, data_type, key=None):
        """Get values dictionary or specific value based on key.

        IefDataTypes HEADER and DETAILS will return a specific value based on
        the provided key. IED_DATA, SNAPSHOTS and  DESCRIPTION will only 
        return the entire list so providing a key for these types will have
        no effect.

        Note:
            Use the IefDataTypes enum class for data_type.
        
        Args:
            data_type (int): The data dictionary in the ief object that you 
                want. 
            key (string): The key for the dictionary access - Optional: if 
                this is not provided the dictionary will be returned.
        
        Returns:
            Dictionary, list, or value requested or False if the key
                 provided does not exist.
            
            
        TODO:
            This should raise an error if the key provided doesn't exist, not
            return False.
        """
        if data_type == IefDataTypes.HEADER:
            if key == None:
                return self.event_header
            else:
                return self.getValue(self.event_header, key)

        elif data_type == IefDataTypes.DETAILS:
            if key == None:
                return self.event_details
            else:
                return self.getValue(self.event_details, key)

        elif data_type == IefDataTypes.IED_DATA:
            return self.ied_data

        elif data_type == IefDataTypes.SNAPSHOTS:
            return self.snapshots

        elif data_type == IefDataTypes.DESCRIPTION:
            return self.description


    def setListValue(self, data_type, key1, key2, value1, value2):
        """Set the value for the given list dataType.
        
        Note:
            This hasn't been implemented becuase it can be accessed directly.
            It probably never will be, so don't implement this without good
            reason.
            
        Raises:
            NotImplementedError
        """
        raise NotImplementedError    
            
            
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
            logger.info('No ' + key + ' key found in ief')
            raise ('Key %s not found in dictionary' % (key))
        
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
        for key, value in self.event_details.iteritems():
            if not key in event_start:
                contents.append(key + '=' + value)
        
        # Finally, if there's a description add it on.
        if not self.description == None and not len(self.description) < 1 \
                                        and not self.description[0] == '':
            
            contents.append('[Description]')
            for i, d in enumerate(self.description):
                contents.append(d)
        
        return contents




        