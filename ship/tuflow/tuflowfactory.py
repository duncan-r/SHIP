from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""

import os
import copy

from ship.tuflow.tuflowmodel import TuflowFilepartTypes
from ship.tuflow import FILEPART_TYPES as fpt
from ship.tuflow import tuflowfilepart as tuflowpart
from ship.utils import utilfunctions as uf



class TuflowFactory(object):
    
    def __init__(self):
        pass

    @classmethod
    def getTuflowPart(cls, line, parent, part_type=None, logic=None):

        filepart_types = TuflowFilepartTypes()
        line = line.strip()
        upline = line.upper()
        if part_type is None:
            found, key = filepart_types.find(upline)
        else:
            found, key = filepart_types.find(upline, part_type)
            if not found:
                raise TypeError("Provided part type (%s) doesn't match line (%s)" % (part_type, line))

#         vars = {'filepart_type': part_type}
        vars = {}
        if logic is not None:
            vars['logic'] = logic
            
        # Don't know what to do with it
        if not found:
            vars['filepart_type'] = fpt.UNKNOWN
            vars['data'] = line
            return [tuflowpart.UnknownPart(parent, **vars)]

        key = checkMultiTypes(line, key)
        vars['filepart_type'] = key

        if key == fpt.MODEL:
            parts = TuflowFactory.createModelType(line, parent, **vars)
        
        elif key == fpt.GIS:
            parts = TuflowFactory.createGisType(line, parent, **vars)
        
        elif key == fpt.RESULT:
            parts = TuflowFactory.createResultType(line, parent, **vars)
        
        elif key == fpt.DATA:
            parts = TuflowFactory.createDataType(line, parent, **vars)
        
        elif key == fpt.VARIABLE:
            parts = TuflowFactory.createVariableType(line, parent, **vars)
        
        elif key == fpt.MODEL_VARIABLE:
            parts = TuflowFactory.createModelVariableType(line, parent, **vars)
        
        elif key == fpt.EVENT_VARIABLE:
            parts = TuflowFactory.createBcEventVariable(line, parent, **vars)
        
        elif key == fpt.USER_VARIABLE:
            parts = TuflowFactory.createUserVariableType(line, parent, **vars)
        
        return parts


    '''
        #
        TuflowFilepart type builders.
        #
    '''
    @staticmethod
    def createModelVariableType(line, parent, **kwargs):
        command, kwargs['comment'], cchar = separateComment(line)
        kwargs['command'], variable = breakLine(command)
        split_var = variable.split('|')
        
        if 'MODEL SCENARIOS' in kwargs['command'].upper():
            prefix = 's'
        else:
            prefix = 'e'
        
        parts = []
        for i, s in enumerate(split_var):
            s = s.strip()
            name = prefix + uf.encodeStr(str(i+1))
            parts.append(tuflowpart.TuflowModelVariable(parent, **{
                    'logic': kwargs.get('logic', None), 'command': kwargs['command'],
                    'comment': kwargs['comment'], 'variable': s, 'name': name
            }))
        
        parts = assignSiblings(parts)
        return parts

   
    @staticmethod
    def createUserVariableType(line, parent, **kwargs):
        command, kwargs['comment'], cchar = separateComment(line)
        kwargs['command'], kwargs['variable'] = breakLine(command)
        part = tuflowpart.TuflowUserVariable(parent, **kwargs)
        return [part]

    @staticmethod
    def createBcEventVariable(line, parent, **kwargs):
        l = line.strip().upper()
        if l.startswith('BC EVENT NAME'):
            return TuflowFactory.createVariableType(line, parent, **kwargs)
        if l.startswith('BC EVENT TEXT'):
            return TuflowFactory.createVariableType(line, parent, **kwargs)
        if l.startswith('BC EVENT SOURCE'):
            return TuflowFactory.createKeyValueType(line, parent, **kwargs)
        
    @staticmethod
    def createVariableType(line, parent, **kwargs):
        command, kwargs['comment'], cchar = separateComment(line)
        kwargs['command'], kwargs['variable'] = breakLine(command)
        part = tuflowpart.TuflowVariable(parent, **kwargs)
        return [part]

    @staticmethod
    def createKeyValueType(line, parent, **kwargs):
        command, kwargs['comment'], cchar = separateComment(line)
        kwargs['command'], kwargs['variable'] = breakLine(command)
        part = tuflowpart.TuflowKeyValue(parent, **kwargs)
        return [part]

    @staticmethod
    def createDataType(line, parent, **kwargs):
        command, kwargs['comment'], cchar = separateComment(line)
        kwargs['command'], kwargs['path'] = breakLine(command)
        kwargs['root'] = parent.root
        part = tuflowpart.DataFile(parent, **kwargs)
        return [part]

    @staticmethod
    def createResultType(line, parent, **kwargs):
        command, kwargs['comment'], cchar = separateComment(line)
        kwargs['command'], kwargs['path'] = breakLine(command)
        kwargs['root'] = parent.root
        part = tuflowpart.ResultFile(parent, **kwargs)
        part = resolveResult(part)
        return [part]
    
    @staticmethod
    def createGisType(line, parent, **kwargs):
        command, kwargs['comment'], cchar = separateComment(line)
        kwargs['command'], kwargs['path'] = breakLine(command)
        kwargs['root'] = parent.root
        
        if '|' in kwargs['path']:
            return partsFromPipedFiles(tuflowpart.GisFile, parent, **kwargs)
        else:
            part = tuflowpart.GisFile(parent, **kwargs)
            return [part]
    
    @staticmethod
    def createModelType(line, parent, **kwargs):
        command, kwargs['comment'], cchar = separateComment(line)
        
        # Check for Estry auto command
        command, has_auto = checkEstryAuto(command, parent)
        kwargs['has_auto'] = has_auto
        kwargs['command'], kwargs['path'] = breakLine(command)
        kwargs['root'] = parent.root
        if takeParentType(kwargs['path']):
            kwargs['model_type'] = parent.model_type
        else:
            kwargs['model_type'] = getExtension(kwargs['path'])
        part = tuflowpart.ModelFile(parent, **kwargs)
        return [part] 
    
    @staticmethod
    def createIfLogic(parent, commands, terms, comments):
        """Create a new IfLogic object.
        
        Args:
            parent(ModelFile): the parent TuflowPart.
            commands(list): a list of the command part to add for each clause.
                e.g. 'If Scenario', 'Else', 'Else If Event', etc.
            terms:(list(list)): terms to add for each clause. e.g.
                [['scen1', 'scen2'], ['scen3']]
            comments(list): the comment that should be attached to the end of
                each clause line. e.g. 'If Scenario == scen1 | scen2 ! comment'
        
        Return:
            IfLogic - created with given args.
        
        Raises:
            ValueError - if commands, terms and comments are not the same length.
        """
        if not len(commands) == len(terms) == len(comments):
            raise ValueError('commands, terms and comments must be the same length')
        
        iflogic = None
        for i, c in enumerate(commands):
            if i == 0:
                vars = {'command': c, 'terms': terms[i], 'comment': comments[i]}
                iflogic = tuflowpart.IfLogic(parent, **vars)
            else:
                iflogic.addClause(c, terms[i], comments[i])
        
        return iflogic

    @staticmethod
    def createBlockLogic(parent, commands, terms, comments):
        """Create a new IfLogic object.
        
        Args:
            parent(ModelFile): the parent TuflowPart.
            commands(str): the command part e.g. 'Define Event'.
            terms:(list): terms to add for the clause ['scen1', 'scen2'].
            comments(str): the comment that should be attached to the end of
                the clause line. e.g. 'If Scenario == scen1 | scen2 ! comment'
        
        Return:
            BlockLogic - created with given args.
        """
        vars = {'command': commands, 'terms': terms, 'comment': comments}
        blocklogic = tuflowpart.BlockLogic(parent, **vars)
        
        return blocklogic


