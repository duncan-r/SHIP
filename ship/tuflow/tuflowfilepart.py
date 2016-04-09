"""

 Summary:
    Contains all of the :class:'TuflowFilePart' type classes.
    
    TuflowFilePart is the interface that all parts of the Tuflow model files 
    should inherit. i.e. SomeFile and derivatives, ModelVariables and ,
    derivatives etc.
    
    Contains the SomeFile base class and other specific types for holding
    the file path objects. These are used for accessing and updating file
    paths read in from the Tuflow model files.
    
    Any TuflowFilePart that contains information about a path variables.
    E.g. BC Database == ..\bc_database\bc.csv
    
    Will be stored in this class or a class derived from this.

    This version of the module replaces the old SomeFile ModelVariables and 
    TuflowFilePart modules. It seemed unnecessary to keep them apart has they 
    are so closely related to each other. The SomeFile module no longer exists.

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

from ship.utils.filetools import PathHolder

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class TuflowFilePart(object):
    """Superclass for any part of a Tuflow file.
    
    This is a light weight superclass that MUST BE inherited by any class
    that will hold data pertaining to the Tuflow model files.

    It is affectively abstract, although it does contain a single functioning
    method getPrintableContents() which should be overridden by any class that
    inherits from it.

    It's key task is maintaining a reference to the order in which sections of
    the tuflow model file were read in. This allows the contents to be written
    out in the correct order when producing a new version of the tuflow model
    file.

    It is also used to keep track of any "unkown contents" within the file.
    I.e. anything that the file loader doesn't know about will be thrown into
    a list to be written out the same as it came in.
    """
    
    
    def __init__(self, global_order, hex_hash, type):
        """Constructor.

        Initialises the file order to -1 and the unknown_contents to a list
        """
        self.file_order = -1
        self.global_order = global_order
        self.unknown_contents = []
        self.hex_hash = hex_hash
        self.TYPE = type
        self.category = ''
        
        
    def getPrintableContents(self):
        """Return contents formatted for writing to file.
        
        Return the contents for the section that this TuflowFilePart is 
        responsible for. By default it will return the unkown contents stored
        in this object.
    
        Note:
            This method should be overridden by any inheriting class in order 
            to properly format the data that it holds for printing back to 
            file.
        
        Returns:
            list of unknown_contents ready to print to file.
        """            
        return self.unknown_contents


class ModelVariables(TuflowFilePart):
    """Stores information on Tuflow model file variable(s).
    
    Holds information pertaining to a variable or a set of variables
    defined in one of the Tuflow model files. This will be a single line
    of the text file.
    
    E.g. MASS BALANCE OUTPUT == ON
    
    It contains methods for reading in the text into variables, providing
    access to those variables for reading or updating and returning the
    line formatted for writing to an updated tuflow model file.
    
    TODO:
        Put in a way to update the variables. This should update the
        individual variable list AND the raw_var variable.
    """
    
    def __init__(self, global_order, var, hex_hash, type, command):
        """Constructor.

        Takes the two parts of a variables command line in a tuflow model file.
        
        All commands in the model files are written as:
        command == some variables go here
        
        The first part of the line, before the '==' sign is command and the 
        second part is var. Var can contain either a single variable or many
        seperated by spaces (as is the case in tuflow model files).
        If there is any comment on the end of the line it will be removed and
        saved seperately for writing back out later.
        
        Args:
            var: variable part of the tuflow command (the bit after '==').
            command: The command part of the tuflow command (the bit before
               the '==')
        """
        TuflowFilePart.__init__(self, global_order, hex_hash, type)

        # extract the variables and the comment (if it exists)
        self.comment = None
        if '!' in var:
            self.raw_var, self.comment = var.split('!', 1)
            self.comment = self.comment.strip()
        elif '#' in var:
            self.raw_var, self.comment = var.split('#', 1)
            self.comment = self.comment.strip()
        else:
            self.raw_var = var
            
        self.raw_var = self.raw_var.strip()
         
        self.command = command.strip()
        
        # If var has spaces in it then it contains more than one values and
        # we need to break them up into a list.
        self.multi_var = None
        if ' ' in var:
            self.multi_var = self.raw_var.split()
            
            
    def getPrintableContents(self):
        """Return the contents formatted for printing.
        
        The returned value will be the complete line ready for writing to
        file.
        
        E.g. MASS BALANCE OUTPUT == ON  ! Some comment here
        back to the tuflow model file.
        
        Returns:
            String - variables line formatted for writing to a file.
        """
        contents = self.command + ' == ' + self.raw_var
        
        # Add the comment back on if it exists.
        if not self.comment == None or self.comment == '':
            contents += ' ! ' + self.comment
        
        return contents
            

            
class SomeFile(TuflowFilePart, PathHolder):
    """Associated with files that are used in TuFLOW models.

    It has specific variables and methods for it's use in that way. E.g. it
    contains a command variable - a variable that defines what the command used
    to call the path is.
    
    The majority of the actual path manupulation methods and storage is 
    inherited from the PathHolder class that this inherits from.
    
    See Also:
        TuflowFilePart and PathHolder    

    TODO:
        Need to make it so that this class can read in / write out piped file
        commands. e.g:
            Read GIS Z HX Line == mi\2d_bc_v1.MIF | mi\2d_zpt_v2.MIF
    """
    
    def __init__(self, global_order, path, hex_hash, type, command, root=None, 
                       parent_relative_root='', category=None, parent_hash=None, 
                       child_hash=None ):
        """Constructor.
        

        Most tuflow files are referenced relative to the file that they are
        called from. This method eakes a 'root' as an optional argument.
        The root will allow for an absolute path to be created from the 
        relative path. 
        
        This means that the file stored in this object will be
        able to store it's absolute path as well the path relative to the
        callng file.
        
        E.g.  
            ..\bc_dbase\bc.csv  
            c:\actual\path\runs\..\bc_dbase\bc.csv

        Args:
            global_order(int): order that the file object was read in.
            path (str): the path to the file that this object holds the meta 
                data for.
            hex_hash(str): hexidecimal code for this object.
            type(int): the TuflowTypes value for this object.
            command (str): the command that was used to call this path in the 
                model file.
            root=None (str): the path to the directory that is the root of 
                this file.
            parent_relative_root=''(str): the path section relative to the main
                file read in (the tcf or ecf).
            category=None(str): Any category specification for the file.
            parent=None(str): the hash code of any parent that this file may
                have. This will be non-None if the file is read in after a 
                pipe command (e.g. with: file_1.mif | file_2.mif | file_3.mif 
                if this file is file_3 then the parent will be the hash code for 
                file_2.
            child=None(str): the hash code of any child that this file may
                have. This will be non-None if the file is read in after a 
                pipe command (e.g. with: file_1.mif | file_2.mif | file_3.mif 
                if this file is file_1 then the child will be the hash code for 
                file_2.
                
        See Also:
            :class:'TuflowTypes'  
            :class:'TuflowFilePart'
        """
        if not isinstance(path, basestring):
            raise TypeError
        
        TuflowFilePart.__init__(self, global_order, hex_hash, type)
        
        self.command = command
        self.category = category
        self.comment = None
        self.all_types = None
        self.parent_hash = parent_hash
        self.child_hash = child_hash
        
        # If it's an absolute path then we will set the root to be that rather
        # than the normal root used for absolute paths so this will be True.
        self.has_own_root = False 
        self.file_name_is_prefix = False
        
        # Tuflow commands are allowed comments after them denoted by '!' so we
        # split on this to make sure it's removed from the path name.
        if '!' in path:
            path, self.comment = path.split('!', 1)
            self.comment = self.comment.strip()
        elif '#' in path:
            path, self.comment = path.split('#', 1)
            self.comment = self.comment.strip()
        
        # Call superclass constructor
        PathHolder.__init__(self, path, root)
        self.parent_relative_root = parent_relative_root

    
    def getPrintableContents(self):
        """Return the formatted contents of this file command.

        Args:
            String formatted for writing to a tuflow model file.
        """
        # Deal with piped commands
        if not self.parent_hash == None:
            start = ''
        else:
            start = self.command + ' == '
            
        if not self.relative_root == None:
            contents = start + self.getRelativePath()
        
        elif not self.root == None:
            contents = start + os.path.join(self.root, self.getFileNameAndExtension())
        
        else:
            contents = start + self.getFilenameAndExtension()

        if not self.comment == None or self.comment == '':
            contents += ' ! ' + self.comment 
            
        return contents
    
    
    def getFileNameAndExtensionAllTypes(self):
        """Get the filename with extension for all types.
        
        Some types of file can have implied associated file. Tuflow knows that
        Shape file may have .prj, .dbf, etc files associated with them as well
        even though they aren't declared in the files.
        
        This function will return a list of all of the filename with all
        possible fie extensions associated with the file type.
        
        Return:
            list containing filename.extension for every type associated
                with this file name.

        Note:
            The other types are taken from a list of known types, not checked in
            the file. This should be done by the calling code.
        
        """
        all_names = []
        if self.all_types == None:
            return [self.getFileNameAndExtension()]
        
        for t in self.all_types:
            all_names.append(self.file_name + '.' + t)
    
        return all_names
    
    
    def getAbsolutePath(self, all_types=False):
        """Get the absolute path of the file path stored in this object.

        Note:
            If there is no root variables set it will return False because there
            is no way of knowing what the absolute path will be.
        
        Args:
            all_types=False (Bool): if set to True the absolute path of this object
                and any files associated with this file name will be returned.
        
        Returns:
            Absolute path of this object or a list containing the
                 absolute paths of all files associated with this file name.
        """
        if all_types and not self.all_types is None:
            all_names = self.getFileNameAndExtensionAllTypes()
            for i, n in enumerate(all_names):
                all_names[i] = PathHolder.getAbsolutePath(self, n)
            return all_names
        elif all_types and self.all_types is None:
            return [PathHolder.getAbsolutePath(self)] 
        else:
            return PathHolder.getAbsolutePath(self)
        
    
    def getRelativePath(self, all_types=False):
        """Returns the full relative path for this object.

        Most paths stated in tuflow model files are done with relative paths.
        If this is the case with the paths given to the constructor or set
        later this will return it, otherwise it will return False.
        
        Args:
            all_types=False (Bool): if set to True the relative path of this 
                object and any files associated with this file name will be 
                returned.
        
        Returns:
            Relative path of this object or a list containing the relative 
                paths of all files associated with this file name
                
        TODO:
            Is it a bit of a burden sending back either a single relative path
            OR a list if there's multiple files?
            
            I think this should be changed so that it always returns a list.
            that would be a lot easier for the calling code to deal with.
        """
        if all_types and not self.all_types is None:
            all_names = []
            for n in self.all_types:
                all_names.append(PathHolder.getRelativePath(self, False) + '.' + n)
            
            return all_names
        
        elif all_types and self.all_types is None:
            return [PathHolder.getRelativePath(self)]
        else:
            return PathHolder.getRelativePath(self)
        
        
    def getPathExistsAllTypes(self):
        """Checks that all the types associated with this path exist.

        Types are the associated file extensions. e.g. .shp, .dbf, etc.
        
        If paths don't exist list of the path types that cannot be found will
        be returned.
        
        Returns:
            True if the main path exists and either all the extensions 
                associated with this file exist or there are no other file
                extensions associated with it.
                False if the main file doesn't exist.
                list of missing name.extension values if some of the associated
                file extensions do not exist.
        
        TODO:
            This method returns too many different types. Perhaps it could 
            just always return a list with element[0] always set to be the
            main file or False if it doesn't exist?
        """
        # Check that the main path exists first. If not then there's not point
        # carrying on.
        if not self.getPathExists():
            return False
        
        # We know the path to this file exists already so it there are no other
        # file types to check we can return True.
        if self.all_types == None: 
            return True
        
        not_found = []
        for t in self.all_types:
            p = self.file_name + '.' + t
            if not self.getPathExists(p):
                not_found.append(self.file_name + '.' + t)

        if len(not_found) < 1:
            return True
        
        return not_found



gis_types = {'MI':('mif', 'mid'), 'Shape': ('shp', 'shx', 'dbf', 'prj')}
"""File type associations for the GisFile class"""

class GisFile(SomeFile): 
    """Extends the SomeFile class with GIS file specific behaviour.
    
    This behaviour includes: 
    defining the different file types (extensions) that should be associated
    with the file path for it to work and any command specific behaviour
    that is associated with GIS file types.
    """
    def __init__(self, global_order, path, hex_hash, type, command=None, 
                       root=None, parent_relative_root='', category=None,  
                       parent_hash=None, child_hash=None):
        """Constructor.

        Provides the all_types variable to SomeFile according to the file
        extension of the path. This will include the other files associated
        with the type of GIS file found.
        
        Args:
            path (str): the path to set for this object
            command (str): the command that was used to call this path in 
                the model file.
            root=None (str): the directory root to use to set the absolute path
               of this object.
        
        See Also:
            SomeFile
        """
        SomeFile.__init__(self, global_order, path, hex_hash, type, command,
                                root, parent_relative_root, category,  
                                parent_hash, child_hash)
        
        # Make sure that we know what all the other associated file types should
        # be for the type of GIS file we are creating. Sets the file category to
        # that defined by the key of the gis_types dictionary.
        for key in gis_types.keys():
            if self.extension in gis_types[key]:
                self.all_types = gis_types[key]
                self.category = key
                
                

data_types = {'TMF': ('tmf',), 'CSV': ('csv',)}
"""File type associations for the GisFile class"""

class DataFile(SomeFile):
    """Extends the SomeFile class with functionality needed for data files.

    Data files are considered to have data or links to other files in text
    format. 

    Class provides the all_types variable to SomeFile according to the
    file extensions of the path.
    
    The main use for this file type is for things like materials.tmf/.csv,
    Boundary conditions .csv files, etc.

    These files can be given as input to the ADataFileObject type classes for
    loading, updating and writing file specific data. This must be done 
    seperate to the main model load.
    
    See Also:
        DataFileComponent
        DataFileObject
    """
    
    def __init__(self, global_order, path, hex_hash, type, command=None, 
                       root=None, parent_relative_root='', category=None,  
                       parent_hash=None, child_hash=None):
        """Constructor.
                
        Args:
            path (str): the path as string to set for this object
            command (str): the command that was used to call this path in 
                the model file.
            root=None (str): the directory root to use to set the absolute 
                path of this object.
        
        See Also:
            SomeFile
        """
        SomeFile.__init__(self, global_order, path, hex_hash, type, command,
                                root, parent_relative_root, category,  
                                parent_hash, child_hash)
        # Make sure that we know what all the other associated file types should
        # be for the type of GIS file we are creating. Sets the file category to
        # that defined by the key of the gis_types dictionary.
        for m in data_types:
            if self.extension in data_types[m]:
                self.all_types = data_types[m]
                self.category = m
        
 