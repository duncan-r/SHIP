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

from ship.tuflow.tuflowfilepart import TuflowFile, ModelVariables
from ship.tuflow.tuflowmodelfile import TuflowModelFile
from ship.tuflow import FILEPART_TYPES as ft

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


    
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
    
    
    """
    
    def __init__(self):
        """Initialise constants and dictionaries.
        """

        self.files = {}
        self.files['tcf'] = {}
        self.files['tgc'] = {}
        self.files['tbc'] = {}
        self.files['ecf'] = {}
        
        self.model_order = None
        """Reference to a :class:'ModelOrder' object"""
        
        self.has_estry_auto = False
        """Boolean. If Estry files are referenced by the AUTO flag."""
        
        self.root = ''
        """The current directory path used to reach the run files in the model"""

        self.missing_model_files = []
        """Contains any tcf, tgs, etc files that could not be loaded."""
        
        self.mainfile = []
        """"""
        
        self.scenario_vals = {}
        """Key, value pairs for scenarios handed in when loading the model."""

        self.event_vals = {}
        """Key, value pairs for events handed in when loading the model."""
        
    
    def getPrintableContents(self):    
        """Get the TuflowModel ready to write to disk.
        
        Returns a dictionary with the absolute path of the different model
        files making up the model as keys and a list containing the lines of
        the files (with newline characters appended) as the values.
        
        Return:
            dict.
        """
        order = self.model_order.getRefOrder()
        output = {}
        for o in order:
            
            if o[2] is None:  # It's the root of the order tree
                model_file = self.mainfile
            else:
                model_file = self.files[o[3]][o[2]].getEntryByHash(o[0])
            output[model_file.getAbsolutePath()] = self.files[o[1]][o[0]].getPrintableContents(self.has_estry_auto)
        
        return output
    
    
    def getAllScenarioVariables(self):
        """Return all scenario variables found in control files.
        
        Return:
            list - containing all of the scenario variables in the control files.
        """
        variables = []
        for model_file_type in self.files.values():
            for model_file in model_file_type.values():
                variables.extend(model_file.getScenarioVariables())
        
        return variables

    
    def getTuflowFilePartsByScenario(self, scenario_vals):
        """Get all the TuflowFilePart's that are within the given scenario params.
        
        Note:
            To get a list of all of the available scenario variables you can
            use the getAllScenarioVariables method.
        
        Args:
            scenario_vals(list): str's representing the scenario variables that
                will be used to identify the TuflowFilePart's to return.
                
        Return:
            list - of TuflowFilePart's that are with the scenario blocks defined
                by the given scenario_vals.
        """
        file_parts = []
        for model_file_type in self.files.values():
            for model_file in model_file_type.values():
                file_parts.extend(model_file.getContentsByScenario(scenario_vals))
        
        return file_parts
    
    
    def getSetScenarioVals(self):
        """Returns the varible dict given to load the model."""
        return self.scenario_vals
    
    
    def changeRoot(self, new_root):
        """Update the root value of all files.
        
        The root is the value of the directory path leading to the Tcf file 
        used to load the Tuflow model. 
        
        All files in this class contain a reference to this root value so it
        can be used to update their paths if it needs saving elsewhere or
        suchlike.
        
        """
        for model_file_type in self.files.values():
            for model_file in model_file_type.values():
                for content in model_file.contents:
                    if isinstance(content[1], TuflowFile):
                        content[1].root = new_root
        
        self.mainfile.root = new_root
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
        for model_file_type in self.files.values():
            for model_file in model_file_type.values():
                missing.extend(model_file.testExists())
                        
        return missing
    
    
    def getVariables(self, no_duplicates=False):
        """Get ModelVariable's included in the model.
        
        Args:
            no_duplicates=False(bool): if set to True any duplicate variables
                will be removed. This is based on the command. The last call to
                that command will be the one returned.
        """
        output = []
        for model_file_type in self.files.values():
            for model_file in model_file_type.values():
                output.extend(model_file.getVariables())
        
        
        if no_duplicates:
            output = self.orderByGlobal(output, reverse=True)
            output = self.removeDuplicateVariables(output)
            output = self.orderByGlobal(output, reverse=False)
        else:
            output = self.orderByGlobal(output, reverse=False)
        
        return output
    
    
    def getFiles(self, file_type=None, no_duplicates=False, include_results=True):
        """Get TuflowFile's included in the model.
        
        Args:
            file_type=None(FILEPART_TYPE): the type of file to return (e.g.
                MODEL, GIS, etc)
            no_duplicates=False(bool): the same file can be called multiple
                times in Tuflow configuration files for different purposes.
                If True this will only return one instance of it.
            include_results=True(bool): will exclude any output files from the list.
                Output, Check and Log files are often only a path without a 
                filename. If name_only=True is used it will return blank
                filenames. Setting this to False means they will be ignored.
        
        Return:
            list - containing the matching TuflowFile's.
        """
        output = []
        for model_file_type in self.files.values():
            for model_file in model_file_type.values():
                output.extend(model_file.getFiles(file_type, 
                                                  include_results=include_results))
        
        output = self.orderByGlobal(output)
        
        if no_duplicates:
            output = self.removeDuplicateFiles(output)
        
        return output
    
    
    def getFilePaths(self, file_type=None, no_duplicates=False, in_order=False, 
                      name_only=False, include_results=True):
        """Get the absolute file paths of all TuflowFile objects in the model.
        
        Args:
            file_type=None(FILEPART_TYPE): the type of file to return (e.g.
                MODEL, GIS, etc)
            no_duplicates=False(bool): the same file can be called multiple
                times in Tuflow configuration files for different purposes.
                If True this will only return one of them.
            in_order=False(bool): if True the file paths will be returned in
                the order that they are read by Tuflow.
            name_only=False(bool): if True only the filename rather than the
                complete absolute path will be returned.
            include_results=True(bool): will exclude any output files from the list.
                Output, Check and Log files are often only a path without a 
                filename. If name_only=True is used it will return blank
                filenames. Setting this to False means they will be ignored.
        
        Return:
            list - containing the matching paths.
        """
        output = []
        files = self.getFiles(file_type=file_type, include_results=include_results)

        if in_order:
            files = self._orderByGlobal(files)
        
        if no_duplicates:
            output = self._removeDuplicateFilenames(output)

        if name_only:
            output = [i.getFileNameAndExtension() for i in files]
        else:
            output = [i.getAbsolutePath() for i in files]

        return output
        
                
    def getTuflowModelFiles(self):
        """Returns the TuflowModelFile objects.
        
        TuflowModelFile's are containers for all of the main model files (tcf,
        tgc, tbc, ecf) in the TuflowModel. They contain all of the TuflowFile,
        ModelVariable and any unknown contents (like comments) loaded.
        
        See Also:
            getModelFiles - which returns the TuflowFile references for each
                of the TuflowModelFile's in the TuflowModel.  
            
            getTMFFromTuflowFile - return the TuflowModelFile object associated
                with a TuflowFile of FILEPART_TYPES.MODEL.  
            
            getTuflowFileFromTMF - return the TuflowFile object associated with
                a TuflowModelFile of FILEPART_TYPES.MODEL.
        
        Return:
            dict - keys are the TuflowModelFile category (tcf, tcf, etc) and
                the values are lists of tuples (TuflowModelFile, filename). As
                the TuflowModelFile does not contain it's own TuflowFile 
                reference it's filename is returned for reference.
        """
        output = {'tcf': [], 'ecf': [], 'tgc': [], 'tbc': []}
        for key, val in self.files.iteritems():
            for tmf in val.values():
                name = self.getTuflowFile(tmf).getFileNameAndExtension()
                output[key].append([tmf, name])
        
        return output
        

    def getModelFiles(self):
        """Returns the TuflowFiles corresponding to each of the TuflowModelFile's.
        
        These are the values that are loaded under FILEPART_TYPES.MODEL. This
        function only returns the TuflowFile (TuflowFilePart subclass), it 
        does not contain any references to other files they refer to.
        
        See Also:
            getTuflowModelFiles - which will return a container referencing all
                of the contents of the tcf, tgc, etc file.  
                
            getTMFFromTuflowFile - return the TuflowModelFile object associated
                with a TuflowFile of FILEPART_TYPES.MODEL.  
            
            getTuflowFileFromTMF - return the TuflowFile object associated with
                a TuflowModelFile of FILEPART_TYPES.MODEL.
        
        Return:
            dict - keys are the TuflowModelFile category (tcf, tgc, etc). Values
                are the TuflowFiles for that type.
        """
        output = {'tcf': [], 'ecf': [], 'tgc': [], 'tbc': []}
        output[self.mainfile.category].append(self.mainfile)
        for model_file_type in self.files.values():
            for model_file in model_file_type.values():
                files = model_file.getFiles(ft.MODEL)
                
                for f in files:
                    output[f.category].append(f)
        
        return output

    
    def getTMFFromTuflowFile(self, tuflowfile):
        """Get the TuflowModelFile associated with the given TuflowFile.
        
        Tuflow control files (tcf, tgc, etc) are represented in two ways. They
        are TuflowFile's like any other file and they are TuflowModelFile's
        which are containers for the other data they hold.
        
        This is a convenience function to access the TuflowFile from a given
        TuflowModelFile. 
        
        Args:
            tuflowfile(TuflowFile): 
            
        Return:
            TuflowModelFile.
        
        Raises:
            AttributeError - if tuflowfile is not an instance of TuflowFile or
                it is not of type FILEPART_TYPES.MODEL.
        """
        if not isinstance(tuflowfile, TuflowFile):
            raise AttributeError
        if not tuflowfile.TYPE == ft.MODEL:
            raise AttributeError
        
        for model_file_type in self.files.values():
            for model_file in model_file_type.values():
                if model_file.hex_hash == tuflowfile.hex_hash:
                    return model_file
    
    
    def getTuflowFileFromTMF(self, tuflowmodelfile):
        """Get the TuflowFile associated with the given TuflowModelFile.
        
        Tuflow control files (tcf, tgc, etc) are represented in two ways. They
        are TuflowFile's like any other file and they are TuflowModelFile's
        which are containers for the other data they hold.
        
        This is a convenience function to access the TuflowModelFile from a given
        TuflowFile. 
        
        Args:
            tuflowmodelfile(TuflowModelFile): 
            
        Return:
            TuflowFile.
        
        Raises:
            AttributeError - if tuflowmodelfile is not an instance of 
                TuflowModelFile. 
        """
        if not isinstance(tuflowmodelfile, TuflowModelFile):
            raise AttributeError
        
        if tuflowmodelfile.parent_hash is None:
            return self.mainfile
        
        for key, val in self.files.iteritems():
            for h, tmf in val.iteritems():
                if h == tuflowmodelfile.parent_hash:
                    return tmf.getEntryByHash(tuflowmodelfile.hex_hash)
        
        return False
    
    
    def orderByGlobal(self, in_list, reverse=False):
        """Order list by global_order attribute of TuflowFilePart.
        
        Args:
            in_list(list): list to sort.
            revers=False(Bool): if True return list descending.
        
        Return:
            List sorted by global_order variables of TuflowFilePart.
        """
        in_list.sort(key=operator.attrgetter('global_order'), reverse=reverse)
        return in_list


    def removeDuplicateVariables(self, in_list):
        """Removes duplicate entries from the given TuflowVariable list.
        
        Args:
            in_list(list): list to remove duplicates from.
        
        Return::
            list - with duplicates removed.
        """
        seen = {}
        result = []
        for item in in_list:
            if not isinstance(item, ModelVariables): continue
            marker = item.command
            if marker in seen: continue
            seen[marker] = 1
            result.append(item)
        
        return result
        
    
    def removeDuplicateFiles(self, in_list):
        """Removes duplicate entries from the TuflowFile list.
        
        Args:
            in_list(list): list to remove duplicates from.
        
        Return::
            list - with duplicates removed.
        """
        seen = {}
        result = []
        for item in in_list:
            if not isinstance(item, TuflowFile): continue
            marker = item.getFileNameAndExtension()
            if marker in seen: continue
            seen[marker] = 1
            result.append(item)
        
        return result
        
        

class TuflowTypes(object):
    """Contains key words from Tuflow files for lookup.
    
    This acts as a lookup table for the TuflowLoader class more than anything
    else. It is kept here as that seems to be most sensible.
    
    Contains methods for identifying whether a command given to it is known
    to the library and what type it is. i.e. what category it falls into.
    """
    
    def __init__(self):
        """Initialise the categories and known keywords"""

#         self.MODEL, self.RESULT, self.GIS, self.DATA, self.VARIABLE, \
#         self.UNKNOWN_FILE, self.UNKNOWN, self.COMMENT = range(8)
        
        
        self.types = {}
        self.types[ft.MODEL] = ['GEOMETRY CONTROL FILE', 'BC CONTROL FILE',
                                  'READ_FILE',
                                  'ESTRY CONTROL FILE', 'READ RESTART FILE']
        self.types[ft.RESULT] = ['OUTPUT FOLDER', 'WRITE CHECK FILES',
                                   'LOG FOLDER']
        self.types[ft.GIS] = ['READ MI', 'READ GIS', 'READ GRID',
                                'SHP PROJECTION', 'MI PROJECTION']
        self.types[ft.DATA] =  ['READ MATERIALS FILE', 
                                  'BC DATABASE']
        self.types[ft.VARIABLE] =  ['START TIME', 'END TIME', 'TIMESTEP',
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
        order.append([self.root_hex, self.model_refs[self.root_hex].extension, None, None])
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
        
            order.append([child, self.model_refs[child].extension, 
                          self.model_refs[child].parent_hash,
                          self.model_refs[model_ref].extension])
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
        
        