def partsFromPipedFiles(part_type, parent, **kwargs):
    """Separates piped file paths and creates a TuflowFilepart for each.
    
    The 'path' entry in the kwargs will be replaced with the specific section
    of the piped file that is being created for each part.
    
    Note:  
        This function also call assignSiblings().
    
    Args:
        part_type(TuflowFilePart): class to crate the resultant parts with.
        parent(TuflowFilePart): the control file part containing this command.
        kwargs(dict): the arguments to use when building the TuflowFilePart.
            These are dependent on the type of TuflowFilePart that you create.
    
    Return:
        list - containing TuflowFilePart instance of part_type type.
    """
    split_var = kwargs['path'].split('|')
        
    parts = []
    for i, s in enumerate(split_var):
        vars = copy.deepcopy(kwargs)
        s = s.strip()
        vars['path'] = s
        parts.append(part_type(parent, **vars))
    
    parts = assignSiblings(parts)
    return parts


def assignSiblings(parts):
    """Assign's next and previours sibling's in an ordered list.
    
    Args:
        parts(list): a list of TuflowFilepart's in associate order.
        
    Return:
        parts(list) - with sibling_next and sibling_prev objects set to 
            adjacent parts in the provided list.
    """
    for i, p in enumerate(parts):
        if i == 0:
            if len(parts) > 1:
                parts[i].associates.sibling_next = parts[i+1]
        if i > 0:
            parts[i].associates.sibling_prev = parts[i-1]
        if i < len(parts) - 1:
            parts[i].associates.sibling_next = parts[i+1]
    
    return parts


