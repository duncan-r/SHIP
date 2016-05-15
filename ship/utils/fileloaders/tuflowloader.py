"""

 Summary:
    Contains the TuflowLoader class.
    This is used to read in the files that make up a Tuflow model. i.e. the
    tcf, tgc, etc files that the model requires to be run.
    Returns a Tcf object that contains references to the other model file
    types and all of the files identified within those models

 Author:  
     Duncan Runnacles

  Created:  
     01 Apr 2016

 Copyright:  
     Duncan Runnacles 2016

 TODO:
    Given file must be a .tcf at the  moment. This should be changed so that an
    .ecf can be provided as well.

 Updates:

"""


import os
import hashlib
import re

from ship.utils import filetools
from ship.utils.fileloaders.loader import ALoader
from ship.utils import utilfunctions as uf
from ship.utils.atool import ATool
from ship.tuflow.tuflowmodel import TuflowModel, TuflowTypes, ModelRef, ModelOrder
from ship.tuflow.tuflowmodelfile import TuflowModelFile, TuflowScenario
from ship.tuflow import FILEPART_TYPES as ft
from ship.tuflow import tuflowfilepart as tfp

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class TuflowLoader(ATool, ALoader):
    """Loads all the data referenced by a .tcf file.
    
    Calling the :method:'load' function of this with a path to a tcf file
    will read in all of content of all the files it references.
    
    The load function will return an instance of :class:'TuflowModel'.
    
    See Also:
        TuflowModel
        ModelOrder
        TuflowTypes
        ModelRef
    """
    
    def __init__(self):
        """Initialise defaults"""

        ATool.__init__(self)
        logger.debug('Initialising TuflowLoader')
        
        self.file_types = {'mif': tfp.GisFile, 'mid': tfp.GisFile, 
                           'shp': tfp.GisFile, 'tmf': tfp.DataFile,
                           'csv': tfp.DataFile}
        """Associates a range of different known file extensions with the
        Class types that deal with them.
        """

        self.types = TuflowTypes()
        """A lookup table containing the known keywords used as instructions
        in Tuflow files and the categories that they are put under.
        """
        

    def loadFile(self, tcf_path, arg_dict={}):
        """Loads all content referenced by the given path.
        
        The arg_dict dictionary is used to pass in any values needed at runtime
        for resolving scenario and event logic in the control files. These are
        the ~s~ and ~e~ values that are specified either in the tcf file or
        on the command line/batch file. They are submitted as two separate
        sub-dicts that contain the values for this run. E.g:
        ::
            > tuflow.exe -s1 scen1 -e1 100yr -e2 4h myfile_~s1~_~e1~_~e2~_place.tcf  
            
            To provide these variables for use by the tuflow loader, so it would
            know how to load any .tcf file with those tilde values in, you could
            do:  
            
            tcfpath = 'C:\path\to\tcf\myfile_~s1~_~e1~_~e2~_place.tcf'
            args_dict = {'scenario': {'s1': 'scen1'}, 'event': {'e1': '100yr', 'e2': '4h'}}
            loader = FileLoader()
            tuflow_model = loader.loadFile(tcfpath, args_dict)            
        
        Args:
            tcf_path(str): path to a .tcf file.
            arg_dict={}(Dict): contains scenario variables for the tuflow model
                being loaded. E.g. tuflow files can be referenced using 
                charactars within tildes (~s~ or ~e~) to indicate placeholders.
                The scenario and event values are passed in as two separate 
                dicts under the main dict keys 'scenario' and 'event'.
        
        Raises:
            ValueError: if tcf_path is not a .tcf file.
            IOError: if tcf_path doesn't exist.
        """
        logger.info('Loading Tuflow model')
        if not uf.checkFileType(tcf_path, ext=['.tcf', '.TCF']):
            logger.error('File: ' + tcf_path + '\nDoes not match tcf extension (*.tcf or *.TCF)')
            logger.error('Illegal File Error: %s in not of type tcf' % (tcf_path))
            raise AttributeError ('Illegal File Error: %s in not of type tcf' % (tcf_path))
        
        # If the file doesn't exist raise an exception
        if not os.path.exists(tcf_path) or not os.path.isabs(tcf_path):
            logger.error('.tfc path must exist and MUST be absolute')
            raise IOError ('Tcf file does not exist')
        
        self.scenario_vals = {}
        """Any scenario values that are passed through."""
        
        if 'scenario' in arg_dict.keys(): self.scenario_vals = arg_dict['scenario']
        
        self.event_vals = {}
        """Any event values that are passed through."""
        
        if 'event' in arg_dict.keys(): self.event_vals = arg_dict['event']

        self.tuflow_model = TuflowModel()
        """TuflowModel class instance"""
        
        self._file_queue = uf.FileQueue()
        """FileQueue instance. Used to store all TuflowModelFile references
        found during loading so that they can be loaded in order.
        """
        
        self._model_order = ModelOrder()
        """Keeps track of the order of the files loaded in. Is given to the
        TuflowModel object so that it knows which files reference which 
        other files
        """
        
        self._global_order = 0
        """Tracks the number of file parts."""

        self._fetchTuflowModel(tcf_path)
        self.tuflow_model.model_order = self._model_order
        self.tuflow_model.scenario_vals = self.scenario_vals
        self.tuflow_model.event_vals = self.event_vals
        return self.tuflow_model

    
    def _fetchTuflowModel(self, tcf_path):
        """Does the actual loading"""
        
        # Load the file load details into the class
        model_details = [tcf_path, None, None, ''] 
        file_d = self._FileDetails(model_details, True)
        if not file_d.getFile(): raise IOError
        model = file_d.getModel()
        
        # Add reference to the model route to the tuflow_model
        self.tuflow_model.root = file_d.root

        # Add file reference to the appropriate structures
        # Handed true because it is the root node.
        self._model_order.addRef(ModelRef(file_d.head_hash, file_d.extension), True)
        
        # Need to create one here becuase it's the first
        line_val = file_d.generateModelTuflowFile(ft.MODEL, self._global_order)
        self._global_order += 1
        self.tuflow_model.mainfile = line_val
        self.tuflow_model.files[file_d.extension][file_d.head_hash] = model

        # Parse the contents into object form
        self._parseFileContents(file_d, model)
        
        # Do the same thing again for all the other files found
        while not self._file_queue.isEmpty():
            
            model_details = self._file_queue.dequeue()
            file_d = self._FileDetails(model_details, False)
            success = file_d.getFile()
            if success == False:
                self.tuflow_model.missing_model_files.append(file_d.filename)
                continue
            
            else:
                model = file_d.getModel()
                self._model_order.addRef(ModelRef(file_d.head_hash, file_d.extension, 
                                                            file_d.parent_hash))
                self.tuflow_model.files[file_d.extension][file_d.head_hash] = model
                self._parseFileContents(file_d, model)


    def _parseFileContents(self, file_d, model):
        """Parse the current file contents and build all the objects.
        
        Creates an object for (almost*) each line in the file and adds it to
        the object and reference lists. 
        
        There are a few places that keep refs to these objects 
        (the TuflowModelFile, TuflowModel) for various reasons. Only 
        TuflowModel.file_parts actually stores the object though.
        
        Args:
            file_d(_FileDetails): stores info about the current file.
            model(TuflowModel): stores references to the loaded objects.
        
        * If there are multiple comments or unknown lines in a row they will
          be lumped together.
        """
        def _clearUnknownContents(file_d, line, model, unknown_contents):
            """Stash and clear any unkown stuff."""

