"""

 Summary:
     Contains all of the TuflowPart type classes used to store the data within
     Tuflow control files.

 Author:
     Duncan Runnacles

 Created:
     20 Nov 2016

 Copyright:
     Duncan Runnacles 2016

 TODO:

 Updates:

"""
from __future__ import unicode_literals

import copy
import uuid
import os

from ship.utils.filetools import PathHolder
from ship.tuflow import FILEPART_TYPES as fpt
from ship.utils import utilfunctions as uf
# from ship.tuflow.tuflowmodel import EventSourceData

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class AssociatedParts(object):
    """Stores associate TuflowPart references.

    Every TuflowPart will hold a copy of this class. It is used to store
    references to any other TuflowPart's that it has an association with.
    """

    def __init__(self, parent, **kwargs):
        self._parent = None
        self.parent = parent
        self.sibling_prev = None
        self.sibling_next = None
        self._logic = None

        self.notify_active_changed = kwargs.get('notify_active', None)

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        if self._parent is not None:
            self._parent.observers.remove(self)

        self._parent = value
        if value is not None:
            self._parent.observers.append(self)

    @property
    def logic(self):
        return self._logic

    @logic.setter
    def logic(self, value):
        if self._logic is not None:
            self._logic.observers.remove(self)

        self._logic = value
        if value is not None:
            self._logic.observers.append(self)

    def observedActiveChange(self, status):
        """called by the parent when registered as an observer."""
        self.notify_active_changed(status)


class TuflowPart(object):
    """Interface for all TuflowPart's.

    All components containing data stored by ControlFile subclass this one.
    """

    def __init__(self, parent, obj_type, **kwargs):
        self.TOP_CLASS = 'part'
        self.hash = uuid.uuid4()
        self.obj_type = obj_type
        self._active = kwargs.get('active', True)
        self.filepart_type = kwargs.get('filepart_type', None)

        self.associates = AssociatedParts(parent, notify_active=self._parentActiveChanged)
        if 'logic' in kwargs.keys() and kwargs['logic'] is not None:
            self.associates.logic = kwargs['logic']

        self.observers = []
        """This is a poor man's observer interface.

        If an object wants to be notified of key internal changes, such as the
        Logic being activated/deactivated, then can add themselves to this
        list.

        If an object is added to this list it should implement the following
        methods:

            - observedActiveChange(bool)
        """

    def _parentActiveChanged(self, status):
        """Called when self.associated observedActiveChanged is called."""
        self.active = status

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        if not value == False:
            value = True
        self._active = value
        for o in self.observers:
            o.observedActiveChange(value)


    def allParents(self, parent_list):
        """Get all the hash codes of all parents to this object.

        Recursive method to search up through all of the parents - in the
        associates object - and retrieve their hash codes.

        The parent hash codes will be returned in ascending order. I.e. the
        immediate parent will be at index 0, then it's parent, and so on.

        Note:
            parent_list arg is used to pass the found parents through the
            recursion. When calling this method you should probably always
            provide an empty list.

        Return:
            list -  containing the hash codes for every parent of the called
            TuflowPart in assending order.
        """
        if self.associates.parent is not None:
            parent_list.append(self.associates.parent.hash)
            parent_list = self.associates.parent.allParents(parent_list)

        return parent_list

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

        is_in = logic.isInTerms(p, se_vals)
        return is_in


    @staticmethod
    def resolvePlaceholder(value, user_vars):
        """Replaces the contents of a placeholder value with an actual value.

        Tuflow allows scenario, event and user defined variables to be used
        as placeholders. This method will check for a given value against a
        dict of current variables and update the value if found.

        Example::

            # Original tcf command
            Cell Size == <<myvar>>
            Read Materials File == '..\Materials_<<s1>>.tmf
            Timestep == <<unknownvar>>

            # user_vars  note that this includes all variable in UserVars in
            # a single dict
            user_vars = {
                's1': 'scen1', 's2': 'scen2', 'e1': 'event1', 'e2': 'event2',
                'myvar': '12'
            }

            # The above commands would return the following values when the
            # above user_vars are given.
            Cell Size == 12
            Read Materials File == '..\Materials_scen1.tmf
            Timestep == <<unknownvar>>

        Args:
            value: the value to check for a placeholder and replace.
            user_vars(dict): see UserVariables.variablesTodict().

        Return:
            the value, updated if found or the same if not.
        """
        for vkey in user_vars.keys():
            temp = '<<' + vkey + '>>'
            if vkey in value:
                value = value.replace(temp, user_vars[vkey])
        return value


    def getPrintableContents(self, **kwargs):
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
        self.TOP_CLASS = 'unknown'
        TuflowPart.__init__(self, parent, 'unknown', **kwargs)
        self.data = kwargs['data'] # raises keyerror


    def getPrintableContents(self, **kwargs):
        return self.data, False