def checkMultiTypes(line, part_type):
    """Returns the corrent filepart _type for multi-type commands.
    
    For example projection can be either a string variable or a gis file.
    
    Args:
        line(str): the control file line to check.
        part_type(FILEPART_TYPE): the default value to return if everything
            was already correct.
    
    Return:
        FILEPART_TYPE
    """
    l = line.strip().upper()
    if l.startswith('SHP PROJECTION') or l.startswith('MI PROJECTION'):
        splitl = l.split('==')
        val = splitl[1].upper()
        if 'COORDSYS' in val and 'EARTH' in val and 'PROJECTION' in val:
            return fpt.VARIABLE
    
    return part_type


def checkEstryAuto(line, parent):
    l = line.strip().upper()
    has_auto = False
    if l.startswith('ESTRY CONTROL FILE'):
        if 'AUTO' in l:
            has_auto = True
            line = 'Estry Control File == ' + parent.filename + '.ecf'
    return line, has_auto



def checkIsComment(line):
    if line.strip().startswith('!') or line.strip().startswith('#'):
        return True
    else:
        return False


def takeParentType(path):
    types = ['TCF', 'TBC', 'TGC', 'TEF', 'ECF']
    ext = getExtension(path)
    if ext in types: 
        return False
    else:
        return True


def getExtension(path, upper=True):
    ext = os.path.splitext(path)[1][1:].upper()
    if upper == True: 
        return ext.upper()
    else:
        return ext.lower()
         
 
def breakLine(line):
    """Breaks a file line into it's command/instruction components.
     
    Most lines in tuflow files are in the form::
    Read Command == ..\some\path.ext ! comment
     
    This separates the command from the rest.
     
    Args:
        line(str): the line as read from the file.
     
    Returns:
        Tuple - (command, instruction).
    """
    line = line.strip()
    command, instruction = line.split('==', 1)
    command = command.strip()
    instruction = instruction.strip()
    return command, instruction
 
 
def separateComment(instruction):
    """Separates any comment from the line.
     
    Args:
        instructions(str): the line to seperate comment from.
     
    Return:
        tuple(Bool, tuple) - (0)==True if comment found, (1) contains a 
            tuple with (instruction, comment).
    """
    comment_char = None
    if '!' in instruction:
        comment_char = '!'

    if '#' in instruction:
        comment_char = '#'

    if not comment_char is None:
        split = instruction.split(comment_char, 1)
    else:
        split = [instruction]
        comment_char = ''
 
    if len(split) > 1:
        return split[0].strip(), split[1].strip(), comment_char
    else:
        return split[0].strip(), '', comment_char
    

def resolveResult(result_part):
    """Fixes the self.type.RESULT paths after load.
    
    Result and Check file paths are a bit tricky because they can be set
    up in a range of ways as either relative or absolute e.g.:
    ::
        ..\some\path\end  
        ..\some\path\end\  
        ..\some\path\end_as_prefix_  
    
    If output is a checkfile no '\' on the end indicates that the final
    string should be prepended to all files, but if it's a result output
    it is the same as having a '\' on the end.
    
    This function attempts to work out what's going on with it all and setup
    the root, relative_root and filename accordingly.
    
    TODO:
        Need to account for the case where a string follows the directory
        is given that will be prepended to all output files.
    
    Args:
        entry(ResultFile):
    
    Returns:
        ResultFile - ammended.
    """
    rtype = result_part.result_type.upper()
             
    is_absolute = os.path.isabs(result_part.path_as_read)
    basename = os.path.basename(result_part.path_as_read)
    final_char = result_part.path_as_read[-1]
    trailing_slash = final_char == '\\' or final_char == '/'
    
    if is_absolute:
        result_part.has_own_root = True
        result_part.relative_root = ''
        
        # If there's a slash on the end keep path as it is
        if trailing_slash:
            result_part.root = result_part.path_as_read
        
        # Get directory for CHECK files so we can set a filename prefix later
        # or stick a slash on the end for the others to make it easier to
        # deal with it later
        elif not trailing_slash and rtype == 'CHECK':
            result_part.root = os.path.dirname(result_part.path_as_read) + os.sep
        else:
            result_part.root = result_part.path_as_read + os.sep
    else:
        # This shouldn't ever happen, but in case it does we set it to 
        # '' here so it doesn't catch anyone out later
        if result_part.root is None: result_part.root = ''

        result_part.has_own_root = False
        if trailing_slash:
            result_part.relative_root = result_part.path_as_read
        elif not trailing_slash and rtype == 'CHECK':
            result_part.relative_root = os.path.dirname(result_part.path_as_read)
        else:
            result_part.relative_root = result_part.path_as_read + os.sep
            
    result_part.filename = ''
    result_part.extension = ''
#         result_part.filename_is_prefix = False
    
    # A trailing string is a prefix in check files so set that up here
    if rtype == 'CHECK':
        if not trailing_slash:
            if not result_part.has_own_root:
                result_part.relative_root = result_part.relative_root + os.sep
            result_part.filename_is_prefix = True
            result_part.filename = os.path.basename(result_part.path_as_read)
   
    return result_part 
    
    