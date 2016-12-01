"""

 Summary:
    Contains file access functions and classes.

    This module contains convenience functions and classes for reading and 
    writing files and launching different types of File dialogue.
    
    Some of the functionality needed in this class is provided by the PyQt
    framework. When this module is loaded it tries to import the PyQt module.
    If it fails it sets a HAS_QT flag to False.
    
    Before any attempts to use the PyQt functions are made the HAS_QT flag
    is checked. If it's false the function will react.

 Author:  
     Duncan Runnacles
     
  Created:  
     01 Apr 2016
 
 Copyright:  
     Duncan Runnacles 2016

 TODO: This module, like a lot of other probably, needs reviewing for how
         'Pythonic' t is. There are a lot of places where generators,
         comprehensions, maps, etc should be used to speed things up and make
         them a bit clearer.
         
         More importantly there are a lot of places using '==' compare that
         should be using 'in' etc. This could cause bugs and must be fixed
         soon.

 Updates:

"""

from __future__ import unicode_literals

import os

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""

from ship.utils import utilfunctions as uf


HAS_QT = True
"""If Qt is not installed on the machine running the library we can't use any 
of the GUI related code, such as file dialogs. This flag informs the code in
the module about the load status.
"""

try:
    from ship.utils.qtclasses import MyFileDialogs
    
except Exception:
    logger.warning('Unable to load Qt modules - cannot launch file dialogues')
    HAS_QT = False
    
    
def getFile(file_path): 
    """Text file reader.

    Reads a text file, appending each new line to a list.
    
    Args:
        filePath (str): File path for text file to load.
    
    Returns:
        List - contents of text file split by new lines.
    
    Raises:
        IOError: if problem in reading file.
        TypeError: if string not given for file_path
    """
    file_contents = []
    line = ""

    try:
        with open(file_path, 'rU') as f:
            for line in f:
                file_contents.append(uf.encodeStr(line))
    except IOError:
        logger.error('Read file IOError')
        raise IOError ('Unable to read file at: ' + file_path) 
    except TypeError:
        logger.error('Read file TypeError')
        raise TypeError
        
    return file_contents
    
    
def writeFile(contents, file_path, add_newline=True):
    """Text file writer

    Writes a list to file, adding a new-line add the end of each list item.
    
    Args:
        contents (List) - lines to be written.
        filename (str) - Name of file to create.
        add_newline=True (Bool): adds a '\n' to the end of each line written
            if set to True.
    
    Raises:
        IOError: if problem in reading file.
        TypeError: if string not given for file_path
    """
    try:
        with open(file_path, 'w') as f:
            for line in contents:
                if add_newline:
                    f.write(line + '\n')
                else:
                    f.write(line)
    except IOError:
        logger.error('Write file IOError')
        raise IOError
    except TypeError:
        logger.error('Write file TypeError')
        raise TypeError
    
        
def directoryFileNames(path): 
    """Get a list of filenames in a directory.

    Args:
        path (str) - Path to directory.
    
    Returns:
        List - filenames in directory.
    
    Raises:
        IOError: If there's a problem with the read/write or the directory 
            doesn't exist
        TypeError: if string not given for file_path.
    """
    files = []
    
    try:
        for (dirpath, dirnames, filenames) in os.walk(path):
            files.extend(filenames)
            break
    except IOError:
        logger.error('Get directory names IOError')
        raise IOError
    except TypeError:
        logger.error('Get directory names TypeError')
        raise TypeError

    return files


def directoryDialog(path=''):
    """Launch a file dialog and return the user selected directory.

    If PyQt libraries are not available (HAS_QT == False) this function will
    raise an ImportError.
        
    Args:
        path (str): Optional -  directory to open the dialog in.
    
    Returns:
        Str containing path is successful or False if not.
    
    Raises:
        ImportError: if PyQt libraries are not available.
    """
    if not HAS_QT:
        logger.error('Qt libraries are not installed  - cannot launch file dialog')
        raise ImportError ('Qt libraries could not be imported - cannot launch dialogs')
    
    fd = MyFileDialogs()
    dir_path = fd.dirFileDialog(path)
    
    if not dir_path == '' and not dir_path == False:
        logger.debug('Chosen save path = ' + dir_path)
        return dir_path 
    else:
        logger.debug('No save path chosen in dialog')
        return False
    

