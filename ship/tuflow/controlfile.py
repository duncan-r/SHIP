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
import os

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""

from ship.tuflow.tuflowfilepart import TuflowPart, TuflowFile, TuflowLogic, \
    TuflowVariable, ModelFile, UnknownPart
from ship.utils import filetools


class ControlFile(object):

    def __init__(self, model_type):
        self.model_type = model_type
        self.parts = PartHolder()
        self.logic = LogicHolder(remove_callback=self.removeLogicPart,
                                 add_callback=self.addLogicPart)
        self.control_files = []

    def files(self, filepart_type=None, no_duplicates=True, se_vals=None,
              **kwargs):
        """Get all the TuflowFile types that match the criteria.

        TuflowPart's will be returned in order.

        All kwargs are passed onto fetchPartType. See there for more details.

        Args:
            filepart_type=None: the FILEPART_TYPES value to check. If None all
                TuflowFile types will be checked. You can also supply a list of
                multiple filepart_type's.
            no_duplicates=True(bool): If True any duplicate commands will be 
                ignored.
            se_vals(dict): containing scenario and event values to define the
                search criteria.

        Return:
            list - of TuflowFile's that matched.
        """
        return self.fetchPartType(TuflowFile, filepart_type, no_duplicates,
                                  se_vals, **kwargs)

    def variables(self, filepart_type=None, no_duplicates=True, se_vals=None,
                  **kwargs):
        """Get all the ATuflowVariable types that match the criteria.

        TuflowPart's will be returned in order.

        All kwargs are passed onto fetchPartType. See there for more details.

        Args:
            filepart_type=None: the FILEPART_TYPES value to check. If None all
                TuflowFile types will be checked. You can also supply a list of
                multiple filepart_type's.
            no_duplicates=True(bool): If True any duplicate commands will be 
                ignored.
            se_vals(dict): containing scenario and event values to define the
                search criteria.

        Return:
            list - of ATuflowVariable types that matched.
        """
        return self.fetchPartType(TuflowVariable, filepart_type, no_duplicates,
                                  se_vals, **kwargs)

    def logics(self, filepart_type=None, se_vals=None, **kwargs):
        """
        """
        ignore_inactive = kwargs.get('ignore_active', True)
        vars = []
        for logic in self.logic:
            if ignore_inactive and not logic.active:
                continue
            if filepart_type is not None and logic.filepart_type != filepart_type:
                continue
            vars.append(logic)

        return vars

    def fetchPartType(self, instance_type, filepart_type=None, no_duplicates=True,
                      se_vals=None, **kwargs):
        """Get all the TuflowPart's that match the criteria.

        TuflowPart's will be returned in order.

        The callback_func kwarg can be used to do any other checks on a file
        part that you need and are not included in the given arguments. It is
        the last check that's run and will therefore only be performed on 
        parts that have already passed all other checks. 

        **kwargs:
            active_only(bool): if True will only return TuflowPart's that have the
                'active' flag set to True.
            'callback_func'(func): if given the function will be called with
                the part after all other logic has run. It must take a list of
                all the parts found so far and the current part (list, TuflowPart).
                It must return a bool, stating whether to add the part to list.
            'by_parent'(bool): if True it will return a dict containing lists of
                the parts under their parent filename and extension as a key.
                Default is False.
            exclude(list): filepart_type's that should not be included
                in the return list.

        Args:
            instance_type(TuflowPart): class derived from TuflowPart to restrict
                the search to.
            filepart_type=None: the FILEPART_TYPES value to check. If None all
                TuflowFile types will be checked. You can also supply a list of
                multiple filepart_type's.
            se_vals(dict): containing scenario and event values to define the
                search criteria.

        Return:
            list - of filepaths that matched.
        """
        active_only = kwargs.get('active_only', True)
        callback = kwargs.get('callback_func', None)
        by_parent = kwargs.get('by_parent', False)
        exclude = kwargs.get('exclude', [])
        if filepart_type is None:
            filepart_type = []
        elif not isinstance(filepart_type, list):
            filepart_type = [filepart_type]

        found_commands = []
        fetch_sibling = False
        vars = []
        parents = {}
        for part in self.parts:
            if active_only and not part.active:
                continue
            if not isinstance(part, instance_type):
                continue
            if filepart_type and not part.filepart_type in filepart_type:
                continue
            if part.filepart_type in exclude:
                continue

            if se_vals is not None:
                if not self.checkPartLogic(part, se_vals):
                    continue

            if no_duplicates:
                if part.command in found_commands and not fetch_sibling:
                    continue
                else:
                    if not part.command in found_commands:
                        found_commands.append(part.command)
                    # If a part has a sibling note that here so that it doesn't
                    # get missed by the found_commands check
                    if part.associates.sibling_next is not None:
                        fetch_sibling = True
                    else:
                        fetch_sibling = False

            if callback:
                take = callback(vars, part)
                if take:
                    if by_parent:
                        if not part.associates.parent.filenameAndExtension() in parents.keys():
                            parents[part.associates.parent.filenameAndExtension()] = []
                        parents[part.associates.parent.filenameAndExtension()].append(part)
                    else:
                        vars.append(part)
            else:
                if by_parent:
                    if not part.associates.parent.filenameAndExtension() in parents.keys():
                        parents[part.associates.parent.filenameAndExtension()] = []
                    parents[part.associates.parent.filenameAndExtension()].append(part)
                else:
                    vars.append(part)

        if by_parent:
            return parents
        else:
            return vars

    def customPartSearch(self, callback_func, include_unknown=False):
        """Return TuflowPart's based on the return value of callback_func.

        Get a generator containing all of the TuflowPart's in PartHolder that
        meet the condition of callback_func.

        callback_func must accept a TuflowPart and return a tuple of: 
        keep-status and the return value. For example::

            # This is the callback_func that we test the TuflowPart. It is
            # defined in your script
            def callback_func(part):

                # In this case we check for GIS parts and return a tuple of:
                # - bool(keep-status): True if it is a GIS filepart_type 
                # - tuple: filename and parent.model_type. This can be 
                #       whatever you want though
                if part.filepart_type == fpt.GIS:
                    return True, (part.filename, part.associates.parent.model_type)

                # Any TuflowPart's that you don't want included must return
                # a tuple of (False, None)
                else:
                    return False, None

            tgc = tuflow.control_files['TGC']
            tgc.customPartSearch(callback_func)

        Args:
            callback_func(func): a function to run for each TuflowPart in 
                this ControlFile's PartHolder.
            include_unknown=False(bool): If False any UnknownPart's will be
                ignored. If set to True it is the resonsibility of the 
                callback_func to check for this and deal with it.

        Return:
            generator - containing the results of the search.
        """
        for p in self.parts:
            if not include_unknown and isinstance(p, UnknownPart):
                continue

            take, value = callback_func(p)
            if take:
                yield[value]

    def filepaths(self, filepart_type=None, absolute=False, no_duplicates=True,
                  no_blanks=True, se_vals=None, **kwargs):
        """Get all the TuflowFile filepaths that match the criteria.

        Filepaths will be returned in order.

        **kwargs:
            active_only: if True only the TuflowPart's with the 'active' flag
                set to True will be returned.
            by_parent: if True a dict where keys are parent filename and 
                extension will be returned. Each dict value is a list of paths.
            exclude(list): filepart_type's that should not be included
                in the return list.
            user_vars(dict): containing placeholder variables as keys and the 
                required values as values. (see TuflowPart.resolvePlaceholder() 
                for more information.

        Args:
            filepart_type=None: the FILEPART_TYPES value to check. If None all
                TuflowFile types will be checked. You can also supply a list of
                multiple filepart_type's.
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
        active_only = kwargs.get('active_only', True)
        by_parent = kwargs.get('by_parent', False)
        exclude = kwargs.get('exclude', [])
        user_vars = kwargs.get('user_vars', None)
        if filepart_type is None:
            filepart_type = []
        elif not isinstance(filepart_type, list):
            filepart_type = [filepart_type]
        paths = []
        parents = {}
        for part in self.parts:
            if active_only and not part.active:
                continue
            p = None
            if not isinstance(part, TuflowFile):
                continue
            if filepart_type and not part.filepart_type in filepart_type:
                continue
            if part.filepart_type in exclude:
                continue
            if se_vals is not None:
                if not self.checkPartLogic(part, se_vals):
                    continue

            if absolute:
                p = part.absolutePath(user_vars)
            else:
                p = part.filenameAndExtension(user_vars)

            if no_duplicates and p in paths:
                continue
            if no_blanks and p.strip() == '':
                continue
            if p is not None:
                if by_parent:
                    if not part.associates.parent.filenameAndExtension() in parents.keys():
                        parents[part.associates.parent.filenameAndExtension()] = []
                    parents[part.associates.parent.filenameAndExtension()].append(p)
                else:
                    paths.append(p)

        if by_parent:
            return parents
        else:
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

    def checkPathsExist(self, se_vals=None, **kwargs):
        """Check that all of the TuflowFile type's absolute paths exist.

        Args:
            se_vals=None(dict): to select only those TuflowFile's that are 
                within certain scenario and event clauses.

        Return:
            list - containing all TuflowFile's that failed the check.
        """
        active_only = kwargs.get('active_only', True)
        failed = []
        for part in self.parts:
            if active_only and not part.active:
                continue
            if not isinstance(part, TuflowFile):
                continue
            if not os.path.exists(part.absolutePath()):
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

    def getPrintableContents(self, se_vals=None, **kwargs):
        """Return the control files with contents formatted for writing to file.

        **kwargs:
            active_only=True(bool): if True only the parts with 'active' status
                set to True will be included.
            parents(list): a list of parents (tuflow control files) to return.
                if not given all the parents in self.control_files will be
                returned.

        Args:
            se_vals(dict): containing scenario and event values to define the
                search criteria.

        Return:
            dict - control files paths as keys and a ordered list of Tuflow
                commands as the values.
        """
        def createIndent(indent):
            if indent < 1:
                return ''
            else:
                return ''.join(['\t' for x in range(indent)])

        active_only = kwargs.get('active_only', True)
        parents = kwargs.get('parents', self.control_files)
        for p in parents:
            if not p in self.control_files:
                raise ValueError("All 'parents' must be in self.control_files'")

        logic_stack = {}
        logic_group = {}
        cur_ctrl = None
        out = {}
        parent_indents = {}
        open_logic = 0

        for p in self.parts:
            if not p.associates.parent in parents:
                continue
            if not cur_ctrl == p.associates.parent.hash:
                cur_ctrl = p.associates.parent.hash
            if not cur_ctrl in out.keys():
                out[cur_ctrl] = []
                logic_stack[cur_ctrl] = []
                logic_group[cur_ctrl] = []
                parent_indents[cur_ctrl] = 0

            part_active = False
            if active_only and p.active:
                part_active = True
            if se_vals is None or (se_vals is not None and
                                   self.checkPartLogic(p, se_vals)):
                part_active = True

            # Get any logic clauses that appear above this part
            if p.associates.logic is not None:
                # Helps track open logic clauses when parts are inactive
                logic_clause = []
                logic_clause = p.associates.logic.getPrintableContents(
                    p, logic_clause)
                for i, l in enumerate(logic_clause):
                    open_logic += 1
                    out[cur_ctrl].append(createIndent(parent_indents[cur_ctrl]) + l)
                    parent_indents[cur_ctrl] += 1

            # Get the part
            if part_active:
                pout, add_to_prev = p.getPrintableContents()
                if add_to_prev:
                    out[cur_ctrl][-1] = out[cur_ctrl][-1] + pout
                else:
                    out[cur_ctrl].append(createIndent(parent_indents[cur_ctrl]) + pout)

            # Get any closing statements for logic clauses
            if p.associates.logic is not None:
                logic_clause = p.associates.logic.getEndClause(p)
                parent_indents[cur_ctrl] -= 1
                if logic_clause and open_logic > 0:
                    out[cur_ctrl].append(createIndent(parent_indents[cur_ctrl]) + logic_clause)
                    open_logic -= 1

        for c in self.control_files:
            if c.hash in out.keys():
                path = c.absolutePath()
                out[path] = out.pop(c.hash)
        return out

    def write(self, overwrite=False, **kwargs):
        """Write the control files to disk.

        Calls the getPrintableContents function and then writes the returned
        contents to file.

        **kwargs:
            active_only=True(bool): if True only the parts with 'active' status
                set to True will be included.
            parents(list): a list of parents (tuflow control files) to return.
                if not given all the parents in self.control_files will be
                returned.

        Args:
            overwrite=False(bool): if set to True it will overwrite an existing
                file without warning. If False it will raise an error if the
                file already exists.
        """
        contents = self.getPrintableContents(**kwargs)
        for ckey in contents.keys():
            if os.path.exists(ckey) and not overwrite:
                raise IOError('File %s already exists. Use overwrite=True to ignore this warning' % ckey)

        for ckey, cval in contents.items():
            i = 0
            filetools.writeFile(cval, ckey)

    def removeLogicPart(self, remove_part, last_part):
        """Called when a TuflowPart is removed from a TuflowLogic.

        This is mostly for use by a callback function in TuflowLogic parts. It
        makes sure that when a TuflowPart is removed from a TuflowLogic it is
        moved outside of the scope of the TuflowLogic in the PartHolder.
        """
        # If it was the only part left in the TuflowLogic there's no need to
        # move anything because the logic is finished
        if last_part is None:
            return

        del_index = self.parts.index(remove_part)
        last_index = self.parts.index(last_part)
        if del_index == -1:
            raise IndexError('remove_part (%s) does not exist in PartHolder' % remove_part.hash)
        if last_index == -1:
            raise IndexError('last_part (%s) does not exist in PartHolder' % last_part.hash)

        self.parts.remove(remove_part)
        if last_index + 1 >= len(self.parts.parts):
            self.parts.parts.append(remove_part)
        else:
            # It's not last_index + 1 becuase we lost an index when removing
            # the old one
            next_part = self.parts[last_index]
            self.parts.add(remove_part, before=next_part)

    def addLogicPart(self, add_part, adjacent_part, **kwargs):
        """Called when a TuflowPart is added to a TuflowLogic.

        **kwargs:
            'after': the part after the one being added.
            'before': the part before the one being added.

        If both 'after' and 'before' are given in kwargs, or neither are given,
        'after' will take precedence.

        This is mostly for use by a callback function in TuflowLogic parts. It
        makes sure that when a TuflowPart is added to a TuflowLogic it is
        also added to the PartHolder.
        """
        after = kwargs.get('after', False)
        before = kwargs.get('before', False)
        if not after and not before:
            after = True
        if after and before:
            after = True

        if after:
            self.parts.add(add_part, after=adjacent_part)
        else:
            self.parts.add(add_part, before=adjacent_part)

    def contains(self, se_vals=None, **kwargs):
        """Find TuflowPart variables that contain a particular string or value.

        All searches are case insensitive.

        **kwargs:
            command(str): text to search for in a TuflowPart.command.
            variable(str): characters to search for in a TuflowPart.variable.
            filename(str): text to search for in a TuflowPart.filename.
            parent_filename(str): text to search for in a 
                TuflowPart.associates.parent.filename.
            active_only(bool): if True only parts currently set to 'active' will
                be returned. Default is True.
            exact(bool): Default is False. If set to True it will only return an
                exact match, otherwise checks if the str is 'in'.

        Args:
            se_vals(dict): containing scenario and event values to define the
                search criteria.

        Return:
            list - of TuflowParts that match the search term.
        """
        command = kwargs.get('command', '').upper()
        variable = kwargs.get('variable', '').upper()
        filename = kwargs.get('filename', '').upper()
        parent_filename = kwargs.get('parent_filename', '').upper()
        active_only = kwargs.get('active_only', True)
        exact = kwargs.get('exact', False)
        results = []
        for part in self.parts:
            out = None
            if active_only and not part.active:
                continue
            if se_vals is not None:
                if not self.checkPartLogic(part, se_vals):
                    continue

            if parent_filename:
                try:
                    if exact:
                        if parent_filename == part.associates.parent.filename.upper():
                            out = part
                    elif parent_filename in part.associates.parent.filename.upper():
                        out = part
                    else:
                        continue
                except AttributeError:
                    continue
            if command:
                try:
                    if exact:
                        if command == part.command.upper():
                            out = part
                    elif command in part.command.upper():
                        out = part
                    else:
                        continue
                except AttributeError:
                    continue
            if variable:
                try:
                    if exact:
                        if variable == part.variable.upper():
                            out = part
                    elif variable in part.variable.upper():
                        out = part
                    else:
                        continue
                except AttributeError:
                    continue
            if filename:
                try:
                    if exact:
                        if filename == part.filename.upper():
                            out = part
                    if filename in part.filename.upper():
                        out = part
                    else:
                        continue
                except AttributeError:
                    continue

            if out is not None:
                results.append(out)

        return results

    def allParentHashes(self, parent_hash, iterator):
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

    def controlFileIndices(self, parent_file, **kwargs):
        """Get the last index of TuflowParts with particular parent.

        **kwargs:
            'start'(bool): only returns the start indices of the control file.
            'end'(bool): only returns the end indices of the control file.
            'both'(bool): return the start and end indices of the control file.
            'part'(bool): returns the parts in that control file as well.

        If not kwargs are supplied 'both' and 'part' are assumed.

        The dict returned will vary in structure depending on the kwargs 
        provided. All keys are X_parts, X_logic, X_cfile where 'X' is either
        'start', 'end', 'part' to match the args given. E.g::

            outputs = {
                'start_part': PartHolder start index,
                'start_logic': LogicHolder start index,
                'start_cfile': control_files start index,
                'part_part': [TuflowPart, TuflowPart],
                ...etc
            }

        Args:
            parent_file(ModelFile): to check for last occurence of in self.parts.

        Return:
            dict - with last index of 'parts', 'logic' and 'control_files'
        """
        start = kwargs.get('start', False)
        end = kwargs.get('end', False)
        both = kwargs.get('both', False)
        parts = kwargs.get('part', False)
        p_part, p_sindex, p_eindex = self.allParentHashes(parent_file.hash, self.parts)
        l_part, l_sindex, l_eindex = self.allParentHashes(parent_file.hash, self.logic)
        c_part, c_sindex, c_eindex = self.allParentHashes(parent_file.hash, self.control_files)
        out = {}
        do_all = False
        if start == end == both == parts == False:
            do_all = True
        if start or both or do_all:
            out['start_part'] = p_sindex
            out['start_logic'] = l_sindex
            out['start_cfile'] = c_sindex
        if end or both or do_all:
            out['end_part'] = p_eindex
            out['end_logic'] = l_eindex
            out['end_cfile'] = c_eindex
        if parts or do_all:
            out['part_part'] = p_part
            out['part_logic'] = l_part
            out['part_cfile'] = c_part

        return out

    def removeControlFile(self, model_file):
        """Remove the contents of an existing ControlFile.

        Will return a dict with the starting indices of removed sections::

            indices = {
                'parts': int, 'logic': int, 'control_files': int
            }

        Args:
            model_file(ModelFile): the ModelFile that will be used to find the
                sections of this ControlFile to delete.
        """
        # First find all of the old controlfile parts to remove
        to_delete, _, _ = self.allParentHashes(model_file.hash, self.parts)

        # Then remove them
        to_delete.reverse()
        for part in to_delete:
            self.parts.remove(part)

        # Next the logic
        to_delete, _, _ = self.allParentHashes(model_file.hash, self.logic)

        # Then remove them
        to_delete.reverse()
        for logic in to_delete:
            self.logic.parts.remove(logic)

        # Finally the control_files
        to_delete, _, _ = self.allParentHashes(model_file.hash, self.control_files)
        to_delete.append(model_file)
        to_delete.reverse()
        for c in to_delete:
            self.control_files.remove(c)

    def addControlFile(self, model_file, control_file, **kwargs):
        """Add the contents of a new ControlFile to this ControlFile.

        **kwargs:
            'after': ModelFile to place the new ModelFile (model_file) after
                in terms of the ordering of the contents.
            'before': ModelFile to place the new ModelFile (model_file) before
                in terms of the ordering of the contents.

        If bother 'before' and 'after' are given after will take preference. If
        neither are given a ValueError will be raised.

        Args:
            model_file(ModelFile): the ModelFile that is being added.
            control_file(ControlFile): the Control to combine with this one.

        Raises:
            ValueError: if neither 'after' or 'before' are given.
        """
        if model_file in self.control_files:
            raise AttributeError('model_file already exists in this ControlFile')

        after = kwargs.get('after', None)
        before = kwargs.get('before', None)

        if after is not None:
            indices = self.controlFileIndices(after, end=True)
            self.parts.parts[indices['end_part']: indices['end_part']] = control_file.parts
            self.logic.parts[indices['end_logic']: indices['end_logic']] = control_file.logic
            self.control_files[indices['end_cfile']: indices['end_cfile']] = control_file.control_files
        elif before is not None:
            indices = self.controlFileIndices(before, start=True)
            self.parts.parts[indices['start_part']: indices['start_part']] = control_file.parts
            self.logic.parts[indices['start_logic']: indices['start_logic']] = control_file.logic
            self.control_files[indices['start_cfile']: indices['start_cfile']] = control_file.control_files

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
        self.addControlFile(model_file, control_file, before=replace_modelfile)
        self.removeControlFile(replace_modelfile)


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

    def append(self, filepart):
        """Adds part to the end of the parts list. 

        Most of the time you probably want to use the add() method with no
        'before' or 'after' kwarg, which will append the TuflowPart to the end
        of it's parent contents. Otherwise you will probably mess up the 
        ordering of the parts.
        """
        if not isinstance(filepart, TuflowPart):
            raise ValueError('filepart must be TuflowPart type')
        self.parts.append(filepart)

    def add(self, filepart, **kwargs):
        """

        If both after and before are supplied, after will take precedence.
        """
        after = kwargs.get('after', None)
        before = kwargs.get('before', None)
        suppress_add_same = kwargs.get('suppress_add_same', False)

        if filepart in self.parts:
            if not suppress_add_same:
                raise ValueError('filepart %s already exists.' % filepart.hash)

        # Insert after the after filepart
        if after is not None:
            index = self.index(after)
            if index == len(self.parts):
                filepart.associates.logic = after.associates.logic
                self.parts.append(filepart)
            else:
                filepart.associates.logic = after.associates.logic
                self.parts.insert(index + 1, filepart)

        # Insert before the before filepart
        elif before is not None:
            index = self.index(before)
            filepart.associates.logic = before.associates.logic
            self.parts.insert(index, filepart)
        else:
            # insert in the list after the last instance of filepart.parent
            found_parent = False
            if not self.parts:
                self.parts.append(filepart)
            else:
                index = self.lastIndexOfParent(filepart.associates.parent)
                if index == -1 or index + 1 >= len(self.parts):
                    self.parts.append(filepart)
                else:
                    self.parts.insert(index + 1, filepart)

    def replace(self, part, replace_part):
        """
        """
        index = self.parts.index(replace_part)
        if index == -1:
            raise ValueError('part does not exist in collection')

        part.associates.logic = replace_part.associates.logic
        self.parts.pop(index)
        self.parts.insert(index, part)

    def move(self, part, **kwargs):  # after):
        after = kwargs('after', None)
        before = kwargs('before', None)
        if after is None and before is None:
            raise AttributeError('Either before or after part must be given')
        take_logic = kwargs('take_logic', True)

        pindex = self.index(part)
        aindex = self.index(after)
        self.parts.insert(aindex, self.parts.pop(pindex))

    def index(self, part):
        if not isinstance(part, TuflowPart):
            raise ValueError('part must be TuflowPart type')
        try:
            return self.parts.index(part)
        except ValueError:
            return -1

    def lastIndexOfParent(self, parent):
        index = -1
        for i, p in enumerate(self.parts):
            if p.associates.parent == parent:
                index = i
        return index


#     def get(self, filepart, filepart_type=None):
#         """
#         """
#         part_hash, type_hash = self._checkPartKeys(filepart.hash, filepart_type)
#
#         return self.parts[filepart.part_type][filepart.hash]

    def remove(self, filepart):
        """
        """
        index = self.index(filepart)
        fpart = self.parts[index]
        del self.parts[index]
        return fpart


