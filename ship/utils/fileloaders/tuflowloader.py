from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""

import os
import uuid

from ship.tuflow import FILEPART_TYPES as fpt
from ship.utils import utilfunctions as uf
from ship.tuflow.tuflowmodel import TuflowModel, TuflowFilepartTypes, UserVariables
from ship.tuflow import controlfile as control
from ship.tuflow import tuflowfilepart as tuflowpart
from ship.utils.fileloaders.loader import ALoader
from ship.utils import filetools
from ship.tuflow import tuflowfactory as tfactory


class TuflowLoader(ALoader):

    def __init__(self):
        ALoader.__init__(self)
        self.types = TuflowFilepartTypes()

        self.user_variables = UserVariables()
#         self.scenario_vals = {}
#         """Any scenario values that are passed through."""
#
#         self.event_vals = {}
        """Any event values that are passed through."""

        self.tuflow_model = None
        """TuflowModel class instance"""

        # Internal stuff
        self._resetLoader()

    def _resetLoader(self):
        self._file_queue = uf.FileQueue()
        self.user_variables = UserVariables()
        self._load_list = {}
        self._file_list = {}
        self._logic_list = {}
        self._bc_event = {}
#         self.scenario_vals = {}
#         self.event_vals = {}
        self.tuflow_model = None
        self._control_files = []

    def loadFile(self, tcf_path, arg_dict={}):
        """Main loader function defined by the ALoader interface.

        The presumption with this loader is that a .tcf file (i.e. the root of
        all tuflow models will be given as a starting point. The rest of the
        model can then be accessed from there.
        """
        return self.loadModel(tcf_path, arg_dict)

    def loadModel(self, tcf_path, arg_dict={}):
        """Load a full tuflow model from the given tcf path."""
        self._resetLoader()

        if 'scenario' in arg_dict.keys():
            self._has_scenario = True

            self.user_variables.has_cmd_vals = True
            self.scenario_vals = arg_dict['scenario']
            for key, val in arg_dict['scenario'].items():
                self.user_variables.add(tuflowpart.TuflowModelVariable.noParent(key, val), 'scen')

        if 'event' in arg_dict.keys():
            self._has_event = True

            self.user_variables.has_cmd_vals = True
            self.event_vals = arg_dict['event']
            for key, val in arg_dict['event'].items():
                self.user_variables.add(tuflowpart.TuflowModelVariable.noParent(key, val), 'evnt')

        # Check that the tcf exists
        if not os.path.exists(tcf_path):
            raise IOError('Tcf file at %s does not exist' % tcf_path)
        root, tcf_name = os.path.split(tcf_path)
        root = uf.encodeStr(root)
#         root = unicode(root)
        tcf_name = uf.encodeStr(tcf_name)

        self.tuflow_model = TuflowModel(root)

        # Parse the tuflow control files
        main_file = tuflowpart.ModelFile(None, **{'path': tcf_name, 'command': None,
                                                  'comment': None, 'model_type': 'TCF',
                                                  'root': root})
        tcf_path = main_file.absolutePath()