def getOpenFileDialog(path='', types='All (*.*)', multi_file=True):
    """Launch an open  file dialog and return the user selected path.

    The file types should follow the format:
        'DAT (*.DAT);;TXT (*.txt);;IEF (*.IEF)'
    
    If PyQt libraries are not available (HAS_QT == False) this function will
    raise an ImportError.
        
    Args:
        path (str): Optional -  directory to open the dialog in.
        types (str): Optional - file types to restrict to. 
        multi_file=True(bool): If False user can only select a single file.
    
    Returns:
        Str containing path is successful or False if not.
    
    Raises:
        ImportError: if PyQt libraries are not available.
    """
    if not HAS_QT:
        logger.error('Qt libraries are not installed - cannot launch file dialog')
        raise ImportError ('Qt libraries could not be imported - cannot launch dialogs')
    
    fd = MyFileDialogs()
    open_path = fd.openFileDialog(path, file_types=types, multi_file=multi_file) 
    
    if not open_path == '' and not open_path == False:
        logger.debug('Chosen save path = ' + open_path)
        return open_path 
    else:
        logger.debug('No save path chosen in dialog')
        return False


def getSaveFileDialog(path='', types='All (*.*)'):
    """Launch a save file dialog and return the user selected path.

    The file types should follow the format:
        "DAT (*.DAT);;TXT (*.txt);;IEF (*.IEF)"
    
    If PyQt libraries are not available (HAS_QT == False) this function will
    raise an ImportError.
        
    Args:
        path (str): Optional -  directory to open the dialog in.
        types (str): Optional - file types to restrict to. 
    
    Returns:
        Str containing path is successful or False if not.
    
    Raises:
        ImportError: if PyQt libraries are not available.
    """
    if not HAS_QT:
        logger.error('Qt libraries are not installed - cannot launch file dialog')
        raise ImportError ('Qt libraries could not be imported - cannot launch dialogs')
    
    fd = MyFileDialogs()
    save_path = fd.saveFileDialog(path, file_types=types) 
    
    if not save_path == '' and not save_path == False:
        logger.debug('Chosen save path = ' + save_path)
        return save_path 
    else:
        logger.debug('No save path chosen in dialog')
        return False


    

"""
###############################                                                                         
  Path Functions and classes                                                 
###############################                                                                         
"""

def pathExists(path):
    """Test whether a path exists.

    Args:
        path (str):  the path to test. 
    
    Returns:
        True if the path exists or False if it doesn't.
    """
    if os.path.exists(path):
        return True
        
    return False


def finalFolder(path):
        """Get the last folder in the path.
        
        Args:
            path (str): the path to extract the final folder from.
        
        Returns:
            str containing the name of the final folder in the path.
        """
        return os.path.basename(os.path.normpath(path))
        
    
def setFinalFolder(path, folder_name):
        """Changes the final folder in the directory path to the given name.
        
        Args:
            path (str): the path to update.
            folder_name (str): the new name for the final folder in the path.
        
        Returns:
            str containing the updated path.
        """
        # Normalise the path so that we don't get any funny behaviour
        norm_path= os.path.normpath(path)

        # Get the drive letter
        drive_letter = os.path.splitdrive(norm_path)[0]

        # Separate out the different folders.
        # If it's an absolute path then we need to deal with the usual drive
        # letter problems (doesn't join it back with a slash.
        plist = norm_path.split(os.sep)
        if drive_letter:
            all_but_final_folder = plist[1:-1]
            all_but_final_folder = os.path.join(*all_but_final_folder)
            all_but_final_folder = plist[0] + os.path.sep + all_but_final_folder
            all_but_final_folder = os.path.normpath(all_but_final_folder)
        
        # Otherwise just remove the final folder so that we can replace it
        # with the new one.
        else:
            all_but_final_folder = plist[:-1]
            all_but_final_folder = os.path.join(*all_but_final_folder)
            
        # Add the new folder name to the end
        return os.path.join(all_but_final_folder, folder_name)
        

def getFileName(in_path, with_extension=False):
        """Return the file name with the file extension appended.
        
        Args:
            in_path (str): the file path to extract the filename from.
            with_extension=False (Bool): flag denoting whether to return 
                the filename with or without the extension.
    
        Returns:
            Str - file name, with or without the extension appended or a 
                 blank string if there is no file name in the path.
        """
        filename = os.path.basename(in_path)
        
        if os.path.sep in in_path[-2:] or (with_extension and not '.' in filename):
            return ''
        
        if with_extension:
            return filename
        else:
            filename = os.path.splitext(filename)[0]
            return filename
        

def directory(in_path):
    """Get the directory component of the given path.

    Checks the given path to see if it has a file or not. 
    
    If there is no file component in the path it will return the path as-is. 

    If there is no directory component in the file it will return a 
    blank string.
    
    Args:
        in_path (str): the path to extract the directory from.   
    
    Returns:
        Str - directory component of the given file path.
    
    TODO:
        Is there any way to tell if it's only a directory without being able to
        check that it exists and it doesn't end in a slash?
    
    """
    # If the path ends in one of the os designated separators, such as '\', 
    # '\\', or '/' then it's already the directory.
    sep = os.path.sep
    if sep in in_path[-2:]:
        return in_path
    
    dirname = os.path.dirname(in_path)
    return dirname