class ATuflowVariable(TuflowPart):
    def __init__(self, parent, obj_type='variable', **kwargs):
        TuflowPart.__init__(self, parent, obj_type, **kwargs)
        self.TOP_CLASS = 'avariable'
        self.command = kwargs['command'] # raise valuerror
        self._variable = kwargs['variable'].strip()
        self.comment = kwargs.get('comment', '')

    @property
    def variable(self):
        return self._variable

    @variable.setter
    def variable(self, value):
        self._variable = value

    def resolvedVariable(self, user_vars):
        """Return the variable with any placeholder vars resolved to a value.

        For more information on user_vars see TuflowPart.resolvePlaceholder.
        """
        return TuflowPart.resolvePlaceholder(self.variable, user_vars)


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

    def getPrintableContents(self, **kwargs):
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

    def getPrintableContents(self, **kwargs):
        return self.buildPrintline(self.command, uf.encodeStr(self._variable), self.comment), False


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

    def getPrintableContents(self, **kwargs):
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

    def getPrintableContents(self, **kwargs):
        instruction = ' | '.join([self.key, self.value])
        return self.buildPrintline(self.command, instruction, self.comment), False


class TuflowFile(TuflowPart, PathHolder):
    """
    """

    def __init__(self, parent, obj_type='file', **kwargs):
        """Constructor.

        **kwargs:
            - 'path': 'relative\path\to\file.ext'
            - 'command': 'command string'
            - 'comment': 'comment at the end of the command'

        Args:
            hash(str): unique code for this object.
            parent(str): unique hash code for this object.

        Raises:
            keyError: if kwargs 'root', 'command', 'path' are not given.
        """
        root = kwargs['root'] # raises keyerror
        self.command = kwargs['command']
        path = kwargs['path']
        self.comment = kwargs.get('comment', '')
        TuflowPart.__init__(self, parent, obj_type, **kwargs)
        PathHolder.__init__(self, path, root)
        self.TOP_CLASS = 'file'
        self.all_types = None
        self.has_own_root = False


    def absolutePathAllTypes(self, user_vars=None):
        """Get the absolute paths for all_types.

        If the file has other file types in all_types (e.g. .shp, shx, .dbf)
        this will return the absolute paths for all of them.

        Args:
            user_vars(dict): a dict containing variable placeholder values as
                keys and the actual values as values. See
                TuflowPart.resolvePlaceholder() method for more information.
        """
        rel_roots = self.getRelativeRoots([])
        paths = []
        if self.all_types:
            all_types = self.all_types
        else:
            all_types = [self.extension]
        for a in all_types:
            f = self.filename + '.' + a
            if self.has_own_root:
                fpath = PathHolder.absolutePath(self, filename=f)
            else:
                fpath = PathHolder.absolutePath(self, filename=f,
                                                relative_roots=rel_roots)

            # Replace any variable placeholders if given
            if user_vars:
                fpath = TuflowPart.resolvePlaceholder(fpath, user_vars)

            paths.append(fpath)
        return paths

    def absolutePath(self, user_vars=None):
        """Get the absolute path of this object.

        Args:
            user_vars(dict): a dict containing variable placeholder values as
                keys and the actual values as values. See
                TuflowPart.resolvePlaceholder() method for more information.
        """
        if self.has_own_root:
            abs_path = PathHolder.absolutePath(self)
        else:
            rel_roots = self.getRelativeRoots([])
            abs_path = PathHolder.absolutePath(self, relative_roots=rel_roots)

        # Replace any variable placeholders if given
        if user_vars:
            abs_path = TuflowPart.resolvePlaceholder(abs_path, user_vars)

        return abs_path


    def filenameAndExtension(self, user_vars=None):
        if user_vars:
            name = self.resolvePlaceholder(self.filename, user_vars)
            if self.extension: name += '.' + self.extension
            return name
        else:
            return PathHolder.filenameAndExtension(self)

    def filenameAllTypes(self, user_vars=None):
        orig_ext = self.extension
        names = []
        names.append(self.filenameAndExtension(user_vars))
        try:
            for a in self.all_types:
                self.extension = a
                names.append(self.filenameAndExtension(user_vars))
        finally:
            self.extension = orig_ext

        return names



    def getRelativeRoots(self, roots):
        """Get the relative paths of this and all parent objects.

        Recursively calls all of it's parents to obtain the relative paths
        before calling absolutePath of the PathHolder superclass.
        """
        if not self.associates.parent is None:
            self.associates.parent.getRelativeRoots(roots)
        if self.relative_root:
            roots.append(self.relative_root)
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


    def getPrintableContents(self, **kwargs):
        if not self.relative_root == None and not self.has_own_root:
            path = self.relativePath()
        elif not self.root == None:
            path = os.path.join(self.root, self.filenameAndExtension())
        else:
            path = self.filenameAndExtension()

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


    def getPrintableContents(self, **kwargs):
        if self.model_type == 'ECF' and self.has_auto:
            line = 'Estry Control File Auto '
            if self.comment: line += '! ' + self.comment
            line = (line, False)
        else:
            line = TuflowFile.getPrintableContents(self, **kwargs)
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

    def filenameAndExtension(self, user_vars=None):
        if self.filename_is_prefix:
            return ''
        else:
            return TuflowFile.filenameAndExtension(self, user_vars)


