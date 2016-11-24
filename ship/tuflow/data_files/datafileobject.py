"""

 Summary:
    Used for accessing files that contain data and links to other files.
    contains a factory method that will select the correct concrete 
    implementation of ADataFileObject for the user based on the contents of
    the DataFile variables given as a parameter.

    Contains the abstract ADataFileObject class and concrete implmentations.

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

import os

from ship.utils import filetools
# from ship.data_structures.rowdatacollection import DataTypes
from ship.data_structures.rowdatacollection import RowDataCollection#, DataTypes

import logging
logger = logging.getLogger(__name__)

class ADataFileObject(object):
    """Abstract superclass for all data file objects.
    
    All classes that deal with reading and writing data from the DataFile 
    derivation of TuflowFilePart should create an implementation of this class.
    
    Loading of the data should be separated into the DataFileLoader module to
    reduce the complexity of these classes.
    
    Primarily these classes are for data access and handling although they also
    must contain a method for writing the data back to file.
    
    See Also:
        :class:'DataFile'  
        :module:'DataFileLoader'
    """
    
    def __init__(self, row_collection, file_part, comment_lines=[]):
        self.row_collection = row_collection 
        self.path_holder = file_part
        self.type = self.path_holder.extension
        self.command = self.path_holder.command
        self.keys = None
        self.subfiles = []
        self.comment_lines = comment_lines
        self.evt_src_data = file_part.evt_src_data
        
    
    def getDataEntry(self, key):
        """Returns the ADataObject associated with the given key.
        
        The Keys for each class are usually defined by a related enum. These
        should be used when calling this function.
        
        Args:
            key (int): values associated with the different data types.
            
        Return:
            ADataObject: containing the data stipulated by the given key.
            
        Raises:
            KeyError: if key value does not exist.
        """
        if self.keys is None or not key in self.keys.ITERABLE:
            raise KeyError ('Key %s does not match any avialable' % (key))
        
        return self.row_collection.getDataObject(key)


    def getDataEntryAsList(self, key):
        """Returns the a list of the data associated with the given key.
        
        The Keys for each class are usually defined by a related enum. These
        should be used when calling this function.
        
        Args:
            key (int): values associated with the different data types.
            
        Return:
            list: containing the data stipulated by the given key.
            
        Raises:
            KeyError: if key value does not exist.
        """
        if self.keys is None or not key in self.keys.ITERABLE:
            raise KeyError ('Key %s does not match any avialable' % (key))
        
        outlist = []
        data = self.row_collection.getDataObject(key)
        outlist = [d for d in data]

        return outlist
    
        
    def saveData(self, plus_subfiles=False):
        """Save the current state of the data contained by this instance.
        
        Unless plus_subfiles == False all subfile data will be saved as well.
        
        Args:
            plus_subfiles=False (bool): if True all associated subfile will be
            saved to their current state as well.
        
        Raises:
            IOError: if there is a problem writing to file.

        """
        try:
            contents = self._getPrintableContents()
            filetools.writeFile(contents, self.path_holder.absolutePath())
        except IOError:
            logger.error('Could not write contents for %s file to %s' %
                (self.path_holder.extension, self.path_holder.absolutePath()))
            raise IOError ('Unable to write file to disc')  
        
        if self.subfiles and plus_subfiles:
            for subfile in self.subfiles:
                try:
                    contents = subfile._getPrintableContents()
                    filetools.writeFile(contents, subfile.path_holder.absolutePath())
                except IOError:
                    logger.error('Could not write contents for %s file to %s' %
                        (subfile.path_holder.absolutePath()))
                    raise 
    
    
    def addSubfile(self, subfile):
        """Add a subfile to this object.
        
        Subfiles are separate data files that are references by the contents
        of an ADatafileObject instance.
        
        They should be derived from ADatafileSubFile.
        
        Args:
            subfile (ADataFileSubfile): subfile to add.
        
        Raises:
            TypeError if subfile is not of type ADataFileSubfile
            
        See Also:
            ADataFileSubfile
        """
        if not isinstance(subfile, ADataFileSubfile):
            raise TypeError ('subfile is not an instance of ADataFileSubFile')
        
        self.subfiles.append(subfile)
    
    
    def changeRoot(self, root):
        """Updates the root variable in the path_holder
        
        Args:
            root (str): new root directory.
        """
        self.path_holder.root = root
        for s in self.subfiles:
            s.path_holder.root = root
    
    
    def getAllPaths(self, include_this=True, name_only=False, resolve_paths=True):
        """Get all paths held by this object
        
        Args:
            include_this=True(bool): if True it includes the path of this 
                DatafileObject.
            name_only=False(bool): if True only the filename will be returned.
            resolver_name=True(bool): if True any placeholders in the filename
                will be replaced with the value set in the EventSourceData.
        
        Return:
            list - containing all the filepaths referenced by this object.
        """
        paths = []
        if include_this:
            if not name_only:
                paths.append(self.path_holder.absolutePath())
            else:
                paths.append(self.path_holder.filenameAndExtension())
        for s in self.subfiles:
            if not name_only:
                paths.append(s.path_holder.absolutePath())
            else:
                paths.append(s.path_holder.filenameAndExtension())
        
        if resolve_paths:
            paths = self.resolveEvtSrc(paths)
        
        return paths
    

    def resolveEvtSrc(self, values):
        """Replace placeholders with values in the given list.
        
        Placeholder values can be used in most of the data files to define
        filenames, variables, etc. This method will replace the placeholder
        with the corresponding value if found in the EventSourceData.
        
        Args:
            value(list): str's to replace placeholders in.
        """
        out = []
        placeholders = self.evt_src_data.keys()
        for v in values:
            for holder in placeholders:
                v = v.replace(holder, self.evt_src_data[holder])
            out.append(v)
            
        return out
    

    def _getPrintableContents(self):
        """Format the data held by this object for writing to file."""
        raise NotImplementedError
    

class XsEnum(object):
    """Enum for accessing data in CrossSectionDataObject."""
    SOURCE, TYPE, FLAGS, COLUMN_1, COLUMN_2, COLUMN_3, COLUMN_4, COLUMN_5, \
    COLUMN_6, Z_INCREMENT, Z_MAXIMUM, SKEW = range(12)
    ITERABLE = range(12)


class XsDataObject(ADataFileObject):
    """
    """
    
    def __init__(self, row_collection, file_part, comment_lines=[]):
        """
        """
        ADataFileObject.__init__(self, row_collection, file_part, comment_lines)
        self.keys = XsEnum()

    
    def _getPrintableContents(self):
        """Format data held by this object for writing to file."""
        logger.warning('It is not currently possible to save changes from XsDataObjects')
        raise NotImplementedError


    
class TmfEnum(object):
    """Enum for accessing data in TmfDataObject
    """
    ID, MANNINGS, INITIAL_LOSS, CONTINUING_LOSS, MANNINGS_DEPTH_1, MANNINGS_1, \
    MANNINGS_DEPTH_2, MANNINGS_2, RESERVED, SOIL_REDUCTION_FACTOR, \
    FRACTION_IMPERVIOUS = range(11)
    ITERABLE = range(11)

class TmfDataObject(ADataFileObject):
    """Concrete implementation of the ADataFileObject class.
    
    Used for reading/writing tuflow .tmf materials files.
    """ 
    
    def __init__(self, row_collection, file_part, comment_lines):
        """Constructor

        Args:
            row_collection (rowdatacollection): row data from file.
            file_part (DataFile): containing the path info for the file.
            comment_lines (list): containing the contents of any comment only
                lines in the file.
        """
        ADataFileObject.__init__(self, row_collection, file_part, comment_lines)
        self.keys = TmfEnum()
    

    def _getPrintableContents(self):
        """Format the data held by this object for writing to file."""

        file_length = self.row_collection.getNumberOfRows()
        out_contents = range(file_length)
        
        data_rows = self.row_collection.getDataObject('row_no')
        
        no_of_rows = self.row_collection.getNumberOfRows()
        for i in range(0, no_of_rows):
            self.row_collection.deleteDataObject('row_no')
            out_contents[data_rows.getValue(i)] = self.row_collection.getPrintableRow(i)
        
        # Add any comment lines in
        for i, c in enumerate(self.comment_lines):
            if not c is None:
                out_contents.insert(i, c)
        
        return out_contents


class BcEnum(object):
    """Enum for accessing data in BcDataObject
    """
    NAME, SOURCE, COLUMN1, COLUMN2, ADD_COL_1, MULT_COL, ADD_COL_2, \
    COLUMN_3, COLUMN_4 = range(9)
    ITERABLE = range(9)

class BcDataObject(ADataFileObject):
    '''Concrete implementation of the ADataFileObject class.
    Reads/Writes the data in tuflow boundary condition database csv files.
    '''
     
    def __init__(self, row_collection, file_part, comment_lines):
        """Constructor

        Args:
            row_collection (rowdatacollection): row data from file.
            file_part (DataFile): containing the path info for the file.
            comment_lines (list): containing the contents of any comment only
                lines in the file.
        """
        ADataFileObject.__init__(self, row_collection, file_part, comment_lines)
        self.keys = BcEnum()
    
    
    def getAllPaths(self, include_this=True, name_only=False, resolve_paths=True):
        """Get all paths held by this object
        
        Overrides superclass method.
        
        Args:
        
        
        Return:
        
        """
        paths = []
        if include_this:
            if not name_only:
                paths.append(self.path_holder.absolutePath())
            else:
                paths.append(self.path_holder.filenameAndExtension())
                
        source = self.row_collection.getDataObject(self.keys.SOURCE)
        for s in source:
            if not name_only:
                paths.append(os.path.join(self.path_holder.root, 
                                      self.path_holder.parent_relative_root, 
                                      self.path_holder.relative_root, s))
            else:
                paths.append(s)
        
        if resolve_paths:
            paths = self.resolveEvtSrc(paths) 
            
        return paths
    
        
    def _getPrintableContents(self):
        """Format data for printing to file"""

        data_rows = self.row_collection.getDataObject('row_no')
        header_row = self.row_collection.getDataObject('actual_header').getDataCollection()
        no_of_rows = self.row_collection.getNumberOfRows()
        out_contents = range(no_of_rows)
        
        for i in range(0, no_of_rows):
            self.row_collection.deleteDataObject('row_no')
            self.row_collection.deleteDataObject('actual_header')
            out_contents[data_rows.getValue(i)] = self.row_collection.getPrintableRow(i)
        
        header_row = ', '.join(header_row)
        out_contents.insert(0, header_row)
        
        # Add any comment lines in
        for i, c in enumerate(self.comment_lines):
            if not c is None:
                out_contents.insert(i, ' ,'.join(c))
        
        return out_contents 


class MatCsvEnum(object):
    """Enum for accessing data in MatCsvDataObject
    """
    ID, MANNINGS, N1, Y1, N2, Y2, SUBFILE_NAME, HEADER1, HEADER2, IL, CL, \
    HAZARD_ID = range(12) 
    ITERABLE = range(12)
    
class MatCsvDataObject(ADataFileObject):
    '''Concrete implementation of the ADataFileObject class.
    Reads/Writes the data in tuflow Materials csv files.
    '''
     
    def __init__(self, row_collection, file_part, comment_lines):
        """Constructor

        Args:
            row_collection (rowdatacollection): row data from file.
            file_part (DataFile): containing the path info for the file.
            comment_lines (list): containing the contents of any comment only
                lines in the file.
        """
        ADataFileObject.__init__(self, row_collection, file_part, comment_lines)
        self.keys = MatCsvEnum()
        
        
    def _getPrintableContents(self):
        """Format the data held by this object for writing to file."""
               
        # Grab these because they need deleting in the loop.
        data_rows = self.row_collection.getDataObject('row_no')
        header_row = self.row_collection.getDataObject('actual_header').getDataCollection()
        comment_row = self.row_collection.getDataObject('comment').getDataCollection()
        no_of_rows = self.row_collection.getNumberOfRows()
        out_contents = range(no_of_rows)
        
        # Get each row in the collection. Need to delete values not written to
        # file on each iteration.
        for i in range(0, no_of_rows):
            self.row_collection.deleteDataObject('row_no')
            self.row_collection.deleteDataObject('actual_header')
            self.row_collection.deleteDataObject('comment')
            out_contents[data_rows.getValue(i)] = self._refactorPrintableRow(self.row_collection.getPrintableRow(i)) + comment_row[i+1]
            
        # Add the header names to the start of the list.
        header_row = self._refactorPrintableRow(header_row, True)
        header_row = ', '.join(header_row) + comment_row[0]
        out_contents.insert(0, header_row)
        
        # Add any comment lines in
        for i, c in enumerate(self.comment_lines):
            if not c is None:
                out_contents.insert(i, ' ,'.join(c))
        
        return out_contents
    
    
    def _refactorPrintableRow(self, data_row, is_header=False):
        """Converts the values from individual back to tuflow recognised groupings.
        
        Tuflow can have multiple values grouped under a single heading.  
        E.g. Mannings can equal:  
            * Single value.  
            * Two n values and two depth values.  
            * A file name and up to two column headers.
            
        This takes the separated values and groups them back together again.
        
        Args:
            data_row (list): The row taken from the RowCollection.
            is_header=False (bool): true if this is a header row.
        
        Return:
            string: comma seperated for writing to file.
        """
        out_row = [''] * 5
         
        if is_header:
            out_row[0] = data_row[0]
            out_row[1] = data_row[1]
            out_row[2] = data_row[9]
            out_row[3] = data_row[11]
            return out_row
         
        # ID is always a single value
        data_row = data_row.split(',')
        out_row[0] = data_row[0].strip()
         
        # if only a single manning's n value
        if not data_row[1] == ' ':
            out_row[1] = data_row[1].strip()
         
        # otherwise it's multiple mannings n and depth values
        elif not data_row[2] == ' ':
            out_row[1] = '\"' + data_row[2].strip() + ',' + data_row[3].strip() + ',' + data_row[4].strip() + ',' + data_row[5].strip() + '\"' 
        
        # Or finally it could be file name and headers
        else:
            out_row[1] = data_row[6].strip()
             
            if not data_row[7] == ' ':
                out_row[1] += ' | ' + data_row[7].strip()
             
            if not data_row[8] == ' ':
                out_row[1] += ' | ' + data_row[8].strip()
 
        # Infiltration parametres
        out_row[2] = '\"' + data_row[9].strip() + ', ' + data_row[10].strip() + '\"'
        # Land use hazard
        out_row[3] = data_row[11].strip()
         
        out_row = ','.join(out_row)
        return out_row


class ADataFileSubfile(object):
    """Abstract super class for and ADataFileObject contained subfiles.
    
    Any files that are referenced by the ADataFileObject and which need to be
    read in should be included in the ADataFileObject's self.subfiles list
    and be derived from this class.
    """
    
    def __init__(self, path_holder, row_collection, filename, comment_lines=[]):
        """Constructor.
        
        Args:
            path_holder (PathHolder): containing file path data.
            row_collection (rowdatacollection): containing all of the
                row data read from file.
            filename (string): the name of file the object is based on.
            comment_lines=[] (list): containing any comment only lines that
                do not need accessing from within the row data.
        """
        self.path_holder = path_holder
        self.row_collection = row_collection 
        self.keys = None
        self.filename = filename
        self.comment_lines = comment_lines
    
    
    def _getPrintableContents(self):
        raise NotImplementedError


class SubfileMatEnum(object):
    """Enum for use in accessing data in DataFileSubfileMat"""
    NAME, DEPTH, MANNINGS = range(3)
    ITERABLE = range(9)

class DataFileSubfileMat(ADataFileSubfile):
    """Concrete instance of ADataFileSubfile"""
    
    def __init__(self, path_holder, row_collection, comment_lines, filename, 
                                        head1_location, head2_location):
        """Constructor.
        
        Args:
            path_holder (PathHolder): containing file path data.
            row_collection (rowdatacollection): containing all of the
                row data read from file.
            filename (string): the name of file the object is based on.
            comment_lines=[] (list): containing any comment only lines that
                do not need accessing from within the row data.
            head1_location (int): location of the first key header in the file
                columns.
            head2_location (int): location of the second key header in the file
                columns.
        """
        ADataFileSubfile.__init__(self, path_holder, row_collection, filename,
                                  comment_lines)

        self.keys = SubfileMatEnum()
        self.head1_location = head1_location
        self.head2_location = head2_location
        
    
    def _getPrintableContents(self):
        """Format data for printing to file"""

        data_rows = self.row_collection.getDataObject('row_no')
        header_row = self.row_collection.getDataObject('actual_header').getDataCollection()
        no_of_rows = self.row_collection.getNumberOfRows()
        out_contents = range(no_of_rows)
        
        for i in range(0, no_of_rows):
            self.row_collection.deleteDataObject('row_no')
            self.row_collection.deleteDataObject('actual_header')
            out_contents[data_rows.getValue(i)] = self.row_collection.getPrintableRow(i)
        
        header_row = ', '.join(header_row)
        out_contents.insert(0, header_row)
        
        # Add any comment lines in
        for i, c in enumerate(self.comment_lines):
            if not c is None:
                out_contents.insert(i, ' ,'.join(c))
        
        return out_contents 