#         self.tuflow_model.main_file = main_file

        # Setup the file and object holders
        self._file_queue.enqueue(main_file)

        # Read the control files and their contents into memory
        self._fetchTuflowModel(root)

        # Order the input and create the actual ControlFile objects
        self._orderModel(tcf_path)

        # Return the loaded model
        self.tuflow_model.root = root
        self.tuflow_model.control_files = self._control_files
        self.tuflow_model.bc_event = self._bc_event
        self.tuflow_model.user_variables = self.user_variables
        self.tuflow_model.control_files['TCF'].add_callback = self.tuflow_model.addTcfModelFile
        self.tuflow_model.control_files['TCF'].remove_callback = self.tuflow_model.removeTcfModelFile
        self.tuflow_model.control_files['TCF'].replace_callback = self.tuflow_model.replaceTcfModelFile
        self.tuflow_model.missing_model_files = self.missing_model_files
        return self.tuflow_model

    def loadControlFile(self, model_file):
        """
        """
        path = model_file.absolutePath()
        if not os.path.exists(path):
            raise IOError('model_file path does not exists at: ' + path)

        self._resetLoader()
        root = model_file.root
        self._file_queue.enqueue(model_file)
        self._fetchTuflowModel(root)
        _load_list = self._load_list[path]
        model = self._file_list[path]
        mtype = model_file.model_type

        self.current_control = [mtype]
        self._control_files = {mtype: control.ControlFile(mtype)}
        self._control_files[mtype].logic.add(self._logic_list[path])
        self._control_files[mtype].control_files.append(model_file)
        self.buildControlFiles(_load_list, model)
        return self._control_files[mtype]

    def _orderModel(self, tcf_path):
        """Setup the ControlFile's with ordered TuflowFilepart's.

        There will always be a tcf file as an entry point, so that is setup
        first. Then builControlFiles is called to deal with all the others.
        """
        _load_list = self._load_list[tcf_path]
        model = self._file_list[tcf_path]
        self.current_control = ['TCF']
        self._control_files = {'TCF': control.TcfControlFile(model)}
        self._control_files['TCF'].logic.add(self._logic_list[tcf_path])
        self._control_files['TCF'].control_files.append(model)
        self.buildControlFiles(_load_list, model)

    def buildControlFiles(self, _load_list, model):
        """Add TuflowFilepart's to the correct ControlFile's.

        Loops through the list of TuflowFilePart's created when parsing the
        tuflow input files. When it finds a TuflowFilepart containing a
        reference to a tuflow control file it will recursively call itself and
        start adding parts to the ControlFile for that type instead. It will
        either find another control file and, again, make a recursive call, or
        will finish adding the TuflowFileparts to the ControlFile and drop back
        into the previous function call (recursive) to continue reading the
        previous list of TuflowFilepart's.

        """
        for part in _load_list:
            self._control_files[self.current_control[-1]].parts.append(part)
            if part.obj_type == 'model':
                p = part.absolutePath()
                if p in self.missing_model_files:
                    continue
                if not part.model_type in self._control_files.keys():
                    self._control_files[part.model_type] = control.ControlFile(part.model_type)
                    self._control_files[part.model_type].logic.add(self._logic_list[p])
                self.current_control.append(part.model_type)
                self._control_files[part.model_type].control_files.append(part)
                self.buildControlFiles(self._load_list[p], self._file_list[p])

            elif part.associates.parent.model_type == 'TCF' and part.filepart_type == fpt.EVENT_VARIABLE:
                self._bc_event[part.command] = part.variable

        self.current_control.pop()

    '''
        #
        Control file parsers.
        #
    '''

    def _fetchTuflowModel(self, root):
        """Read all of the control files into memory.
        """
        self.missing_model_files = []

        # Keep processing control files until there are none left in the queue
        while not self._file_queue.isEmpty():
            control_part = self._file_queue.dequeue()
            cpath = control_part.absolutePath()
            raw_contents = self.getFile(cpath)

            # If we couldn't load the file add it to the missing list
            if raw_contents == False:
                self.missing_model_files.append(cpath)
                continue

            contents, logic = self._readControlFile(raw_contents, root, control_part)
            self._load_list[cpath] = contents
            self._logic_list[cpath] = logic
            self._file_list[cpath] = control_part

        del self._file_queue

    def _readControlFile(self, raw_contents, root, control_part):
        """Load the content of a control file.
        """
        contents = []
        unknown_store = []
        logic = []
        logic_done = []
        factory = tfactory.TuflowFactory()

        def createUnknown(unknown_store, l):
            """Creates an UnknownPart from the current list."""
            if unknown_store:
                vars = {}
                vars['data'] = '\n'.join(unknown_store)
                vars['logic'] = l
                contents.append(tuflowpart.UnknownPart(control_part, **vars))
            return []

        def addLogicAssociate(lpart, logic_stack):
            if logic:
                lpart.associates.logic = logic[-1]
                logic[-1].addPart(lpart, skip_callback=True)
            logic.append(lpart)
            return logic

        for line in raw_contents:

            current_logic = logic[-1] if logic else None
            line = line.strip()
            upline = line.upper()

            if tfactory.checkIsComment(line):
                unknown_store.append(line)
                continue

            found, key = self.types.find(upline)

            # If we don't know what it is
            if not found:
                unknown_store.append(line)
                continue
            else:
                unknown_store = createUnknown(unknown_store, current_logic)

            # Build logic types
            if key == fpt.IF_LOGIC:
                vars = self.parseIfLogic(line, control_part, root, key)
                if vars['command'].upper().strip().startswith('IF'):
                    lfile = tuflowpart.IfLogic(control_part, **vars)
                    logic = addLogicAssociate(lfile, logic)
                elif vars['command'].upper().strip().startswith('END IF'):
                    logic_done.append(logic.pop())
                else:
                    current_logic.addClause(vars['command'], vars['terms'], vars['comment'])
                continue

            elif key == fpt.EVENT_LOGIC or key == fpt.SECTION_LOGIC:
                vars = self.parseDefineLogic(line, control_part, key)
                if vars['command'].upper().strip().startswith('END'):
                    logic_done.append(logic.pop())
                else:
                    if key == fpt.EVENT_LOGIC:
                        dfile = tuflowpart.BlockLogic(control_part, **vars)
                    else:
                        dfile = tuflowpart.SectionLogic(control_part, **vars)
                    logic = addLogicAssociate(dfile, logic)
                continue

            # All other FilePart types
            else:
                parts = factory.getTuflowPart(line, control_part, key, current_logic)
                if key == fpt.MODEL:
                    for p in parts:
                        self._file_queue.enqueue(p)
                if key == fpt.MODEL_VARIABLE:
                    for p in parts:
                        if not self.user_variables.has_cmd_args:
                            self.user_variables.add(p)
                if key == fpt.USER_VARIABLE:
                    for p in parts:
                        self.user_variables.add(p)

            for p in parts:
                contents.append(p)
                if logic:
                    current_logic.addPart(p, skip_callback=True)

        unknown_store = createUnknown(unknown_store, current_logic)
        return contents, logic_done

    '''
        #
        TuflowFilepart type builders.
        #
    '''

    def parseDefineLogic(self, line, parent, key):
        vars = {}
        command, vars['comment'], cchar = tfactory.separateComment(line)
        if '==' in line:
            vars['command'], vars['terms'] = tfactory.breakLine(command)
            vars['terms'] = [vars['terms']]
        else:
            vars['command'] = command
            vars['terms'] = None
        vars['filepart_type'] = key
        return vars

    def parseIfLogic(self, line, parent, root, key):
        vars = {}
        command, vars['comment'], cchar = tfactory.separateComment(line)
        if '==' in line:
            vars['command'], vars['terms'] = tfactory.breakLine(command)
            vars['terms'] = vars['terms'].split('|')
        else:
            vars['command'] = command
            vars['terms'] = None
        vars['type'] = key
        return vars

    def _addModelVariable(self, part):
        """Adds any model variables read in to the global variables dict.

        The dict will only be updated if there are no values in it already.
        This is inline with the Tuflow manual guidance.

        Args:
            part(TuflowVariable): with self.filepart_type == FILEPART_TYPE.MODEL_VARIABLE.
        """
        if not part.filepart_type == fpt.MODEL_VARIABLE:
            return
        if 'EVENT' in part.command.upper():
            if not self.event_vals:
                for i, e in enumerate(part.split_variable):
                    self.event_vals['e' + uf.encodeStr(i + 1)] = e
        else:
            if not self.scenario_vals:
                for i, s in enumerate(part.split_variable):
                    self.scenario_vals['s' + uf.encodeStr(i + 1)] = s

    '''
        #
        File processing methods
        #
    '''

    def getFile(self, path):
        """Load the file into the contents list.

        Args:
            file_path (str): path to the required file.

        Returns:
            True if loaded ok, False otherwise.
        """
        logger.debug('loading File: ' + path)
        try:
            raw_contents = filetools.getFile(path)
        except IOError:
            logger.error('IOError - Unable to load file')
            return False

        if(raw_contents == None):
            logger.error('model file is empty at: ' + path)
            return False

        return raw_contents
