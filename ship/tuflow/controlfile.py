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
        
   
    def files(self, filepart_type=None, no_duplicates=True, user_vars=None):
        """
        """
        return self.fetchPartType(TuflowFile, filepart_type, no_duplicates, user_vars)
    
    def variables(self, filepart_type=None, no_duplicates=True, user_vars=None):
        """
        """
        return self.fetchPartType(TuflowVariable, filepart_type, no_duplicates, user_vars)
    
    def logics(self, filepart_type=None, user_vars=None):
        """
        """
        vars = []
        for logic in self.logic:
            if filepart_type is not None and logic.tpart_type != filepart_type:
                continue
            vars.append(logic)
        
        return vars

    
    def fetchPartType(self, instance_type, filepart_type=None, no_duplicates=True, 
                      user_vars=None):
        """
        """
        found_commands = []
        vars = []
        for part in self.parts[::-1]:
            if not isinstance(part, instance_type): continue
            if filepart_type is not None and part.tpart_type != filepart_type:
                continue
            if user_vars is not None:
                if not self.checkPartLogic(part, user_vars): continue
            if no_duplicates:
                if part.command in found_commands:
                    continue
            vars.append(part)
            found_commands.append(part.command)
        
        vars.reverse()
        return vars
    
    def filepaths(self, filepart_type=None, absolute=False, no_duplicates=True,
                  no_blanks=True, user_vars=None):
        """
        """
        paths = []
        for part in self.parts:
            p = None
            if not isinstance(part, TuflowFile): continue
            if filepart_type is not None and part.tpart_type != filepart_type:
                continue
            if user_vars is not None:
                if not self.checkPartLogic(part, user_vars): continue
            if absolute:
                p = part.getAbsolutePath()
            else:
                p = part.getFileNameAndExtension()
            
            if no_duplicates and p in paths: continue
            if p is not None: paths.append(p)

        return paths
    
    def checkPartLogic(self, part, user_vars):
        """Check that the part or it's parents are inside the current logic terms.
        
        See TuflowPart isInSeVals method for further information.
        
        Args:
            part(TuflowPart): the part to check logic terms for.
            user_vars(UserVariables): containing the current scenario and
                event values.
        
        Return:
            bool - True if it's in the logic terms, or False otherwise.
        """
        se = user_vars.scenarioEventValuesToDict()
        output = part.isInSeVals(se)
        return output

    
    def checkPathsExist(self, user_vars=None):
        """
        """
        failed = []
        for part in self.parts:
            if not isinstance(part, TuflowFile): continue
            if not os.path.exists(part.getAbsolutePath()):
                failed.append(part)
        return failed
    
    def updateRoot(self, root, must_exist=True):
        """
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
        
        
class PartHolder(object):
    
    def __init__(self):
        self.part_hashes = []
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
        self.part_hashes[key] = value.hash
    
    
#     def addPart(self, filepart, **kwargs):#after=None, before=None):
    def add(self, filepart, **kwargs):#after=None, before=None):
        """
        
        If both after and before are supplied, after will take precedence.
        """
        after = kwargs('after', None)
        before = kwargs('before', None)
        take_logic = kwargs('take_logic', True)

        if filepart.hash in self.part_hashes:
            raise (ValueError, 'filepart %s already exists.' % filepart.hash)

        if not after is None:
            index = self.findPartIndex(after)
            if index == len(self.part_order):
                self.parts.append(filepart)
                self.part_hashes.append(filepart.hash)
            else:
                self.parts.insert(index+1, filepart)
                self.part_hashes.insert(index+1, filepart.hash)
        elif not before is None:
            index = self.findPartIndex(before.hash)
            self.parts.insert(index, filepart)
            self.part_hashes.insert(index, filepart.hash)
        else:
            self.parts.append(filepart)
            self.part_hashes.append(filepart.hash)
            

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
            return self.part_hashes.index(hash)
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
        del self.part_hashes[index]
        return fpart
        
       
class LogicHolder(object):
    
    def __init__(self):
        self.parts = []
        self.part_hashes = []
        
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
        self.part_hashes[key] = value.hash
    
    
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
    
    
    def addLogic(self, logic):
        for l in logic:
            self.part_hashes.append(l.hash)
            self.parts.append(l)
    
    
    
class TcfControlFile(ControlFile):
    
    def __init__(self, mainfile_hash):
        self.model_type = 'TCF'
        self.parts = PartHolder()
        self.logic = LogicHolder()
        self.control_files = []
        self.mainfile_hash = mainfile_hash
        
        
        
        