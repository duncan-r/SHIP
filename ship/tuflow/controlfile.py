"""

 Summary:
     Container for the main tuflow control files (tcf/tgc/etc).
     
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

from __future__ import unicode_literals

import uuid

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""

from ship.tuflow.tuflowfilepart import TuflowPart, TuflowFile, TuflowLogic, TuflowVariable

    

class ControlFile(object):
    
    def __init__(self, model_type):
        self.model_type = model_type
        self.parts = PartHolder()
        self.logic = LogicHolder()
        self.control_files = []
        
   
    def files(self, filepart_type=None, no_duplicates=True, se_vals=None):
        """Get all the TuflowFile types that match the criteria.
        
        TuflowPart's will be returned in order.
        
        Args:
            filepart_type=None: the FILEPART_TYPES value to check. If None all
                TuflowFile types will be checked.
            no_duplicates=True(bool): If True any duplicate paths will be 
                ignored.
            se_vals(dict): containing scenario and event values to define the
                search criteria.
            
        Return:
            list - of TuflowFile's that matched.
        """
        return self.fetchPartType(TuflowFile, filepart_type, no_duplicates, se_vals)
    
    def variables(self, filepart_type=None, no_duplicates=True, se_vals=None):
        """Get all the ATuflowVariable types that match the criteria.
        
        TuflowPart's will be returned in order.
        
        Args:
            filepart_type=None: the FILEPART_TYPES value to check. If None all
                TuflowFile types will be checked.
            no_duplicates=True(bool): If True any duplicate paths will be 
                ignored.
            se_vals(dict): containing scenario and event values to define the
                search criteria.
            
        Return:
            list - of ATuflowVariable types that matched.
        """
        return self.fetchPartType(TuflowVariable, filepart_type, no_duplicates, se_vals)
    
    def logics(self, filepart_type=None, se_vals=None):
        """
        """
        vars = []
        for logic in self.logic:
            if filepart_type is not None and logic.tpart_type != filepart_type:
                continue
            vars.append(logic)
        
        return vars

    
    def fetchPartType(self, instance_type, filepart_type=None, no_duplicates=True, 
                      se_vals=None):
        """Get all the TuflowPart's that match the criteria.
        
        TuflowPart's will be returned in order.
        
        Args:
            instance_type(TuflowPart): class derived from TuflowPart to restrict
                the search to.
            filepart_type=None: the FILEPART_TYPES value to check. If None all
                TuflowFile types will be checked.
            no_duplicates=True(bool): If True any duplicate paths will be 
                ignored.
            se_vals(dict): containing scenario and event values to define the
                search criteria.
            
        Return:
            list - of filepaths that matched.
        """
        found_commands = []
        vars = []
        for part in self.parts[::-1]:
            if not isinstance(part, instance_type): continue
            if filepart_type is not None and part.tpart_type != filepart_type:
                continue
            if se_vals is not None:
                if not self.checkPartLogic(part, se_vals): continue
            if no_duplicates:
                if part.command in found_commands:
                    continue
            vars.append(part)
            found_commands.append(part.command)
        
        vars.reverse()
        return vars
    
    def filepaths(self, filepart_type=None, absolute=False, no_duplicates=True,
                  no_blanks=True, se_vals=None):
        """Get all the TuflowFile filepaths that match the criteria.
        
        Filepaths will be returned in order.
        
        Args:
            filepart_type=None: the FILEPART_TYPES value to check. If None all
                TuflowFile types will be checked.
            absolute=False(bool): If True absolute paths will be returned. If
                False only filenames will be returned.
            no_duplicates=True(bool): If True any duplicate paths will be 
                ignored.
            no_blanks=True(bool): if True any blank filenames will be ignored.
            se_vals(dict): containing scenario and event values to define the
                search criteria.
            
        Return:
            list - of filepaths that matched.
        """
        paths = []
        for part in self.parts:
            p = None
            if not isinstance(part, TuflowFile): continue
            if filepart_type is not None and part.tpart_type != filepart_type:
                continue
            if se_vals is not None:
                if not self.checkPartLogic(part, se_vals): continue
            if absolute:
                p = part.getAbsolutePath()
            else:
                p = part.getFileNameAndExtension()
            
            if no_duplicates and p in paths: continue
            if p is not None: paths.append(p)

        return paths
    
    def checkPartLogic(self, part, se_vals):
        """Check that the part or it's parents are inside the current logic terms.
        
        See TuflowPart isInSeVals method for further information.
        
        Args:
            part(TuflowPart): the part to check logic terms for.
            se_vals(dict): containing the current scenario and event values.
        
        Return:
            bool - True if it's in the logic terms, or False otherwise.
        """
        output = part.isInSeVals(se_vals)
        return output

    
    def checkPathsExist(self, se_vals=None):
        """Check that all of the TuflowFile type's absolute paths exist.
        
        Args:
            se_vals=None(dict): to select only those TuflowFile's that are 
                within certain scenario and event clauses.
        
        Return:
            list - containing all TuflowFile's that failed the check.
        """
        failed = []
        for part in self.parts:
            if not isinstance(part, TuflowFile): continue
            if not os.path.exists(part.getAbsolutePath()):
                failed.append(part)
        return failed
    
    def updateRoot(self, root, must_exist=True):
        """Update the root variable of all TuflowPart's.
        
        Args:
            root(str): the new directory path.
            must_exist=True(bool): if True and the given root directory doesn't
                exist it will raise a ValueError.
        """
        if must_exist and not os.path.isdir(root):
            raise ValueError('root must be a directory and must exist when must_exist=True')
        for part in self.parts:
            part.root = root
    
    def createIndent(self, indent):
        if indent < 1: 
            return ''
        else:
            return ''.join(['\t' for x in range(indent)])
        
    def getPrintableContents(self):
        """Return the control files with contents formatted for writing to file.
        
        Return:
            dict - control files paths as keys and a ordered list of Tuflow
                commands as the values.
        """
        logic_stack = {}
        logic_group = {}
        cur_ctrl = None
        out = {}
        indent = 0
         
        for p in self.parts:
            if not cur_ctrl == p.associates.parent.hash:
                cur_ctrl = p.associates.parent.hash
            if not cur_ctrl in out.keys():
                out[cur_ctrl] = []; logic_stack[cur_ctrl] = []; logic_group[cur_ctrl] = []
            
            # Get any logic clauses that appear above this part
            if p.associates.logic is not None:
                logic_clause = []
                logic_clause = p.associates.logic.getPrintableContents(p, logic_clause)
                for i, l in enumerate(logic_clause):
                    out[cur_ctrl].append(self.createIndent(indent) + l)
                    if 'IF' in l.upper() or 'ELSE' in l.upper() or 'DEFINE' in l.upper():
                        indent += 1

            # Get the part
            pout, add_to_prev = p.getPrintableContents()
            if add_to_prev:
                out[cur_ctrl][-1] = out[cur_ctrl][-1] + pout
            else:
                out[cur_ctrl].append(self.createIndent(indent) + pout)
            
            # Get any closing statements for logic clauses
            if p.associates.logic is not None:
                logic_clause = p.associates.logic.getEndClause(p)
                if indent > 0: indent -= 1
                if logic_clause: out[cur_ctrl].append(self.createIndent(indent) + logic_clause)
                
        keys = out.keys()
        paths = {}
        for c in self.control_files:
            path = c.getAbsolutePath()
            out[path] = out.pop(c.hash)
        return out
    
    def removeLogicItem(self, remove_hash, last_hash):
        self.parts.movePart(remove_hash, last_hash)
        for i, part in enumerate(self.parts):
            if part.hash == remove_hash: 
                try:
                    next_part = self.parts[i+1]
                except IndexError:
                    next_part = None
                if next_part is None or next_part.associates.logic is None:
                    part.associates.logic = None; 
                else:
                    part.associates.logic = next_part.associates.logic
                    part.associates.logic.insertPart(part, next_part)
                break
            
    def contains(self, **kwargs):
        """Find TuflowPart variables that contain a particular string or value.
        
        All searches are case insensitive.
        
        **kwargs:
            command(str): text to search for in a TuflowPart.command.
            variable(str): characters to search for in a TuflowPart.variable.
            filename(str): text to search for in a TuflowPart.filename.
        
        Return:
            list - of TuflowParts that match the search term.
        """
        command = kwargs.get('command', '').upper()
        variable = kwargs.get('variable', '').upper()
        filename = kwargs.get('filename', '').upper()
        out = []
        for part in self.parts:
            if command:
                try:
                    if command in part.command.upper():
                        out.append(part)
                except AttributeError:
                    continue
            if variable:
                try:
                    if variable in part.variable.upper():
                        out.append(part)
                except AttributeError:
                    continue
            if filename:
                try:
                    if filename in part.filename.upper():
                        out.append(part)
                except AttributeError:
                    continue
        
        return out
    
    def allWithParent(self, parent_hash, iterator):
        """Get all of the TuflowParts with a specific parent in their heirachy.
        
        Calls the allParents() method in TuflowPart. To get all of the parent
        TuflowPart.hash values. allParents() is a recursive method that will
        walk all the way up the tree and return the hash of every parent item.
        
        This method checks to see if a certain hash is in the returned list.
        
        Args:
            parent_hash(uuid4): hash to check against.
            iterator(list or Iterator): containing TuflowPart's to fetch the
                parents from.
                
        Return:
            tuple - list(Tuflowpart's), first index of found paren, last index
                of found parent.
        """
        parts = []
        found = False
        first_index = -1
        last_index = -1
        for i, part in enumerate(iterator):
            allp = part.allParents([])
            if parent_hash in allp:
                parts.append(part)
                if not found:
                    found = True
                    first_index = i
                else:
                    last_index = i
                continue
            
            if not found: 
                continue
            else: 
                break
        
        return parts, first_index, last_index
    
    
    def lastIndexOfControlFile(self, parent_file):
        """Get the last index of TuflowParts with particular parent.
        
        Args:
            parent_file(ModelFile): to check for last occurence of in self.parts.
        
        Return:
            dict - with last index of 'parts', 'logic' and 'control_files'
        """
        _, _, part_index = self.allWithParent(model_file.hash, self.parts)
        _, _, logic_index = self.allWithParent(model_file.hash, self.logic)
        _, _, control_index = self.allWithParent(model_file.hash, self.control_files)
        return {'parts': part_index, 'logic': logic_index, 'control_files': control_index}
    
    
    def removeControlFile(self, model_file):
        """Remove the contents of an existing ControlFile.
        
        Will return a dict with the starting indices of removed sections::
        
            indices = {
                'parts': int, 'logic': int, 'control_files': int
            }
        
        Args:
            model_file(ModelFile): the ModelFile that will be used to find the
                sections of this ControlFile to delete.
        
        Returns:
            dict - containging the starting indices of 'parts', 'logic', 
                and 'control_files' that were deleted.
        """
        # First find all of the old controlfile parts to remove
        to_delete, part_index, _ = self.allWithParent(model_file.hash, self.parts)

        # Then remove them
        to_delete.reverse()
        for part in to_delete:
            self.parts.remove(part)

        # Next the logic
        to_delete, logic_index, _ = self.allWithParent(model_file.hash, self.logic)
            
        # Then remove them
        to_delete.reverse()
        for logic in to_delete:
            self.logic.parts.remove(logic)

        # Finally the control_files
        to_delete, control_index, _ = self.allWithParent(model_file.hash, self.control_files)
        to_delete.append(model_file)
        to_delete.reverse()
        for c in to_delete:
            self.control_files.remove(c)
        
        return {'parts': part_index, 'logic': logic_index, 'control_files': control_index}

    
    def addControlFile(self, model_file, control_file, start_indices):
        """Add the contents of a new ControlFile to this ControlFile.
        
        Args:
            model_file(ModelFile): the ModelFile that is being added.
            control_file(ControlFile): the Control to combine with this one.
            start_index(dict): the locations to perform the replacements at.
                this should contain indices for 'parts', 'logic', and 'control_files'.
        """
        if model_file in self.control_files:
            raise AttributeError('model_file already exists in this ControlFile') 
        self.parts.parts[start_indices['parts'] : start_indices['parts']] = control_file.parts
        self.logic.parts[start_indices['logic'] : start_indices['logic']] = control_file.logic
        self.control_files[start_indices['control_files'] : start_indices['control_files']] = control_file.control_files

    
    def replaceControlFile(self, model_file, control_file, replace_modelfile):
        """Replace contents of an existing ModelFile with a new one.
        
        Args:
            model_file(ModelFile): the ModelFile that will be replacing an 
                existing ModelFile.
            control_file(ControlFile): containing the contents to update this
                ControlFile with.
            replace_modelfile(ModelFile): the ModelFile in this ControlFile to
                replace with the new ControlFile.
        """
        if model_file in self.control_files:
            raise AttributeError('model_file already exists in this ControlFile') 
        start_index = self.removeControlFile(replace_modelfile)
        self.addControlFile(control_file, start_index)

    
        
        
class PartHolder(object):
    
    def __init__(self):
        self.parts = []
        self._min = 0
        self._max = len(self.parts)
        self._current = 0
    
    
    def __iter__(self):
        """Return an iterator for the units list"""
        return iter(self.parts)
    
    
    def __delitem__(self, key):
        del self.parts[key]
        self._max -= 1
    
    
    def __next__(self):
        """Iterate to the next unit"""
        if self._current > self._max or self._current < self._min:
            raise StopIteration
        else:
            self._current += 1
            return self.parts[self._current]
    
    
    def __getitem__(self, key):
        """Gets a value from units using index notation.
        
        Returns:
            contents of the units element at index.
        """
        return self.parts[key]
    

    def __setitem__(self, key, value):
        """Sets a value using index notation
        
        Calls the setValue() function to do the hard work.
        
        Args:
            key (int): index to update.
            value: the value to add to the units.
        
        Raises:
        """
        if not isinstance(value, TuflowPart):
            raise ValueError('Item must be of type TuflowPart')
        self.parts[key] = value
    
    
#     def addPart(self, filepart, **kwargs):#after=None, before=None):
    def add(self, filepart, **kwargs):#after=None, before=None):
        """
        
        If both after and before are supplied, after will take precedence.
        """
        after = kwargs.get('after', None)
        before = kwargs.get('before', None)
        take_logic = kwargs.get('take_logic', True)

        if filepart in self.parts:
            raise (ValueError, 'filepart %s already exists.' % filepart.hash)

        if not after is None:
            index = self.findPartIndex(after)
            if index == len(self.part_order):
                self.parts.append(filepart)
            else:
                self.parts.insert(index+1, filepart)
        elif not before is None:
            index = self.findPartIndex(before.hash)
            self.parts.insert(index, filepart)
        else:
            self.parts.append(filepart)
    
    
    def replace(self, part, replace_part):
        """
        """
        index = self.parts.index(replace_part)
        if index == -1:
            raise IndexError('part does not exist in collection')
        
        self.parts.pop(index)
        self.parts.insert(index, part)
            

#     def movePart(self, part, after):
    def move(self, part, **kwargs): #after):
        after = kwargs('after', None)
        before = kwargs('before', None)
        if after is None and before is None:
            raise AttributeError('Either before or after part must be given')
        take_logic = kwargs('take_logic', True)

        pindex = self.findPartIndex(part)
        aindex = self.findPartIndex(after)
        self.parts.insert(aindex, self.parts.pop(pindex))
        
        
    def findPartIndex(self, part):
        if isinstance(part, TuflowPart):
            hash = part.hash
        elif isinstance(part, uuid.UUID):
            hash = part
        else:
            raise ValueError ('Reference part is not of type TuflowPart or a hashcode.')
        
        try:
            return self.parts.index(part)
        except ValueError:
            raise ValueError('Reference part does not exist (%s)' % hash)
    
    
#     def getPart(self, filepart, filepart_type=None):
    def get(self, filepart, filepart_type=None):
        """
        """
        part_hash, type_hash = self._checkPartKeys(filepart_hash, filepart_type)
        return self.parts[filepart.part_type][filepart.hash]
    
    
    def remove(self, filepart):
        """
        """
        index = self.findPartIndex(filepart)
        fpart = self.parts[index]
        del self.parts[index]
        return fpart
        
       
class LogicHolder(object):
    
    def __init__(self):
        self.parts = []
        self._min = 0
        self._max = len(self.parts)
        self._current = 0
    
    def __iter__(self):
        """Return an iterator for the units list"""
        return iter(self.parts)
    
    
    def __next__(self):
        """Iterate to the next unit"""
        if self._current > self._max or self._current < self._min:
            raise StopIteration
        else:
            self._current += 1
            return self.parts[self._current]
    
    
    def __getitem__(self, key):
        """Gets a value from units using index notation.
        
        Returns:
            contents of the units element at index.
        """
        return self.parts[key]
    

    def __setitem__(self, key, value):
        """Sets a value using index notation
        
        Calls the setValue() function to do the hard work.
        
        Args:
            key (int): index to update.
            value: the value to add to the units.
        
        Raises:
        """
        if not isinstance(value, TuflowPart):
            raise ValueError('Item must be of type TuflowPart')
        self.parts[key] = value
    
    
    def getAllParts(self, hash_only):
        output = []
        for p in self.parts:
            if hash_only:
                output.append(p.hash)
            else:
                output.append(p)
        return output
    
    def partFromHash(self, hash):
        for p in self.parts:
            if p.hash == hash: return p
        return None
    
    
    def add(self, logic):
        for l in logic:
            self.parts.append(l)
    
    
    
class TcfControlFile(ControlFile):
    
    def __init__(self, mainfile):
        self.model_type = 'TCF'
        self.parts = PartHolder()
        self.logic = LogicHolder()
        self.control_files = []
        self.mainfile = mainfile
        
        
        
        