#             c_hash = file_d.generateHash('comment' + line + str(
#                                                 file_d.parent_hash))
            model.addContent(ft.COMMENT, unknown_contents)
            unknown_contents = []
            return unknown_contents

        
#         contents = []
        scenario_stack = uf.LoadStack()
        scenario_order = 0
        unknown_contents = []
        for line in file_d.raw_contents:
            line_contents = self._getLineDetails(line, file_d)
            line_type = line_contents[0][2]

            if line_type == ft.COMMENT or line_type == ft.UNKNOWN:
                unknown_contents.append(line_contents[0][0])
            
            # Add or remove an if-else scenario object from the stack. When they
            # are removed they are added to the model. 
            elif line_type == ft.SCENARIO:
                rettype, scenario = self.breakScenario(line_contents[0][0],
                                                       line_contents[0][1],
                                                       scenario_order)
                if rettype == 'IF':
                    # If it's an embedded if we need to give a reference to the
                    # parent TuflowScenario as well
                    if not scenario_stack.isEmpty():
                        scenario_stack.peek().addPartRef(TuflowScenario.SCENARIO_PART,
                                                          line_contents[0][1])
                    scenario_stack.add(scenario)
                    scenario_order +=1
                    model.addContent(line_type, line_contents[0][1])

                elif rettype == 'ELSE':
                    model.addContent(ft.SCENARIO_END, '')
                    s = scenario_stack.pop()
                    model.addScenario(s)
                    scenario_order +=1
                    if not scenario_stack.isEmpty():
                        scenario_stack.peek().addPartRef(TuflowScenario.SCENARIO_PART,
                                                          line_contents[0][1])
                    scenario_stack.add(scenario)
                    model.addContent(line_type, line_contents[0][1])
                else:
                    s = scenario_stack.pop()
                    s.has_endif = True
                    model.addContent(ft.SCENARIO_END, '')
                    model.addScenario(s)
            
            else:
                # Stash and clear any unknown stuff first if it's there.
                if unknown_contents:
                    unknown_contents = _clearUnknownContents(file_d, line, model, 
                                                             unknown_contents)
                
                # Add the new object to the TuflowModelFile
                for l in line_contents:
                    
                    line_val, hex_hash, line_type, ext = l

                    model.addContent(line_type, line_val)
                    if not scenario_stack.isEmpty():
                        scenario_stack.peek().addPartRef(TuflowScenario.TUFLOW_PART, 
                                                          hex_hash)
                    
                    if line_type == ft.MODEL: 
                        line_val, hex_hash, line_type, ext = line_contents[0]

                        rel_root = ''
                        if not line_val.relative_root is None:
                            rel_root = line_val.relative_root
                        self._file_queue.enqueue([line_val.getAbsolutePath(), hex_hash, 
                                                  file_d.head_hash, rel_root])

        # Make sure we clear up any leftovers
        if unknown_contents:
            unknown_contents = _clearUnknownContents(file_d, line, model, 
                                                     unknown_contents)
            
    
    def _getLineDetails(self, line, file_d):
        """Constructs the appropriate object from the file line.
        
        Takes a line from the file and decides what to do with it...and does
        it. This includes:
        # Checking if it's a comment or has any contents.
        # seperating the components if it's an instruction.
        # Deciding on what type of object to create (if any)
        # Creating the appropriate object and returning it. 
        
        This function is a bit messy, but it's hard to break up. It's 
        tempting to add a lot of it to :class:'TuflowFilePart' and let it
        deal with it in a nice polymorphic manner.
        
        Args:
            line(str): the file line to be dealt with.
            file_d(_FileDetails): object containing the current file data.
        
        Returns:
            Tuple - (line_val, hex_hash, command_type, ext):
                # the object created from the line.
                # the hexidecimal hash value created for the object.
                # the category that the object has been put in.
                # the extension of the file or '' if none found.
        """
        hex_hash = file_d.generateHash(file_d.filename + line + str(
                                                        file_d.parent_hash))
        line = line.lstrip()
        upline = line.upper()
        line_val = '\n'
        ext = ''
        
        # It's a comment or blank line
        if line.startswith('#') or line.startswith('!'):
            line_val = line
            command_type = ft.COMMENT 
            
        elif line.strip() == '':
            command_type = ft.COMMENT 
        
        # If scenario statement
        elif upline.startswith('IF SCENARIO') or upline.startswith('ELSE IF') \
                    or upline.startswith('END IF') or upline.startswith('ELSE'):
            command_type = ft.SCENARIO
            line_val = line
        
        elif '==' in line or 'AUTO' in line.upper():

            # Estry AUTO 
            if 'AUTO' in line.upper():
                line = self._breakAuto(line, file_d.filename)
                self.tuflow_model.has_estry_auto = True

            command, instruction = self._breakLine(line)
            found, command_type = self.types.find(command.upper())
            
            # TODO: Not sure about this at the moment. I think these should be
            #       going into UNKNOWN FILE, if a file, so we can still update 
            #       them when needed. Even if we don't know what they do?
            if not found:
                command_type = ft.UNKNOWN 
                line_val = line
            else:
                if command_type == ft.VARIABLE: 
                    line_val = tfp.ModelVariables(self._global_order, instruction, 
                                            hex_hash, command_type, command)
                    self._global_order += 1
                else:
                    # Do a check for MI Projection and SHP projection
                    isfile = True
                    if command.upper() == 'MI PROJECTION' or command.upper() == 'SHP PROJECTION':
                        isfile = self._checkProjectionIsFile(instruction)

                    if not isfile:
                        line_val = line
                        command_type = ft.COMMENT 
                    else:    
                        ext = self.extractExtension(instruction)
                        f_type = self.file_types.get(ext)
                        
                        # It's a model file or a results file
                        # TODO: Not safe yet...needs more work.
                        if f_type == None:

                            # If it's a .trd file give it the extension of the
                            # model file type that it's in (.tcf/.tgc/etc)
                            if ext is 'trd':
                                ext = file_d.extension
                            line_val = tfp.TuflowFile(self._global_order, instruction, 
                                                    hex_hash, command_type, 
                                                    command, file_d.root, 
                                                    file_d.relative_root, ext)
                            self._global_order += 1

                            if command_type is ft.RESULT: 
                                line_val = self._resolveResult(line_val)
                        
                        # It's one of the files in self.types
                        else:
                            piped_files, pipe_hashes = self.checkForPipes(instruction,
                                                                        file_d, hex_hash)
                            multi_lines = []
                            for i, p in enumerate(piped_files):
                                hex_hash = pipe_hashes[i] 
                                
                                # If there's a piped file command we need to register
                                # associated files with each other
                                hex_hash = pipe_hashes[i]
                                child_hash = None
                                parent_hash = None
                                if len(piped_files) > i+1:
                                    child_hash = pipe_hashes[i+1]
                                if i > 0:
                                    parent_hash = pipe_hashes[i-1]
                                    
                                line_val = self.file_types[ext](self._global_order, 
                                                                p, hex_hash, 
                                                                command_type, command, 
                                                                file_d.root, 
                                                                file_d.relative_root,
                                                                parent_hash=parent_hash,
                                                                child_hash=child_hash)
                                multi_lines.append([line_val,
                                                   hex_hash,
                                                   command_type,
                                                   ext]) 
                                
                            # TODO: currently the same _global_order for all the
                            #       files in a piped command. Should they be 
                            #       different?
                            self._global_order += 1
                            return multi_lines

        else:
            command_type = ft.UNKNOWN 
            line_val = line
        
        # Needs to be return in a list because of the multi_lines setup above.
        return [[line_val, hex_hash, command_type, ext]]
    
    
    def breakScenario(self, instruction, hex_hash, order):
        """Breaks a scenario IF statement down into parts.
        
        Args:
            instruction(str): the if statement to break up.
            hex_hash(str): the hash code for this line.
            order(int): the order this scenario appears in the file.
            
        Return:
            tuple(str, TuflowScenario or None):  
        """
        found, split, comment_char = self.separateComment(instruction)
        comment = ''
        if found: comment = split[1].strip()
        instruction = split[0].strip()
        
        scenario = None
        upinstruction = instruction.upper()
        
        if 'ELSE' in upinstruction and not 'IF' in upinstruction:
            scen_vals = ['ELSE']
            return_type = 'ELSE'
            scenario = TuflowScenario(TuflowScenario.ELSE, scen_vals, hex_hash,
                                       order, comment, comment_char)
        elif 'ELSE IF SCENARIO' in upinstruction:
            scen_vals = instruction.split('==')[1].strip()
            scen_vals = scen_vals.split('|')
            scen_vals = [val.strip() for val in scen_vals]
            return_type = 'ELSE'
            scenario = TuflowScenario(TuflowScenario.ELSE, scen_vals, hex_hash,
                                       order, comment, comment_char)
        elif 'IF SCENARIO' in upinstruction:
            scen_vals = instruction.split('==')[1].strip()
            scen_vals = scen_vals.split('|')
            scen_vals = [val.strip() for val in scen_vals]
            return_type = 'IF'
            scenario = TuflowScenario(TuflowScenario.IF, scen_vals, hex_hash,
                                       order, comment, comment_char)       
        else:
            return_type = 'END'
        
        return return_type, scenario
        
    
    def checkForPipes(self, instruction, file_d, hex_hash):
        """Checks the instruction command to see if it contains multiple files.
        
        Some commands in tuflow can contain multiple files seperate by a pipe
        "|" charactar. This checks to see if that's the case and returns the
        file names if so.
        """
        found, split, comment_char = self.separateComment(instruction)
        
        comment = ''
        if found: comment = split[1].strip()
        instruction = split[0].strip()

        instruction = instruction.split('|')
        
        hashes = []
        for i, val in enumerate(instruction):
            hashes.append(file_d.generateHash(hex_hash + val))
        
        if found:
            instruction[-1] = instruction[-1] + ' ' + comment_char + ' ' + comment
        
        return instruction, hashes

    
    def extractExtension(self, instruction):
        """Find the file extension in a file line.
        
        Args:
            instruction(str): the part of the line after the '=='
        
        Returns:
            String - containing the file extension.
        """
        if '!' in instruction:
            instruction = instruction.split('!')[0]
        if '#' in instruction:
            instruction= instruction.split('#')[0]
        root, filename = os.path.split(instruction)
        ext = os.path.splitext(filename)[1][1:]
        ext = ext.strip().lower()
        return ext
    
    
    def separateComment(self, instruction):
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
            return True, split, comment_char
        else:
            return False, split, comment_char
        
        
    def _breakLine(self, line):
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
    
    
    def _breakAuto(self, line, filename):
        """Estry file 'AUTO' fix.
        
        Estry files can either be loaded with a filepath like the other files
        or with the 'AUTO' feature. This requires only:
        
        :code:'READ ESTRY FILE AUTO'
        
        and means that we won't have a file path stored.
        
        This function replaces the line with the .tcf file path (and .ecf
        extension) so it can be treated like all of the other files.
        
        Note:
            There is functionality in the TuflowModel class to convert this
            back to 'AUTO' when writing.
         
        Args:
            line(str): line as read from the file.
            filename(str): the file path name part.
        """
        if '==' in line:
            line = line.replace(' == ', ' ')
            
        index = line.upper().find('AUTO')
        command = line[:index-1]
        end = line[index+5:]
        filename = os.path.splitext(filename)[0]
        new_line = ' '.join([command, '==', filename + '.ecf', end])
        return new_line

    
    def _resolveResult(self, entry):
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
        
        This method attempts to work out what's going on with it all and setup
        the root, relative_root and filename accordingly.
        
        TODO:
            Need to account for the case where a string follows the directory
            is given that will be prepended to all output files.
        
        Args:
            entry(TuflowFilePart): containing a RESULT type.
        
        Returns:
            TuflowFilePart - ammended.
        """
        
        RESULT, CHECK, LOG = range(3)
        if entry.command.upper() == 'OUTPUT FOLDER':
            rtype = RESULT
        elif entry.command.upper() == 'WRITE CHECK FILES':
            rtype = CHECK
        else:
            rtype = LOG
             
        is_absolute = os.path.isabs(entry.path_as_read)
        basename = os.path.basename(entry.path_as_read)
        final_char = entry.path_as_read[-1]
        trailing_slash = final_char == '\\' or final_char == '/'
        
        if is_absolute:
            entry.has_own_root = True
            entry.relative_root = ''
            
            # If there's a slash on the end keep path as it is
            if trailing_slash:
                entry.root = entry.path_as_read
            
            # Get directory for CHECK files so we can set a filename prefix later
            # or stick a slash on the end for the others to make it easier to
            # deal with it later
            elif not trailing_slash and rtype == CHECK:
                entry.root = os.path.dirname(entry.path_as_read) + os.sep
            else:
                entry.root = entry.path_as_read + os.sep
        else:
            # This shouldn't ever happen, but in case it does we set it to 
            # '' here so it doesn't catch anyone out later
            if entry.root is None: entry.root = ''

            entry.has_own_root = False
            if trailing_slash:
                entry.relative_root = entry.path_as_read
            elif not trailing_slash and rtype == CHECK:
                entry.relative_root = os.path.dirname(entry.path_as_read)
            else:
                entry.relative_root = entry.path_as_read + os.sep
                
        entry.file_name = ''
        entry.extension = ''
        entry.file_name_is_prefix = False
        
        # A trailing string is a prefix in check files so set that up here
        if rtype == CHECK:
            if not trailing_slash:
                entry.file_name_is_prefix = True
                entry.file_name = os.path.basename(entry.path_as_read)
       
        return entry
    
    
    def _checkProjectionIsFile(self, instruction):
        """Check that the MI PROJECTION line is a file and not a command.
        
        Args:
            instruction: the instruction command after the ==.
            
        Return:
            Bool - True if it's a file and False otherwise.
        """
        if 'COORDSYS' in instruction.upper():
            return False
        else:
            return True
        
            
    class _FileDetails(object):
        """Protected nested class for storing file load details.
        
        This class stores file load state and data so that we don't need to
        keep passing it back and forth through all of the functions.
        
        Contains methods for loading the file and generating some of the
        model file objects as well.
        """
    
        def __init__(self, details, gen_hash):
            """Initialise class state.
            
            Can either be handed the hash values as element 2 & 3 or details,
            or generate them by setting gen_hash to True. This is because the
            first tcf file will need them generated, but none of the later
            ones will.
            """
            self.path = details[0]
            self.root, self.filename = os.path.split(self.path)
            self.extension = os.path.splitext(self.filename)[1][1:]
            if gen_hash:
                self.head_hash = self.generateHash(self.filename + 'HEAD')
                self.parent_hash = None
            else:
                self.head_hash = details[1]
                self.parent_hash = details[2]
            self.relative_root = details[3]


        def getModel(self):
            """Generates a new TuflowModelFile base on current state.
            
            Returns:
                TuflowModelFile - based on extension in class.
            """
            return TuflowModelFile(self.extension, self.head_hash, self.parent_hash) 
            

        def generateModelTuflowFile(self, line_type, global_order):
            """Creates a TuflowFile object from the current state.
            
            Generates the class the self params.
            
            Args:
                line_type(int): one of the TuflowLoader.types value e.g. MODEL
            
            Returns:
                TuflowFile object.
            """
            return tfp.TuflowFile(global_order, self.filename, self.head_hash, 
                        line_type, self.extension, self.root, 
                        self.relative_root, self.extension)
            

        def generateHash(self, salt):
            """Generate an md5sum hashcode from the salt.
             
            Md5 should be good enough for the number of them we will be 
            generating.
             
            Args:
                salt: string to use to generate the hash value.
                 
            Returns:
                Hexadecimal version of the hash value.
            """
            head_hash = hashlib.md5(salt.encode())
            head_hash = head_hash.hexdigest()
            return head_hash
        
        
        def getFile(self):
            """Load the file into the contents list.

            Args:
                file_path (str): path to the required file. 
            
            Returns:
                True if loaded ok, False otherwise.
            """
            logger.debug('loading File: ' + self.path)
            try: 
                self.raw_contents = filetools.getFile(self.path)
            except IOError: 
                logger.error('IOError - Unable to load file')
                return False
                
            if(self.raw_contents == None): 
                logger.error('model file is empty at: ' + self.path)
                return False
                    
            return True