class GisFile(TuflowFile):

    GIS_TYPES = {'mi': ('mif', 'mid'), 'shp': ('shp', 'shx', 'dbf')}

    def __init__(self, parent, **kwargs):
        TuflowFile.__init__(self, parent, 'gis', **kwargs)

        # Needed to catch GIS files without an extension
        if self.filename == '':
            self.filename = os.path.basename(kwargs['path'])

        # Try and work out what kind of gis file it is when it doesn't have
        # an extension
        # DEBUG
        if self.extension == '':
            if 'test' in kwargs.keys():
                self.extension = kwargs['test']
            else:
                self.extension = 'mif'
                if not os.path.exists(self.absolutePath()):
                    self.extension = 'mid'
                    if not os.path.exists(self.absolutePath()):
                        self.extension = 'shp'
                        if not os.path.exists(self.absolutePath()):
                            self.extension = ''


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
        self.TOP_CLASS = 'logic'
        self.parts = []
        self.group_parts = [[]]
        self.terms = [[]]
        self.commands = []
        self.comments = []
        self._top_written = False

        self.remove_callback = None
        """Function called when a TuflowPart is removed."""

        self.add_callback = None
        """Function called when a TuflowPart is added."""

        self.check_sevals = False
        """Whether to check the scenarion event values."""

        self.END_CLAUSE = 'End'
        """Override with with whatever the end statement is (e.g. 'End If')"""


    def addPart(self, part, group=-1, **kwargs):
        """Add a new TuflowPart.

        **kwargs:
            skip_callback=False(bool): if true it won't call the callback
                function in the ControlFile. Basically don't use this.

        Args:
            part(TuflowPart): the part to add.
            group(int): the clause group to add the part to.
            skip_callback=False(bool): if true it won't call the callback
                function in the ControlFile. Basically don't change this.
        """
        skip_callback = kwargs.get('skip_callback', False)
        part.associates.logic = self
        self.parts.append(part.hash)
        self.group_parts[group].append(part)
        if not skip_callback:
            self.add_callback(part, self.group_parts[group][-1])

    def insertPart(self, new_part, adjacent_part):
        """Insert a TuflowPart adjacent to an existing part.

        This allows you to have control over where in a group a part is placed.
        If you don't care where it goes in the group, or you want it to go at
        the end of the group use addPart() instead.

        Args:
            new_part(TuflowPart): the part to add.
            adjacent_part(TuflowPart): the part to put the new part next to.
                It will be placed above the existing part.
        """
        if not adjacent_part.hash in self.parts:
            raise ValueError('adjacent_part could not be found')
        g = self.getGroup(adjacent_part)
        index = self.group_parts[g].index(adjacent_part)
        new_part.associates.logic = self
        self.parts.append(new_part.hash)
        self.group_parts[g].insert(index, new_part)
        self.add_callback(new_part, adjacent_part)

    def removePart(self, part):
        """Remove a TuflowPart.

        Will also call a callback function to the ControlFile object that
        contains this TuflowLogic and ensure that the PartHolder order is
        updated. It just ensures that the TuflowPart is moved out of the
        scope of the parts still within the TuflowLogic.

        Args:
            part(TuflowPart):
        """
        for p in self.parts:
            if p == part.hash:
                self.parts.remove(part.hash)
                break
        for i, group in enumerate(self.group_parts):
            for j, val in enumerate(group):
                if val == part:
                    del self.group_parts[i][j]
                    break

        if self.group_parts and self.group_parts[-1]:
            last_part = self.group_parts[-1][-1]
        else:
            last_part = None
        part.associates.logic = None
        self.remove_callback(part, last_part)

    def getAllParts(self, hash_only):
        """Return all of the TuflowParts in this TuflowLogic.

        Args:
            hash_only: if True the TuflowPart.hash codes otherwise the actual
                TuflowPart will be.

        Return:
            list - of TuflowPart's or TuflowPart.hash
        """
        if not hash_only:
            parts = []
            for group in self.group_parts:
                for p in group:
                    parts.append(p)
            return parts
        else:
            return self.parts

    def getGroup(self, part):
        """Return the group index of the given part.

        Args:
            part(TuflowPart):

        Return:
            int - the index of the group that this part is in, or -1 if it
                could not be found.
        """
        for i, g in enumerate(self.group_parts):
            if part in g: return i
        else:
            return -1

    def getLogic(self, hash_only):
        """TODO: Check what this does and if it's used."""
        if self.associates.logic is None:
            return None
        else:
            if hash_only:
                return self.associates.logic.hash
            else:
                return self.associates.logic

    def isTuflowPart(self, part):
        """Internal function."""
        if isinstance(part, uuid.UUID):
            return False
        elif isinstance(part, TuflowPart):
            return True
        else:
            raise TypeError('filepart must be either TuflowPart or TuflowPart.hash')

    def isInClause(self, part, term):
        """Test whether the given part is within a particular clause.

        Args:
            part(TuflowPart): check if it's in this TuflowLogic.
            term(str): term to check the part against.

        Return:
            bool - True if the term is part of one of the clauses in this
                TuflowLogic and the part is within that clause; Else False.
        """
        for i, terms in enumerate(self.terms):
            for t in terms:
                if t == term:
                    success = True if part in self.group_parts[i] else False
                    return success
        return False

    def allTerms(self):
        """Returns all of the terms in every clause."""
        out = []
        for terms in self.terms:
            out.extend(terms)
        return out

    def isInTerms(self, part, se_vals):
        """Checks to see if the clause terms associated with part match se_vals.

        If the part is in an 'Else' clause it checks that the se_vals DON'T
        match any of the terms in any of the clauses.

        Args:
            part(TuflowPart): to find the terms for. If now reference of the
                part can be found False will be returned.
            se_Vals(dict): in format {'scenario': [list, of]. 'event': [terms]}.

        Return:
            bool - True if the part is within the given se_vals, otherwise False.
        """
        retval = False
        group = self.getGroup(part)
        if group == -1: return False
        terms = self.terms[group]
        command = self.commands[group]
        se_keys = se_vals.keys()

        '''
        If 'Else' we need to check if it's NOT in any of the terms. So check
        all of the terms and compare against the se_vals. If there's no
        match then we set retval to True.
        '''
        if command.upper() == 'ELSE':
            all_terms = self.allTerms()
            found = True
            if 'scenario' in se_keys:
                found = set(all_terms).isdisjoint(set(se_vals['scenario']))
            elif 'event' in se_keys:
                found = set(all_terms).isdisjoint(set(se_vals['event']))
            if found == True: retval = True

        # Otherwise we need to check if this groups terms are in the se_vals
        else:
            for t in terms:
                if 'scenario' in se_keys and t in se_vals['scenario']:
                    retval = True; break
                elif 'event' in se_keys and t in se_vals['event']:
                    retval = True; break
        return retval

    def getPrintableContents(self, part, out, group=0, **kwargs):
        """Return contents formatted for printing.

        Args:
            part(TuflowPart): current TuflowPart in PartHolder parts list.
            out(list): list to update.
        """
        force = kwargs.get('force', False)
        out = self.getTopClause(part, [], False, **kwargs)
        return out

    def getTopClause(self, part, out, force, **kwargs):
        """Get the top clause command and terms formatted for printing."""
        if not force and not self.group_parts[0]: return out
        if force or self.group_parts[0][0] == part:
            self._top_written = True
            if self.active:
                out.insert(0, self._getContentsLine(0))
            if not self.associates.logic is None:
                out = self.associates.logic.getTopClause(self, out, False)
        return out

    def getEndClause(self, part):
        """Get the end clause formatted for printing."""
        if self.group_parts[-1][-1] == part:
            self._top_written = False
            if self.active:
                return self.END_CLAUSE
            else:
                return ''
        return ''

    def _getContentsLine(self, group=0):
        """Get a clause line formatted for printing.
        """
        if group > len(self.group_parts): raise IndexError('Group %s does not exist' % group)
        if self.terms[group]:# is not None:
            t = ' | '.join(self.terms[group])
            line = self.commands[group] + ' == ' + t
        else:
            line = self.commands[group]
        if self.comments[group]: line += ' ! ' + self.comments[group]
        return line