class PathHolder(object):
    """Class for storing file paths.
    
    This holds a range of useful path variables, such as:
    # file name
    # directory
    # full path
    # extension
    #etc
    
    Contains functions useful for extracting and updating parts of a file path.
    """
    
    # FilePathTypes constants
    ABSOLUTE, RELATIVE, DIRECTORY, NAME, EXTENSION, NAME_AND_EXTENSION = range(6) 

    def __init__(self, path, root=None):
        """Constructor.
        
        Args:
            path (str): the path to the file that this object holds the meta 
                data for.
            root (str): Optional - the path to the directory that is the root 
                of this file. Most tuflow files are referenced relative to the 
                file that they are called from. The root will allow for an 
                absolute path to be created from the relative path.
        """
#         if not isinstance(path, basestring):
#         if not type(path) in (str, unicode):
#             raise TypeError
        
        self.root = root
        self.relative_root = None
        self.filename = None
        self.extension = None
        self.path_as_read = None
#         self.parent_relative_root = ''
        
        self._setupVars(path)

    
    def _setupVars(self, path):
        """Sets up everything.
        
        Extracts everything that we need to get from the inputs given to the
        constructor. Including the directory, filename and extension.
        
        Args:
            path (str): the path to create this object for.
        """
        self.path_as_read = path = path.strip()
        
        if os.path.isabs(path): 
            root = directory(path)
            
            if self.root == None:
                self.root = root
            self.setFilename(getFileName(path, with_extension=True), True, True)
        else:
            self.relative_root = directory(path)
            self.setFilename(getFileName(path, True), True, True)
    
    
#     def getFinalFolder(self):
    def finalFolder(self):
        """Get the last folder in the path.

        If the relative_root variable is set it will be taken from that. 
        Otherwise if it is not and the root variable is set it will be taken 
        from that. If nether are set it will return False.
        
        Returns:
            tuple - the first part of the directory path and the final 
                folder in the directory path for this file, or False if the 
                variable has not been set.
        """
        final_folder = False
        if not self.relative_root == None and not self.relative_root == False:
            final_folder = finalFolder(self.relative_root)
        
        elif not self.root == None:
            final_folder = finalFolder(self.root)

        return final_folder
    
    
    def setFinalFolder(self, folder_name):
        """Changes the final folder in the directory path to the given name
        
        Args:
            folder_name (str): the new name for the final folder in the path.
        """
        if not self.relative_root == None and not self.relative_root == False:
            self.relative_root = setFinalFolder(self.relative_root, folder_name)
        elif not self.root == None:
            self.root = setFinalFolder(self.root, folder_name)
            
    
#     def getAbsolutePath(self, filename=None, relative_roots=[], normalize=True):
    def absolutePath(self, filename=None, relative_roots=[], normalize=True):
        """Get the absolute path of the file path stored in this object.

        If there is no root variables set it will return False because there
        is no way of knowing what the absolute path will be.
        
        Args:
            filename: Optional - if a different file name to the one 
                currently stored in this object is required it can be 
                specified with this variable.
        
        Returns:
            str - absolute path of this object.
        """
        if filename is None: 
            filename = self.filenameAndExtension()
        
        outpath = False
        if relative_roots and not self.root is None:
#         if not self.root == None and not self.relative_root == None:
            paths = [self.root] + relative_roots + [filename]
            if normalize:
                outpath = os.path.normpath(os.path.join(*paths))
            else:
                outpath = os.path.join(*paths)
#             return os.path.join(self.root, self.parent_relative_root, 
#                                         self.relative_root, filename)


#             if not filename == None:
#                 return os.path.join(self.root, self.parent_relative_root, 
#                                         self.relative_root, filename)
#             
#             else:
#                 return os.path.join(self.root, self.parent_relative_root,
#                             self.relative_root, self.filenameAndExtension())
        
#         elif not self.root == None and self.relative_root == None:
        elif not self.root is None:
            if normalize:
                outpath = os.path.normpath(os.path.join(self.root, filename))
            else:
                outpath = os.path.join(self.root, filename)
#             if not filename == None:
#                 return os.path.join(self.root, filename)
#             
#             else:
#                 return os.path.join(self.root, self.filenameAndExtension())
        
        return outpath