class LogicHolder(object):

    def __init__(self, remove_callback=None, add_callback=None):
        self.parts = []
        self._min = 0
        self._max = len(self.parts)
        self._current = 0
        self.remove_callback = remove_callback
        self.add_callback = add_callback

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
            if p.hash == hash:
                return p
        return None

    def add(self, logic):
        for l in logic:
            l.remove_callback = self.remove_callback
            l.add_callback = self.add_callback
            self.parts.append(l)


class TcfControlFile(ControlFile):

    def __init__(self, mainfile, remove_callback=None, replace_callback=None,
                 add_callback=None):
        self.model_type = 'TCF'
        self.parts = PartHolder()
        self.logic = LogicHolder()
        self.control_files = []
        self._mainfile = mainfile
        self.remove_callback = remove_callback
        self.replace_callback = replace_callback
        self.add_callback = add_callback

    @property
    def mainfile(self):
        return self._mainfile

    @mainfile.setter
    def mainfile(self, value):
        if not isinstance(value, ModelFile):
            raise ValueError('value must be of type ModelFile')
        if not value.model_type == 'TCF':
            raise ValueError("value must be model_type 'TCF'")
        self._mainfile = value
        if not value in self.control_files:
            self.control_files.append(value)

    def updateRoot(self, root, must_exist=True):
        """Update the root variable of all TuflowPart's.

        Args:
            root(str): the new directory path.
            must_exist=True(bool): if True and the given root directory doesn't
                exist it will raise a ValueError.
        """
        ControlFile.updateRoot(self, root, must_exist=must_exist)
        self._mainfile.root = root

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
        if not model_file.model_type == 'TCF':
            if self.remove_callback is None:
                raise AttributeError('remove_callback has not been defined')
            else:
                self.remove_callback(model_file)
        else:
            return ControlFile.removeControlFile(self, model_file)

    def addControlFile(self, model_file, control_file, **kwargs):
        """Add the contents of a new ControlFile to this ControlFile.

        **kwargs:
            'after': ModelFile to place the new ModelFile (model_file) after
                in terms of the ordering of the contents.
            'before': ModelFile to place the new ModelFile (model_file) before
                in terms of the ordering of the contents.

        If both 'before' and 'after' are given after will take preference. If
        neither are given a ValueError will be raised.

        Args:
            model_file(ModelFile): the ModelFile that is being added.
            control_file(ControlFile): the Control to combine with this one.

        Raises:
            ValueError: if neither 'after' or 'before' are given.
        """
        if not model_file.model_type == 'TCF':
            if self.add_callback is None:
                raise AttributeError('add_callback has not been defined')
            else:
                self.add_callback(model_file, control_file, **kwargs)
        else:
            ControlFile.addControlFile(self, model_file, control_file, **kwargs)

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
        if not model_file.model_type == 'TCF':
            if self.replace_callback is None:
                raise AttributeError('replace_callback has not been defined')
            else:
                self.replace_callback(model_file, control_file, replace_modelfile)
        else:
            ControlFile.replaceControlFile(self, model_file, control_file,
                                           replace_modelfile)