class IfLogic(TuflowLogic):

    def __init__(self, parent, **kwargs):
        """Constructor.

        **kwargs:
            'command(str)': the command (e.g. If Scenario) for the opening clause.
            'terms'(list): list of terms for the first clause
                (e.g. ['scen1', 'scen2', 'scenN'].
            'comment'(str): any comment next to the first clause.

        Args:
            parent(ModelFile): that contains this TuflowLogic.
        """
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

    def getPrintableContents(self, part, out, **kwargs):
        """Get the printable contents for this TuflowLogic."""
        out = TuflowLogic.getPrintableContents(self, part, out, **kwargs)
        out = self.getMiddleClause(part, out)
        return out

    def getMiddleClause(self, part, out):
        """Check to see if there's any middle clause.

        Used for writing out the clauses when printing to file.
        """
        for i, val in enumerate(self.group_parts):
            if i > 0:
                if val[0] == part:

                    if not self.group_parts[0] and not self._top_written:
                        out = self.getTopClause(None, out, True)
                    if self.active:
                        out.append(self._getContentsLine(i))
        return out

    def addClause(self, command, terms, comment=''):
        """Add a new clause to this TuflowLogic.

        Args:
            command(str): the command part of the clause (e.g. 'Else if Event ==')
            terms(list): str's of terms for clause (e.g. ['evt1', 'evt2', 'evtN'].
            comment=''(str): any comment for the clause line.
        """
        self.commands.append(command.strip())
        if terms is not None:
            self.terms.append([i.strip() for i in terms])
        else:
            self.terms.append([])
        self.comments.append(comment)
        self.group_parts.append([])


