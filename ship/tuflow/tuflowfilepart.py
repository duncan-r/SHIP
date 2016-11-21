"""

 Summary:
     

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

import copy
import uuid

from ship.utils.filetools import PathHolder
from ship.tuflow import FILEPART_TYPES as fpt
# from ship.tuflow.tuflowmodel import EventSourceData

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class AssociatedParts(object):
    """
    """
    
    def __init__(self, parent):
        self.parent = parent
        self.sibling_prev = None
        self.sibling_next = None
        self.logic = None
    

class TuflowPart(object):
    """
    """
    
    def __init__(self, parent, obj_type, **kwargs):
        self.hash = uuid.uuid4()
        self.obj_type = obj_type
        self.associates = AssociatedParts(parent)
        self.active = kwargs.get('active', True)
        self.tpart_type = kwargs.get('tpart_type', None)
        if 'logic' in kwargs.keys() and kwargs['logic'] is not None: 
            self.associates.logic = kwargs['logic']
    
    def allParents(self, parent_list):
        """
        """
        if self.associates.parent is not None:
            parent_list.append(self.associates.parent.hash)
            parent_list = self.associates.parent.allParents(parent_list)
        
        return parent_list
#         if self.associates.parent is not None:
#             parent_list.append(self.associates.parent.hash)
#             parent_list.extend(self.associates.parent.allParents(parent_list))
#         else:
#             return parent_list
        
    def isInSeVals(self, se_vals):
        """Check that this TuflowPart or it's parents are inside given logic terms.
        
        The parents must be checked when a part doesn't have a reference to any
        logic because the part may exists inside a control file that does have
        a logic clause. In this situation the part would not have any logic
        directly assigned to it, but would be within the logical clause by
        virtue of it's parent being inside it...
                
        Example::
        :
            a_tcf_file.tcf...
            
            If Scenario == somescenario
                tgc1.tgc
            Else
                tgc2.tgc
            End If

            
            tgc1.tgc...
            
            ! This file's logic == None, but if scenario == 'somescenario' it
            ! should not be returned.
            Read GIS Z Line == afile.shp 
        
        Args:
            part(TuflowPart): the part to check logic terms for.
            user_vars(UserVariables): containing the current scenario and
                event values.
        
        Return:
            bool - True if it's in the logic terms, or False otherwise.
        """
        logic = None
        p = self
        # If the part doesn't have any logic check the parents.
        while True: 
            if p.associates.logic is not None:
                logic = p.associates.logic
                break
            if p.associates.parent is None: 
                break
            p = p.associates.parent
        if logic is None:
            return True
        
        output = logic.isInTerms(p, se_vals)
        return output
    

    def getPrintableContents(self):
        """
        """
        raise NotImplementedError
    
    def buildPrintline(self, command, instruction, comment=''):
        output = [command, '==', instruction]
        if comment:
            output += ['!', comment]
        return ' '.join(output)
    
    def __eq__(self, other):
        return isinstance(other, TuflowPart) and other.hash == self.hash
    
    
    @classmethod
    def copy(self, **kwargs):
        new_version = copy.deepcopy(self)
        
        new_version.hash = uuid.uuid4()
        strip_unique = kwargs('strip_unique', True)
        keep_logic = kwargs('keep_logic', False)
        if strip_unique:
            new_version.sibling_next = None
            new_version.sibling_prev = None
            new_version.comment = ''
            if not keep_logic:
                new_version.logic = None

        return new_version
    
    
class UnknownPart(TuflowPart):
    
    def __init__(self, parent, **kwargs):
        TuflowPart.__init__(self, parent, 'unknown', **kwargs)
        self.data = kwargs['data'] # raises keyerror
    
    
    def getPrintableContents(self):
        return self.data, False
    

class ATuflowVariable(TuflowPart):
    def __init__(self, parent, obj_type='variable', **kwargs):
        TuflowPart.__init__(self, parent, obj_type, **kwargs)
        self.command = kwargs['command'] # raise valuerror
        self._variable = kwargs['variable'].strip()
        self.comment = kwargs.get('comment', '')
    
    @property
    def variable(self):
        return self._variable
    
    @variable.setter
    def variable(self, value):
        self._variable = value


class TuflowVariable(ATuflowVariable):
    """
    """
    
    def __init__(self, parent, **kwargs):
        """
        kwargs(dict): the component of this parts command line::  
            - 'variable': 'one or more variable'  
            - 'command': 'command string'  
            - 'comment': 'comment at end of command'
        """
        ATuflowVariable.__init__(self, parent, 'variable', **kwargs)
        self.split_char = kwargs.get('split_char', ' ')
        self.split_char = self.split_char.replace('\s', ' ')
        self._createSplitVariable(self.variable)
        
    @property
    def variable(self):
        return self._variable
    
    @variable.setter
    def variable(self, value):
        self._variable = value   
        self._createSplitVariable(value)

    @property
    def split_variable(self):
        return self._split_variable
    
    @split_variable.setter
    def split_variable(self, value):
        if len(value) > 1:
            s = self.split_char if self.split_char == ' ' else ' ' + self.split_char + ' '
            s = s.join(value)
        else:
            s = value[0]
        self._variable = s   
        self._split_variable = value
    
    def _createSplitVariable(self, variable):
        s = ' '.join(self._variable.split())
        s = s.split(self.split_char)
        self._split_variable = [i.strip() for i in s]

    def getPrintableContents(self):
        return self.buildPrintline(self.command, self._variable, self.comment), False


class TuflowUserVariable(ATuflowVariable):

    def __init__(self, parent, **kwargs):
        ATuflowVariable.__init__(self, parent, 'uservariable', **kwargs)
        self._variable_name = self.command.split('Set Variable ')[1].strip()
    
    @classmethod
    def noParent(cls, key, variable):
        vars = {'command': '', 'variable': variable}
        uv = cls(None, vars)
        uv._variable_name = key
        return uv
    
    @property
    def variable_name(self):
        return self._variable_name
    
    @variable_name.setter
    def variable_name(self, value):
        self._variable_name = value   
        self.command = 'Set Variable ' + value
    
    def getPrintableContents(self):
        return self.buildPrintline(self.command, unicode(self._variable), self.comment), False


class TuflowModelVariable(ATuflowVariable):

    def __init__(self, parent, **kwargs):
        ATuflowVariable.__init__(self, parent, 'modelvariable', **kwargs)
        self._variable_name = kwargs['name']
        if self._variable_name.upper().startswith('S'):
            self._variable_type = 'scenario'
        else:
            self._variable_type = 'event'

    @classmethod
    def noParent(cls, key, variable):
        vars = {'command': key, 'variable': variable, 'name': key}
        mv = cls(None, **vars)
        return mv
    
    @property
    def variable_name(self):
        return self._variable_name
    
    @variable_name.setter
    def variable_name(self, value):
        self._variable_name = value
    
    def getPrintableContents(self):
        has_next = False; has_prev = False
        if self.associates.sibling_prev is not None: has_prev = True
        if self.associates.sibling_next is not None: has_next = True
        
        line = []
        if not has_prev:
            line.append(self.command + ' == ' + self._variable)
            
        else:
            line.append(' | ' + self._variable)
        
        if not has_next and self.comment:
            line.append('! ' + self.comment)
            
        return ' '.join(line), has_prev


class TuflowKeyValue(ATuflowVariable):
    """
    """
    def __init__(self, parent, **kwargs):
        ATuflowVariable.__init__(self, parent, 'keyvalue', **kwargs)
        keyval = self._variable.split('|')
        self.key = keyval[0].strip()
        self.value = keyval[1].strip()
    
    def getPrintableContents(self):
        instruction = ' | '.join([self.key, self.value])
        return self.buildPrintline(self.command, instruction, self.comment), False

    
class TuflowFile(TuflowPart, PathHolder):
    """
    """
    
    def __init__(self, parent, obj_type='file', **kwargs):
        """
        hash(str): unique code for this object.
        parent(str): unique hash code for this object.
        kwargs(dict): the components of this parts command line:: 
            - 'path': 'relative\path\to\file.ext'   
            - 'command': 'command string'  
            - 'comment': 'comment at the end of the command'
        """
        root = kwargs['root'] # raises keyerror
        self.command = kwargs['command'] 
        path = kwargs['path']
        self.comment = kwargs.get('comment', '') 

        self.all_types = None
        self.has_own_root = False
#         self.actual_name = None
        
        TuflowPart.__init__(self, parent, obj_type, **kwargs)
        PathHolder.__init__(self, path, root)
    
    
    def getAbsolutePath(self):
        """Get the absolute path of this object.
        """
        rel_roots = self.getRelativeRoots([])
        abs_path = PathHolder.getAbsolutePath(self, relative_roots=rel_roots)
        return abs_path
    
    
    def getRelativeRoots(self, roots):
        """Get the relative paths of this and all parent objects.
        
        Recursively calls all of it's parents to obtain the relative paths
        before calling getAbsolutePath of the PathHolder superclass.
        """
        if not self.associates.parent is None:
            roots.extend(self.associates.parent.getRelativeRoots(roots))
        if self.relative_root: 
            roots.extend([self.relative_root])
        return roots
    
    def checkPipedStatus(self, path):
        has_next = False; has_prev = False
        if self.associates.sibling_prev is not None: has_prev = True
        if self.associates.sibling_next is not None: has_next = True

        if has_next or has_prev:
            line = []
            if not has_prev:
                line.append(self.command + ' == ' + path)
                
            else:
                line.append(' | ' + path)
            
            if not has_next and self.comment:
                line.append('! ' + self.comment)
                
            return ' '.join(line), has_prev
        else:
            return [], False


    def getPrintableContents(self):
        if not self.relative_root == None and not self.has_own_root:
            path = self.getRelativePath()
        elif not self.root == None:
            path = os.path.join(self.root, self.getFileNameAndExtension())
        else:
            path = self.getFilenameAndExtension()

        out, has_prev = self.checkPipedStatus(path)
        if out:
            return out, has_prev
        else: 
            return self.buildPrintline(self.command, path, self.comment), False


class ModelFile(TuflowFile):
    
    
    def __init__(self, parent, **kwargs):
        TuflowFile.__init__(self, parent, 'model', **kwargs)
        self.model_type = kwargs['model_type']
        self.has_auto = kwargs.get('has_auto', False)
    
    
    def getPrintableContents(self):
        if self.model_type == 'ECF' and self.has_auto:
            line = 'Estry Control File Auto '
            if self.comment: line += '! ' + self.comment
            line = (line, False)
        else:
            line = TuflowFile.getPrintableContents(self)
        return line


class ResultFile(TuflowFile): 

    RESULT_TYPE = {'output': 'OUTPUT FOLDER', 'check': 'WRITE CHECK FILE',
                   'log': 'LOG'}

    def __init__(self, parent, **kwargs):
        TuflowFile.__init__(self, parent, 'result', **kwargs)
        self.filename_is_prefix = False
        self.result_type = 'UNKNOWN'
        for key, val in ResultFile.RESULT_TYPE.items():
            if self.command.upper().startswith(val):
                self.result_type = key


class GisFile(TuflowFile):
    
    GIS_TYPES = {'mi': ('mif', 'mid'), 'shape': ('shp', 'shx', 'dbf')}
    
    def __init__(self, parent, **kwargs):
        TuflowFile.__init__(self, parent, 'gis', **kwargs)
        
        # Needed to catch GIS files without an extension
        if self.file_name == '': 
            self.file_name = os.path.basename(path)
            
        self.gis_type = None
        for key in GisFile.GIS_TYPES:
            if self.extension in GisFile.GIS_TYPES[key]:
                self.all_types = GisFile.GIS_TYPES[key]
                self.gis_type = key
        
        
        
class DataFile(TuflowFile):
    
    DATA_TYPES = {'TMF': ('tmf',), 'CSV': ('csv',)}
    
    def __init__(self, parent, **kwargs):
        TuflowFile.__init__(self, parent, 'data', **kwargs) 
        
        
        for d in DataFile.DATA_TYPES:
            if self.extension in DataFile.DATA_TYPES[d]:
                self.all_types = DataFile.DATA_TYPES[d]
                self.data_type = d
            
    

class TuflowLogic(TuflowPart): 
    
    def __init__(self, parent, obj_type='logic', **kwargs):
        TuflowPart.__init__(self, parent, obj_type, **kwargs)
        self.parts = []
        self.group_parts = [[]]
        self.terms = [[]]
        self.commands = []
        self.comments = []
        self.remove_callback = None
        self.check_sevals = False
        self._top_written = False
        
        self.END_CLAUSE = 'End'
        """Override with with whatever the end statement is (e.g. 'End If')"""
    
    def addPart(self, part, group=-1):
        self.parts.append(part)
        self.group_parts[group].append(part.hash)
    
    def insertPart(self, new_part, adjacent_part):
        if not adjacent_part in self.parts:
            raise ValueError('adjacent_part could not be found')
        g = self.getGroup(adjacent_part.hash)
        index = self.group_parts[g].index(adjacent_part.hash)
        self.parts.append(new_part)
        self.group_parts[g].insert(index, new_part.hash)
    
    def removePart(self, part):
        hash = part.hash if self.isTuflowPart(part) else part

        for p in self.parts:
            if p.hash == hash:
                self.parts.remove(p)
                break
        for i, group in enumerate(self.group_parts):
            for j, val in enumerate(group):
                if val == hash:
                    del self.group_parts[i][j]
                    break
 
        last_hash = self.group_parts[-1][-1]
        self.remove_callback(hash, last_hash)        
        
    def getAllParts(self, hash_only):
        """"""
        if not hash_only:
            return self.parts
        else:
            return [p.hash for p in self.parts]
    
    def getGroup(self, part_hash):
        for i, g in enumerate(self.group_parts):
            if part_hash in g: return i
        else:
            return -1
    
    def getLogic(self, hash_only):
        if self.associates.logic is None:
            return None
        else:
            if hash_only:
                return self.associates.logic.hash
            else:
                return self.associates.logic
    
    def isTuflowPart(self, part):
        if isinstance(part, uuid.UUID):
            return False
        elif isinstance(filepart, TuflowPart):
            return True
        else:
            raise TypeError('filepart must be either TuflowPart or TuflowPart.hash')
        
    def isInClause(self, filepart, term):
        hash = part.hash if self.isTuflowPart(filepart) else filepart
        for i, term in enumerate(self.terms):
            for t in term:
                if t == term:
                    success = True if hash in self.group_parts[i] else False
                    return success
        return False
    
    def isInTerms(self, part, se_vals): 
        """Checks to see if the clause terms associated with part match se_vals.
        
        Args:
            part(TuflowPart): to find the terms for. If now reference of the
                part can be found False will be returned.
            se_Vals(dict): in format {'scenario': [list, of]. 'event': [terms]}.
        
        Return:
            bool - True if the part is within the given se_vals, otherwise False.
        """
        retval = False
        group = self.getGroup(part.hash)
        if group == -1: return False
        terms = self.terms[self.getGroup(part.hash)]
        for t in terms:
            if t in se_vals['scenario'] or t in se_vals['event']: 
                retval = True
#                 if check_parents and part.associates.parent is not None:
#                     parent = part.associates.parent
#                     if parent.associates.logic is not None:
#                         retval = parent.associates.logic.isInTerms(parent, se_vals, True, retval)
                break
        return retval
    
    def getPrintableContents(self, part, group=0):
        """
        """
        out = self.getTopClause(part, [], False)
        return out
    
    def getTopClause(self, part, out, force):
        """
        """
        if not force and not self.group_parts[0]: return out
        if force or self.group_parts[0][0] == part.hash:
            self._top_written = True
            out.insert(0, self._getContentsLine(0))
            if not self.associates.logic is None:
                out = self.associates.logic.getTopClause(self, out, False)
        return out

    def getEndClause(self, part):
        if self.group_parts[-1][-1] == part.hash:
            self._top_written = False
            return self.END_CLAUSE
        return ''
        
    def _getContentsLine(self, group=0):
        """
        """
        if group > self.group_parts: raise IndexError('Group %s does not exist' % group)
        if self.terms[group]:# is not None:
            t = ' | '.join(self.terms[group])
            line = self.commands[group] + ' == ' + t
        else:
            line = self.commands[group]
        if self.comments[group]: line += ' ! ' + self.comments[group]
        return line


class IfLogic(TuflowLogic): 
    
    def __init__(self, parent, **kwargs):
        TuflowLogic.__init__(self, parent, 'iflogic', **kwargs)
        self.commands = [kwargs['command'].strip()]
        self.all_terms = []
        if kwargs['terms'] is not None:
            self.terms = [[i.strip() for i in kwargs['terms']]]
            self.all_terms.extend(kwargs['terms'])
        else:
            kwargs['terms'] = [None]
        self.comments = [kwargs.get('comment', '').strip()]
        self.check_sevals = True
        self.END_CLAUSE = 'End If'
    
    def getPrintableContents(self, part, out):

        out = TuflowLogic.getPrintableContents(self, part, out) 
        out = self.checkMiddleClause(part, out)
        return out

    def checkMiddleClause(self, part, out):
        for i, val in enumerate(self.group_parts):
            if i > 0:
                if val[0] == part.hash:
                    
                    if not self.group_parts[0] and not self._top_written:
                        out = self.getTopClause(None, out, True)
                    
                    out.append(self._getContentsLine(i))
        return out

    def addClause(self, command, terms, comment=''):
        self.commands.append(command.strip())
        if terms is not None: 
            self.terms.append([i.strip() for i in terms])
        else:
            self.terms.append([])
        self.comments.append(comment)
        self.group_parts.append([])
    
        
# class BlockLogic(TuflowLogic): 
class BlockLogic(TuflowLogic): 
    
    def __init__(self, parent, **kwargs):
        TuflowLogic.__init__(self, parent, 'blocklogic', **kwargs)
        self.commands = [kwargs['command'].strip()]
        if kwargs['terms'] is not None:
            self.terms = [[i.strip() for i in kwargs['terms']]]
        else:
            self.terms = [[]]
        self.comments = [kwargs.get('comment', '').strip()]
        self.check_sevals = True
        self.END_CLAUSE = 'End Define'
    
    
class SectionLogic(BlockLogic): 
    
    def __init__(self, parent, **kwargs):
        TuflowLogic.__init__(self, parent, 'sectionlogic', **kwargs)
        self.commands = [kwargs['command'].strip()]
        if kwargs['terms'] is not None:
            self.terms = [[i.strip() for i in kwargs['terms']]]
        else:
            self.terms = [[]]
        self.comments = [kwargs.get('comment', '').strip()]
        self.check_sevals = False 
        self.END_CLAUSE = 'End Define'
    
    
    
    