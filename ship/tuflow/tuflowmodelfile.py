"""

 Summary:
     Container for the main tuflow model files (tcf/tgc/etc).
     
     This class is used to store the order of items in the file and any data
     that is not understood by the tuflowloader e.g. commented sections and
     components of the file that are not specifically listed.
     
     If does not store the data directly, just the hash codes for the file
     parts so that they can be cross referenced against the 
     TuflowModel.file_parts dictionary.
     
     The ModelFileEntry class is also kept in this module. This provides simple 
     access to main variables held by the TuflowFilePart objects.

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

from ship.tuflow.tuflowfilepart import TuflowFile
from ship.tuflow import FILEPART_TYPES as ft

        

class TuflowModelFile(object):
    """ Contains data pertaining to TUFLOW model files.
    
    The main model files that are loaded by TUFLOW, e.g. Tcf, Tgc, etc, have
    their meta data and references to their contents stored in this class.
    
    Contains a list denoting the order of the file and any lines that are 
    either comments or not recognised by the loader.
    
    Other, known, file commands are stored in the approproate object (instances
    of :class: 'TuflowFilePart') and their hash key is stored in this list.
        
    See Also:
        :class: 'TuflowFile <ship.tuflow.tuflowfilepart.TuflowFile>'
        :module: 'tuflowfilepart <ship.tuflow.tuflowfilepart>'
    """

    def __init__(self, category, hex_hash, parent_hash):
        """Constructor.

        Checks if the path to the file is absolute. If it doesn't it converts
        it. If the absolute path doesn't exist an error will be raised.

        Args:
            category (str): a type variable denoting which form of model file this
                is. E.g. tcf, tgc, etc.
            hex_hash(str): a unique hexidecimal hash code.
            parent_hash(str): the unique code of the file that created this
                model file (e.g. if this was a tgc referenced by a tcf the
                parent would be the tcf file).
        """
        self.TYPE = category
        self.hex_hash = hex_hash
        self.parent_hash = parent_hash
        self.contents = []

    
    def addContent(self, line_type, filepart): 
        """Add an entry to the content_order list.
        
        Entries are added in order so that the order can be maintained.
        
        This could be either a reference (hash code) for a 
        :class:'TuflowFilePart' type object or actual contents. The actual 
        contents are sent if the line is a comment or isn't known by the
        loader.
        
        Args:
            line_type (int): denotes the code to store the entry under. This is
                one of the constants in :class:'TuflowModel' (GIS, MODEL, etc).
            hex_hash (hex): the unique hex value of the line hash used to 
                identify all parts of the tuflow model.
        """
        self.contents.append([line_type, filepart])
 
    
    def getEntryByHash(self, hex_hash):
        """Return the TuflowFilePart referenced by a particular hash code. 
        
        Args:
            hex_hash(str): the hash code.
        
        Return:
            TuflowFilePart
            
        Raises:
            KeyError - if no part was found with the given hash code.
            
        """
        for c in self.contents:
            if c[0] == ft.UNKNOWN or c[0] == ft.COMMENT: continue
            if c[1].hex_hash == hex_hash:
                return c[1]
        else:
            raise KeyError ("No entry found with hex_hash: " + hex_hash)
    
    
    def testExists(self):
        """Tests each file to see if it exists.
        
        Returns:
            list - containing tuple's (filename, absolute path) of any files
                that do not exist.
        """
        failed = []
        for c in self.contents:
            if isinstance(c[1], TuflowFile):
                p = c[1].getAbsolutePath()
                if c[0] == ft.RESULT:
                    continue
                else:
                    if not os.path.exists(p):
                        failed.append([c[1].getFileNameAndExtension(), 
                                       os.path.normpath(p)])
        
        return failed
    
    
    def getFiles(self, file_type=None, extensions=[], include_results=True):
        """Get the TuflowFile objects referenced by this object.
        
        Args:
            file_type=None(FILEPART_TYPE): the type of file to return (e.g.
                MODEL, GIS, etc)
            extension=None(str): if supplied only files with the given extension
                will be included.
            include_results=True(bool): if False any output files will be
                excluded, such as outputs, check files, log files.
        
        Return:
            list - containing TuflowFile objects.
        """
        output = []
        for c in self.contents:
            if isinstance(c[1], TuflowFile):
                
                if not file_type is None and not c[0] == file_type: 
                    continue
                elif not include_results and c[0] == ft.RESULT:
                    continue
                else:
                    if extensions and not c[1].extension in extensions:
                        continue
                    output.append(c[1])
        
        return output
    
    
    def getFileNames(self, file_type=None, extensions=[], with_extension=True, 
                     all_types=False, include_results=True):
        """Get all of the file names for TuflowFile object in this class.
        
        This is a convenience method. It calls the getFiles method and extracts
        the file name from the TuflowFile's.
        
        Args:
            file_type=None(FILEPART_TYPE): the type of file to return (e.g.
                MODEL, GIS, etc)
            extension=None(str): if supplied only files with the given extension
                will be included.
            with_extension=True(bool): if True the file extension will be 
                included in the return values.
            include_results=True(bool): if False any output files will be
                excluded, such as outputs, check files, log files.
        
        Return:
            list - containing file names as strings.
        """
        files = self.getFiles(file_type, extensions, include_results)
        
        output = []
        if with_extension:
            if all_types:
                for f in files:
                    output.extend(f.getFileNameAndExtensionAllTypes())
            else:
                output = [f.getFileNameAndExtension() for f in files]
        else:
            output = [f.file_name for f in files]
        
        return output
    
    
    def getAbsolutePaths(self, file_type=None, extension=None, all_types=False):
        """Get all of the absolute paths for TuflowFile objects in this class.
        
        This is a convenience method. It calls the getFiles method and extracts
        the absolute path from the TuflowFile's.
        
        Args:
            file_type=None(FILEPART_TYPE): the type of file to return (e.g.
                MODEL, GIS, etc)
            extension=None(str): if supplied only files with the given extension
                will be included.
            include_results=True(bool): if False any output files will be
                excluded, such as outputs, check files, log files.
        
        Return:
            list - containing absolute paths as strings.
        """
        files = self.getFiles(file_type, extension)
        files = [f.getAbsolutePath(all_types=all_types) for f in files]

        return files
            

    def getRelativePaths(self, file_type=None, extension=None, all_types=False):
        """Get all of the relative paths for TuflowFile objects in this class.
        
        This is a convenience method. It calls the getFiles method and extracts
        the relative path from the TuflowFile's.
        
        Args:
            file_type=None(FILEPART_TYPE): the type of file to return (e.g.
                MODEL, GIS, etc)
            extension=None(str): if supplied only files with the given extension
                will be included.
            include_results=True(bool): if False any output files will be
                excluded, such as outputs, check files, log files.
        
        Return:
            list - containing relative paths as strings.
        """
        files = self.getFiles(file_type, extension)
        files = [f.getRelativePath(all_types=all_types) for f in files]

        return files
    
    
    def getVariables(self):
        """Get all of the ModelVariable's referenced by this object.
        
        Return:
            list - of ModelVariable's.
        """
        output = []
        for c in self.contents:
            if c[0] == ft.VARIABLE:
                output.append(c[1])
        
        return output
    


    
    
    