class BlockLogic(TuflowLogic):
    """For any logic that uses a 'Define something'.

    I can only think of 'Define Event == term1 | term2 | termN', but maybe
    there are others?
    """

    def __init__(self, parent, **kwargs):
        """Constructor.

        **kwargs:
            'command(str)': the command (e.g. If Scenario) for the opening clause.
            'terms'(list): list of terms for the first clause
                (e.g. ['scen1', 'scen2', 'scenN'].
            'comment'(str): any comment next to the first clause.

        Args:
            parent(ModelFile): that contains this TuflowLogic.
        """
        TuflowLogic.__init__(self, parent, 'blocklogic', **kwargs)
        self.commands = [kwargs['command'].strip()]
        if kwargs['terms'] is not None:
            self.terms = [[i.strip() for i in kwargs['terms']]]
        else:
            self.terms = [[]]
        self.comments = [kwargs.get('comment', '').strip()]
        self.check_sevals = True
        self.END_CLAUSE = 'End Define'

    def addClause(self):
        """Only one clause allowed in this type."""
        raise NotImplementedError('Not supported for this TuflowLogic type')


class SectionLogic(BlockLogic):
    """Used for all other types of scoping logic.

    This includes things like 'Define Output Zone ==' etc. The only real
    difference between this and BlockLogic is that BlockLogic sets
    check_sevals = True. It kind of makes sense to treat them slightly
    differently though as the BlockLogic and IfLogic are used with scenario
    and event logic.
    """

    def __init__(self, parent, **kwargs):
        """Constructor.

        **kwargs:
            'command(str)': the command (e.g. If Scenario) for the opening clause.
            'terms'(list): list of terms for the first clause
                (e.g. ['scen1', 'scen2', 'scenN'].
            'comment'(str): any comment next to the first clause.

        Args:
            parent(ModelFile): that contains this TuflowLogic.
        """
        TuflowLogic.__init__(self, parent, 'sectionlogic', **kwargs)
        self.commands = [kwargs['command'].strip()]
        if kwargs['terms'] is not None:
            self.terms = [[i.strip() for i in kwargs['terms']]]
        else:
            self.terms = [[]]
        self.comments = [kwargs.get('comment', '').strip()]
        self.check_sevals = False
        self.END_CLAUSE = 'End Define'