#         else:
#             return outpath
        
    
#     def getDirectory(self):
    def directory(self):
        """Get the directory of the file path stored in this object.

        This makes sure that the correct path, taking into consideration any
        relative path links to the main root, is returned.

        If there is no root variable set it will return False because there
        is no way of knowing what the absolute path should be.
        
        Returns:
            str - absolute path of this object without the file name, or
                 False if no root variables have been set.
        """
        if not self.root == None and not self.relative_root == None:
            return os.path.join(self.root, self.relative_root)
        
        elif not self.root == None and self.relative_root == None:
            return self.root
        
        else:
            return False
        
    
#     def getRelativePath(self, with_extension=True, filename=None):
    def relativePath(self, with_extension=True, filename=None):
        """Returns the full relative root with filename for this object.

        
        If a relative root was given to the constructor or set later this will 
        return it, otherwise it will return False.
        
        Args:
            with_extension=True (bool): append the extension to the end of the
                path if True.
            filename=None (str): if a different file name to the one 
                currently stored in this object is required it can be 
                specified with this variable.
        
        Returns:
            str - relative path of this object or False if there is no
                 relative path set.
        """            
        if not self.relative_root == None:
            
            if filename is None:
                if not with_extension:
                    return os.path.join(self.relative_root, self.filename)
                else:
                    return os.path.join(self.relative_root, self.filenameAndExtension())
            else:
                return os.path.join(self.relative_root, filename)
        
        return False
    
    
#     def getFileNameAndExtension(self):
    def filenameAndExtension(self):
        """Return the file name with the file extension appended.
        
        Returns:
            str - file name with the extension appended or a blank string if
                 the file name does not exist.
        """
        if self.filename and self.extension:
            return self.filename + '.' + self.extension
        elif self.filename:
            return self.filename
        else:
            return ''
        

#     def setPathsWithAbsolutePath(self, absolute_path, keep_relative_root=False):
    def setAbsolutePath(self, absolute_path, keep_relative_root=False):
        """Sets the absolute path of this object.
        
        Takes an absolute path and set the file variables in this object with
        it. 
        
        Note:
            This function WILL NOT check that the path exists. If the path used 
            to call this function must exist it is the responsibility of the 
            caller to check this.
            
        keep_relative_root variable information:

        If a relative root is not set to None it will be included in any path 
        that is returned by this object. i.e. when an absolute path is 
        returned by this object it will return: 
        
        path + relativepath + filename + extension
        
        Args:
            absolute_path (str): the new absolute path to use to set the file
                variables in this object.
            keep_relative_root=False (Bool): if a relative root exists for 
                this object it will be set to None unless this variable is 
                set to True.         """
        absolute_path = absolute_path.strip()
        self.root, filename = os.path.split(absolute_path)
        self.filename, ext = os.path.splitext(filename)
        self.extension = ext[1:]
        
        if not keep_relative_root:
            self.relative_root = None
    
    
#     def setFileName(self, filename, has_extension=False, keep_extension=False):
    def setFilename(self, filename, has_extension=False, keep_extension=False):
        """Updates the filename variables with the given file name.

        The caller can provide a filename with or without an extension and choose
        whether to keep the extension on the file or not.
        
        has_extension will only be checked if keep_extension == False.
        
        Args:
            filename (str): the new filename to set.
            has_extension=False (Bool): whether the filename has a file 
                extension or not. This should be set to True if an extension 
                exists. Otherwise the filename will be corrupted. 
            keep_extension: if the caller want to keep the extension on the 
               given filename this should be True. Otherwise the file extension
               on the new filename will be discarded.
        """
        filename = filename.strip()
        if keep_extension:
            self.filename, ext = os.path.splitext(filename)
            self.extension = ext[1:].lower()
        else:
            if has_extension:
                self.filename = os.path.splitext(filename)[0]
            else:
                self.filename = filename
            

#     def getPathExists(self, ext=None):
    def pathExists(self, ext=None):
        """Test whether the path exists..
        
        Note:
            If not self.root variable is set for this object then it is 
            impossible to know if the path exists or not, so it will always
            return False.

        Returns:
            True if the path exists or False if it cannot be found or there
                has not been a root variable set for this object.
        """
        if not self.root == None:
            path = self.root
           
            # If we have a relative root we need to use that as well. if the 
            # relative root shouldn't be used we will have had a new root set
            # and the relative root set to None in the setAbsolutePath()
            # function. 
            if not self.relative_root == None:
                path = os.path.join(path, self.relative_root)
            
            if ext == None:
                path = os.path.join(path, self.filenameAndExtension())
            else:
                path = os.path.join(path, self.filename + '.' + ext)
            if os.path.exists(path):
                return True
            
        return False
    
    
    
    
        