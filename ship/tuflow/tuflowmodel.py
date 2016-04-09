"""

 Summary:
     Container and main interface for accessing the Tuflow model and a class
     for containing the main tuflow model files (Tcf, Tgc, etc). Also includes
     the FilesFilter class. This is used to store standard function arguments
     for the majority of the methods in the TuflowModel class. It makes it 
     easier to set defaults for multiple method calls and improves the 
     readability of the method parameter lists.
     
     There are several other classes in here that are used to determine the
     order of the files in the model and key words for reading in the files.
     
     
     

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
import operator

from ship.tuflow.tuflowfilepart import SomeFile

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class FilesFilter(object):
    """Filter class to use when requesting file data from TuflowModel.
    
    This is for convenience to avoid multiple long method argument calls
    when dealing with TuflowModel methods that return file objects or 
    filenames.
    """
    
    def __init__(self, modelfile_type=[], content_type=None, 
                 filename_only=False, no_duplicates=False, 
                 in_model_order = False, all_types=False, with_extension=True):
        
        self.modelfile_type = modelfile_type
        """The type of model file to return for.
        
        This could be 'main', 'tcf', 'ecf', 'tgc', or 'tbc'.
        
        'main' returns only the main '.tcf' file. I.e. the tcf file that is
        called to load the model.
        
        If None all types will be returned.
        """
        
        self.content_type = content_type
        """ The type of filepart to return.
        
        This could be TuflowModel.GIS/MODEL/RESULT/etc.
        """
        
        self.filename_only = filename_only
        """Get the TuflowFilePart of only the filename."""

        self.no_duplicates = no_duplicates
        """Remove any duplicate filename entries."""
        
        self.in_model_order = in_model_order
        """Return in the order that the file parts were read in."""
        
        self.all_types = all_types
        """If True will return all associated file extensions (e.g. mid/mif)"""
        
        self.with_extension = with_extension
        """Include the file extension in the filename."""
        

    
class TuflowModel(object):
    """Container for the entire loaded tuflow model.
    
    Stores the details of all of the files and instruction lines in a 
    tuflow model. These are separated into two different sections:
    # files - the Tcf, Tgc, etc file objects.
    # file_parts - the components of the files. 
    
    To files dictionary contains sub dictionaries underneath keys for each of
    the type of file. These are:
    # tcf
    # tgc
    # tbc
    # ecf
    
    The file_parts are :class:'<TuflowFilePart>' instances.

    This class is the only object to hold the actual data found in the tuflow
    files (model variables, file paths, etc), within the file_parts dictionary.
    Any other references held by other classes are only hash codes that can 
    be used to access the actual data in the file_parts dict. This approach
    has been taken to avoid complications arising in having mutliple instances
    of the TuflowFilePart objects in many places. This can be complicated by,
    for instance, the tcf having a reference to a tgc, whicha has a reference
    to a TuflowFilePart (e.g. a Gis file command in the tgc file). If the 
    objects themselves were referenced by the the different TuflowModelFile's
    there would be multiple versions of the same TuflowFilePart held in 
    memory. In this case updating it would prove problematic and it would be
    easy to introduce bugs. This setup centralies the path and makes looking
    up the actual data simple. The hash codes held by the different model files
    are created during load time and will not change throughout the life of
    the TuflowModel object.
    """
    
    def __init__(self):
        """Initialise constants and dictionaries.
        """
        self.MODEL, self.RESULT, self.GIS, self.DATA, self.VARIABLE, \
        self.UNKNOWN_FILE, self.UNKNOWN, self.COMMENT = range(8)
        """Constants for accessing categories in class"""

        self.files = {}
        self.files['tcf'] = {}
        self.files['tgc'] = {}
        self.files['tbc'] = {}
        self.files['ecf'] = {}
        self.file_parts = {}
        
        self.model_order = None
        """Reference to a :class:'ModelOrder' object"""
        
        self.has_estry_auto = False
        """Boolean. If Estry files are referenced by the AUTO flag."""
        
        self.root = ''
        """The current directory path used to reach the run files in the model"""

        self.missing_model_files = []
        """Contains any tcf, tgs, etc files that could not be loaded."""
        
    
    def getPrintableContents(self):
        """Returns a dictionary of all the file contents ready to write to disk.
        
        Each dict entry contains a list. The list can be written to file by
        iterating and writing each entry as a new line.
        
        The lines already contain newline chars.
        
        Returns:
            Dict containing entries for each model file loaded.
        """
        orders = self.model_order.getRefOrder()
        output = {}
        for order in orders:
            filename = self.file_parts[order[0]].filepart.getAbsolutePath()
            output[filename] = self._getFilePrintableContents(self.files[order[1]][order[0]])
            
        return output
    

    def _getFilePrintableContents(self, model_file):
        """Get the printable contents from each file referenced by this class.
        
        Args:
            model_file(self.file): file to retrive the contents from.
            
        Results:
            List containing the entries in the model_file.
        """
        skip_codes = []
        output = []
        
        '''Read the order of the contents in the model file.
        [0] = the type of file part: MODEL, COMMENT, GIS, etc
        [1] = the hash_hex of the file part
        [2] = the comment contents (or None if it's not a comment section
        '''
        for entry in model_file.content_order:
            
            line_type = entry[0]
            hash_hex = entry[1]
            if hash in skip_codes: continue

            if line_type == self.COMMENT:
                output.append(''.join(entry[2]))
            else:
                f = self.file_parts[hash_hex].filepart 
                
                if f.category == 'ecf':
                    if self.has_estry_auto:
                        temp = ' '.join([f.command, 'Auto !', f.comment])
                        output.append(temp)
                else:
                    
                    # If there's piped files
                    if isinstance(f, SomeFile) and not f.child_hash is None:
                        out_line = []
                        has_children = True
                        out_line.append(f.getPrintableContents())
                        
                        # Keep looping through until there are no more piped files
                        while has_children:
                            if not f.child_hash is None:
                                f = self.f_parts[f.child_hash].fpart
                                out_line.append(f.getPrintableContents())
                                skip_codes.append(f.hex_hash)
                            else:
                                output.append(' | '.join(out_line) + '\n')
                                has_children = False
                            
                    else:
                        output.append(f.getPrintableContents() + '\n')
        
        return output
    

    def getModelFilesByAllTypes(self, files_filter):
        """Get all of the model files referenced by this instance.
        
        Args:
            files_filter(FilesFilter): containing parametres used to define 
                the output of the return values,
        
        See Also:  
            :class:'FilesFilter <FilesFilter>'
        """
        model_files = {}
        for f in self.files.keys():
            
            # If there's a KeyError it means there are no files of that type
            # so move on
            try:
                model_files[f] = self.getModelFilesByType(f, files_filter) 
            except KeyError:
                pass
        
        return model_files
        
    
    def getModelFilesByType(self, files_filter):
        """Get the file names for the given model type.
        
        If model_type left as the default 'main' it will return a list
        containing only the entry file value. i.e. either the tcf or ecf that
        was called to load the model.
        
        Args:
            files_filter(FilesFilter): settings class for determing the setup
                of the return values.
        
        Return:
            list - Either the TuflowModelFile's as found based on the 
                model_type provided, or the filenames for entry tcf/ecf file 
                if name_only=True.
        
        Raises:
            KeyError: when the given model_type does not exist.
            AttributeError: if the given model_type is None. 
                getModelFilesByAllTypes() function should be used in this case.
        
        See Also:
            :class: 'FilesFilter <FilesFilter>'
        """
        if not files_filter.modelfile_type:
            logger.error('FilesFilter.model_type == []: Use getModelFilesByAllTypes() function to return all types')
            raise AttributeError ('FilesFilter.model_type == []: Use getModelFilesByAllTypes() function to return all types')
            
        
        model_files = []
        if files_filter.modelfile_type == 'main':
            model_files = [self.file_parts[self.part_order[0]].filepart]
        else:
            for mtype in files_filter.modelfile_type:
                try:
                    file_type = self.files[mtype]
                except KeyError:
                    logger.error('Key %s does not exist in files' % (mtype))
                    raise ('Key %s does not exist in files' % (mtype))
                
                if not files_filter.filename_only: 
                    for val in file_type.values():
                        model_files.append(val)
                else:
                    for f in file_type:
                        model_files.append(self.file_parts[f].filepart)
            
        output = []
        if files_filter.filename_only:
            for m in model_files:
                output.append(m.getFileNameAndExtension())
            model_files = output
        
        return model_files
        
        
    def changeRoot(self, new_root):
        """Update the root value of all files.
        
        The root is the value of the directory path leading to the Tcf file 
        used to load the Tuflow model. 
        
        All files in this class contain a reference to this root value so it
        can be used to update their paths if it needs saving elsewhere or
        suchlike.
        
        """
        for part in self.file_parts.values():
            if part.isSomeFile():
                part.filepart.root = new_root
        
        self.root = new_root 
    
    
    def testExists(self):
        """Tests all of the files referenced by this model to see if they exist.
        
        Does not check the self.RESULT entry as this will always show false as
        it doesn't have a file.
        
        Returns:
            list of tuples: (hex hash, filename.ext, root path) for each file
                that doesn't exist or an empty list if all exist.
        """
        missing = []
        for hash_hex, part in self.file_parts.iteritems():
            
            if part.isSomeFile():
                if not part.part_type == self.RESULT:
                    p = part.filepart.getAbsolutePath() # DEBUG
                    if not os.path.exists(part.filepart.getAbsolutePath()):
                        missing.append((hash_hex, part.filepart.getFileNameAndExtension(), part.filepart.root))
        
        return missing
    
    
    def getFileNames(self, files_filter, extensions=[]):
        """Return file names referenced by this class.
        
        If no options are given all files referenced by this object will be
        returned.
        
        Args:
            content_type(int): class constant defining which type of file to
                return (e.g self.GIS).
            file_type(str): Optional - the str denoting a specific type of file
                to interogate (e.g. 'tbc').
            all_types=False(Bool): If True it will return all file extensions
                associated with the name (e.g. mid, mif). Always return name
                + extension, i.e. with_extension has no affect.
            with_extension=False(Bool): If True, returns the file extension
                appended to the name. 
            extensions=[](list): If set returns only the files with the 
                given extensions.
            in_order=False(Bool): if True the selected parts will be return in
                the order that they were loaded.
            no_duplicates=False(Bool): Remove all duplicated entries from
                the output list.
                
        Returns:
            List - filenames found.
            
        Note:
            Attempts to return all file names, which include the result files,
            which can be emtpy strings i.e. may not have an actual filename
            as they are only a directory.
        """
        contents = self.getContents(files_filter.content_type, files_filter.modelfile_type, 
                                    extensions, files_filter.in_model_order,
                                    files_filter.no_duplicates)
        
        files = [f for f in contents if isinstance(f, SomeFile)]
        
        filenames = []
        for f in files:
            
            if files_filter.all_types:
                ftypes = f.getFileNameAndExtensionAllTypes()
                for ftype in ftypes:
                    if ftype == '': continue  # This can be blank for result/check files
                    filenames.append(ftype)
            else:
                if files_filter.with_extension:
                    fname = f.getFileNameAndExtension()
                    if fname == '': continue 
                    filenames.append(fname)
                else:
                    fname = f.file_name
                    if fname == '': continue 
                    filenames.append(fname)
        
        return filenames
                
                
    def getAbsolutePaths(self, files_filter, extensions=[]): #content_type=None, file_type=None, all_types=False):
        """
        """
        contents = self.getContents(files_filter.content_type, 
                                    files_filter.modelfile_type, extensions,
                                    files_filter.in_model_order, 
                                    files_filter.no_duplicates)
        filenames = []
        if files_filter.all_types:
            for f in contents:
                if isinstance(f, SomeFile):
                    rel_paths = f.getAbsolutePath(all_types=True)
                    for r in rel_paths:
                        filenames.append(r)
        else:
            for f in contents:
                if isinstance(f, SomeFile):
                    filenames.append(f.getAbsolutePath())
        return filenames
        

    def getContents(self, content_type=None, modelfile_type=[], extensions=[],
                                        in_order=False, no_duplicates=False):
        """Get the objects stored by this tuflow model.
        
        If no options are given allfile parts referenced by this object will be
        returned.
        
        Args:
            content_type(int): class constant defining which type of file to
                return (e.g self.GIS).
            file_type(str): Optional - the str denoting a specific type of model
                file to interogate (e.g. 'tbc').
            extensions=[](list): If set returns only the files with the 
                given extensions.
            in_order=False(Bool): if True the selected parts will be return in
                the order that they were loaded.
            no_duplicates=False(Bool): Only call if setting content_type to a
                SomeFile type (GIS, MODEL, DATA - Not VARIABLE). Removes any
                duplicate file entries. Useful if, for example, there are 
                multiple calls the same file, such as a boundary conditions 
                file and you only want a single reference.
                
        Returns:
            List - TuflowFilePart's found.
        """
        extensions = [x.upper() for x in extensions]        
        
        content = []
        if not modelfile_type:
            if content_type is None:
                content = [c.filepart for c in self.file_parts.values()] 
            else:
                content = [c.filepart for c in self.file_parts.values() if c.part_type == content_type]
        
        else:
            hashes = None
            for mtype in modelfile_type:
                if mtype in self.files:
                    
                    # If file type has no entries
                    if not self.files[mtype]:
                        return []
                    
                    hashes = [f.getHashCategory(content_type) for f in self.files[mtype].values()][0]
                else:
                    hashes = []
                    for file_type in self.files:
                        hashes += [f.getHashCategory(content_type) for f in self.files[file_type].values()][0]

                content = [self.file_parts[x].filepart for x in hashes]
        
        # If only SomeFile types with a certain extension are wanted.
        if len(extensions) > 0:
            temp = []
            for c in content:
                if isinstance(c, SomeFile):
                    if c.extension.upper() in extensions:
                        temp.append(c)
            content = temp
        
        # Order list by global_order if requested
        if in_order:
            self._orderByGlobal(content)
        
        # Remove any duplicate file names if requested
        # Only works for SomeFile type objects
        if no_duplicates and not content_type == self.VARIABLE:
            content = self._removeDuplicateFilenames(content)

        return content

    
    def _orderByGlobal(self, in_list, reverse=False):
        """Order list by global_order attribute of TuflowFilePart.
        
        Args:
            in_list(list): list to sort.
            revers=False(Bool): if True return list descending.
        
        Return:
            List sorted by global_order variables of TuflowFilePart.
        """
        in_list.sort(key=operator.attrgetter('global_order'), reverse=reverse)
        return in_list

    
    def _removeDuplicateFilenames(self, in_list):
        """Removes duplicate entries from the given list.
        
        Args:
            in_list(list): list to remove duplicates from.
        
        Return::
            list - with duplicates removed.
        """
        seen = {}
        result = []
        for item in in_list:
            if not isinstance(item, SomeFile): continue
            marker = item.getFileNameAndExtension()
            if marker in seen: continue
            seen[marker] = 1
            result.append(item)
        
        return result
        
        

class ScenarioScope(object):
    """
    """
    
    def __init__(self, name):
        """
        """
        self.name = name
        self.scoped_hashcodes = []
        self.scoped_ifelse = []
    
    
    

class TuflowTypes(object):
    """Contains key words from Tuflow files for lookup.
    
    This acts as a lookup table for the TuflowLoader class more than anything
    else. It is kept here as that seems to be most sensible.
    
    Contains methods for identifying whether a command given to it is known
    to the library and what type it is. i.e. what category it falls into.
    """
    
    def __init__(self):
        """Initialise the categories and known keywords"""

        self.MODEL, self.RESULT, self.GIS, self.DATA, self.VARIABLE, \
        self.UNKNOWN_FILE, self.UNKNOWN, self.COMMENT = range(8)
        
        self.types = {}
        self.types[self.MODEL] = ['GEOMETRY CONTROL FILE', 'BC CONTROL FILE',
                                  'READ_FILE',
                                  'ESTRY CONTROL FILE', 'READ RESTART FILE']
        self.types[self.RESULT] = ['OUTPUT FOLDER', 'WRITE CHECK FILES',
                                   'LOG FOLDER']
        self.types[self.GIS] = ['READ MI', 'READ GIS', 'READ GRID',
                                'SHP PROJECTION', 'MI PROJECTION']
        self.types[self.DATA] =  ['READ MATERIALS FILE', 
                                  'BC DATABASE']
        self.types[self.VARIABLE] =  ['START TIME', 'END TIME', 'TIMESTEP',
                                'SET IWL', 'MAP OUTPUT INTERVAL', 
                                'MAP OUTPUT DATA TYPES', 'CELL WET/DRY DEPTH',
                                'CELL SIDE WET/DRY DEPTH', 'SET IWL',
                                'TIME SERIES OUTPUT INTERVAL',
                                'SCREEN/LOG DISPLAY INTERVAL', 'CSV TIME',
                                'START OUTPUT', 'OUTPUT INTERVAL',
                                'STRUCTURE LOSSES', 'WLL APPROACH',
                                'WLL ADJUST XS WIDTH', 'WLL ADDITIONAL POINTS',
                                'DEPTH LIMIT FACTOR', 'BC EVENT TEXT',
                                'BC EVENT NAME', 'CELL SIZE', 'SET CODE',
                                'GRID SIZE (X,Y)', 'SET ZPTS', 'SET MAT',
                                'MASS BALANCE OUTPUT', 'GIS FORMAT']
        
        
    def find(self, find_val, file_type='*'):
        """Checks if the given value is known or not.
        
        The word to look for doesn't have to be an exact match to the given
        value, it only has to start with it.
        
        This helps to avoid unnecessary repatition. i.e. many files are like:
        'READ GIS' + another word. All of them are GIS type files so they all
        get dealt with in the same way.
        
        Args:
            find_val (str): the value attempt to find in the lookup table.
            file_type (int): Optional - reduce the lookup time by providing 
                the type (catgory) to look for the value in. These are the
                constants (MODEL, GIS, etc).
        
        Returns:
            Tuple (Bool, int) True if found. Int is the class constant 
                indicating what type the value was found under.
        """ 
        find_val = find_val.upper()
        if file_type == '*':
            for key, part_type in self.types.iteritems():
                found = [i for i in part_type if find_val.startswith(i)]
                if found:
                    return True, key
            return (False, None)
        else:
            found = [i for i in self.types[file_type] if i.startswith(find_val)]
            if found:
                return True, file_type
            return (False, None)



class ModelOrder(object):
    """Graph for storing the order of the model files in.
    
    The order is based on how they are added and how they define their parent
    node.
    
    Only hex hash values are stored here to use to reference back to other data
    elsewhere. 
    
    This is also just for the main model files (Tcf, Tgc, etc).
    
    When a node is added it declares it's parents hash hex. This will be 
    looked up. If it exists the node will be added to the parent nodes 
    children.
    """
    
    def __init__(self):
        """Constructor"""
        self.root_hex = None
        self.model_refs = {}
    

    def addRef(self, model_ref, is_root=False):
        """Add a new node to the graph.
        
        Args:
            model_ref (:class: 'ModelRef'): the ModelRef object containing the
                hex details, children, and parent. 
            is_root=False (Bool): True if this is the root node.
        """
        self.model_refs[model_ref.hex_hash] = model_ref
        if is_root:
            self.root_hex = model_ref.hex_hash
        if not model_ref.parent_hash is None:
            self.model_refs[model_ref.parent_hash].children.append(
                                                            model_ref.hex_hash)
    
    def getRef(self, hex_hash):
        """Get the ModelRef object referenced by the hex hash.
        
        Args:
            hex_hash(hex): a hexidecimal hash to lookup.
        Returns:
            :class:'ModelRef' object referenced by the given hex hash. 
        """
        return self.model_refs[hex_hash]
    

    def getRefOrder(self): 
        """Get the order of all of the references in the class.
        
        Puts the root node hex hash in the order list and then calls the
        recursive :method:'_findAllSubRefs' function to walk the graph and
        add all of the files in order.
        
        Returns:
            List containing the hex hash values of all the nodes in order.
        """
        order = []
        order.append([self.root_hex, self.model_refs[self.root_hex].extension])
        order = self._findAllSubRefs(order, self.root_hex)
        return order
    

    def _findAllSubRefs(self, order, model_ref):
        """Recursive function to extract the hex hashes of all the nodes in order.
        
        Args:
            order(List): list to update with the new entries.
            model_ref(hex): hex hash value to interogate.
        
        Returns:
            List containing the hex values.
        """
        for child in self.model_refs[model_ref].children:
        
            order.append([child, self.model_refs[child].extension])
            self._findAllSubRefs(order, child)
        
        return order


class ModelRef(object):
    """Contains the details of each model files associations.
    
    Each :class:'TuflowModel' file has one of these to track its associations.
    
    Keeps track of the calling file (parent) and any files that it calls (its
    children), as well as its own hex hash value.
    """
    
    def __init__(self, hex_hash, extension, parent_hash=None):
        """Set the values.
        
        Args:
            hex_hash(hex): hex hash value for the model file.
            extension(str): the file extenion of the model type. This can be 
                used to find what type of model file it is.
            parent_hash(hex): Optional - the hex hash of the parent if it has 
                one. Although this can be None, all except the root node
                should have one.
        """
        self.children = []
        self.hex_hash = hex_hash
        self.parent_hash = parent_hash
        self.extension = extension


    def addChild(self, hex_hash):
        """Adds a reference to a child ModelRef.
        
        Args:
            hex_hash(hex): the hex hash reference of the child.
        """
        self.children.append(hex_hash)
        
        
