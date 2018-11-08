"""

 Summary:
     Container and main interface for accessing the Tuflow model and a class
     for containing the main tuflow model files (Tcf, Tgc, etc). 
     
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

from __future__ import unicode_literals

from itertools import chain

from ship.tuflow.tuflowfilepart import TuflowFile, TuflowKeyValue, TuflowUserVariable, TuflowModelVariable
from ship.tuflow import FILEPART_TYPES as fpt
from ship.utils import utilfunctions as uf


import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class TuflowModel(object):
    """Container for the entire loaded tuflow model.
    """

    def __init__(self, root):
        """Initialise constants and dictionaries.
        """

        self.control_files = {}
        """Tuflow Control File objects.
        
        All types of Tuflow Control file are stored here under the type header.
        Types are: TCF, TGC, TBC, ECF, TEF.  
        TCF is slightly different to the others as it contains an additional
        member variable 'main_file_hash' to identify the main tcf file that
        was called to load the model.
        """

        self._root = ''
        """The current directory path used to reach the run files in the model"""

        self.missing_model_files = []
        """Contains any tcf, tgs, etc files that could not be loaded."""

        self.bc_event = {}
        """Contains the currently acitve BC Event variables."""

        self.user_variables = None
        """Class containing the scenario/event/variable keys and values."""

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, value):
        self._root = value
        self.updateRoot(value)

    def checkPathsExist(self):
        """Test that all of the filepaths in the TuflowModel exist."""
        failed = []
        for file_type, file in self.control_files.items():
            failed.extend(file.checkPathsExist())
        return failed

    def updateRoot(self, root):
        """Update the root variable in all TuflowFile's in the model.

        The root variable (TuflowModel.root) is the directory that the main
        .tcf file is in. This is used to define the location of all other files
        which are usually referenced relative to each other.

        Note:
            This method will be called automatically when setting the 
                TuflowModel.root variable.

        Args:
            root(str): the new root to set.
        """
        for c in self.control_files.values():
            c.updateRoot(root)

    def customPartSearch(self, control_callback, tuflow_callback=None,
                         include_unknown=False):
        """Return TuflowPart's based on the return value of the callbacks.

        control_callback will be used as an argument in each of 
        self.control_files' customPartSearch() methods. The tuflow_callback
        will be called on the combined generators returned from that method.

        See Also:
            ControlFile.customPartSearch

        Continuing the example in the ControlFile.customPartSearch method. This
        time the additinal tuflow_callback function is defined as well.

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

            # Here we define a function to run after the generators are returned
            # from callback_func. In the funcion above the return type is a 
            # tuple, so we accept that as the arg in this function, but it will
            # be whatever you return from callback_func above.
            # This function checks to see if there are any duplicate filename's.
            # Note that it must return the same tuple as the other callback.
            # i.e. keep-status, result
            def tuflow_callback(part_tuple):
                found = []
                if part_tuple[0] in found:
                    return False, None
                else:
                    return True, part_tuple[0] 

            # Both callback's given this time
            results = tuflow.customPartSearch(callback, 
                                              tuflow_callback=tuflowCallback)
            # You can now iteratre the results
            for r in results:
                print (str(r))

        Args:
            callback_func(func): a function to run for each TuflowPart in 
                this ControlFile's PartHolder.
            include_unknown=False(bool): If False any UnknownPart's will be
                ignored. If set to True it is the resonsibility of the 
                callback_func to check for this and deal with it.

        Return:
            generator - containing the results of the search.
        """
        gens = []
        for c in self.control_files.values():
            gens.append(
                c.customPartSearch(control_callback, include_unknown)
            )
        all_gens = chain(gens[0:-1])
        for a in all_gens:
            for val in a:
                if tuflow_callback:
                    take, value = tuflow_callback(val)
                    if take:
                        yield[value]
                else:
                    yield [val]

    def removeTcfModelFile(self, model_file):
        """Remove an existing ModelFile from 'TCF' and update ControlFile.

        Note:
            You can call this function directly if you want to, but it is also
            hooked into a callback in the TCF ControlFile. This means that when
            you use the standard ControlFile add/remove/replaceControlFile()
            methods these will be called automatically.

        Args:
            model_files(ModelFile): the ModelFile being removed.
        """
        if not model_file in self.control_files[model_file.model_type].control_files:
            raise AttributeError("model_file doesn't exists in %s control_files" % model_file.model_type)

        self.control_files[model_file.model_type].removeControlFile(model_file)
        self.control_files['TCF'].parts.remove(model_file)

    def replaceTcfModelFile(self, model_file, control_file, replace_file):
        """Replace an existing ModelFile in 'TCF' and update ControlFile.

        Note:
            You can call this function directly if you want to, but it is also
            hooked into a callback in the TCF ControlFile. This means that when
            you use the standard ControlFile add/remove/replaceControlFile()
            methods these will be called automatically.

        Args:
            model_file(ModelFile): the replacement TuflowPart.
            control_file(ControlFile): containing the contents to replace the
                existing ControlFile.
            replace_file(ModelFile): the TuflowPart to be replaced.
        """
        if model_file in self.control_files[model_file.model_type].control_files:
            raise AttributeError('model_file already exists in this ControlFile')

        self.control_files[replace_file.model_type].replaceControlFile(
            model_file, control_file, replace_file)
        self.control_files['TCF'].parts.replace(model_file, replace_file)

    def addTcfModelFile(self, model_file, control_file, **kwargs):
        """Add a new ModelFile instance to a TCF type ControlFile.

        Note:
            You can call this function directly if you want to, but it is also
            hooked into a callback in the TCF ControlFile. This means that when
            you use the standard ControlFile add/remove/replaceControlFile()
            methods these will be called automatically.

        **kwargs:
            after(TuflowPart): the part to add the new ModelFile after.
            before(TuflowPart): the part to add the new ModelFile before.

        Either after or before kwargs must be given. If both are provided after
        will take precedence.

         Args:
            model_file(ModelFile): the replacement ModelFile TuflowPart.
            control_file(ControlFile): containing the contents to replace the
                existing ControlFile.
        """
        if not 'after' in kwargs.keys() and not 'before' in kwargs.keys():
            raise AttributeError("Either 'before' or 'after' TuflowPart kwarg must be given")

        if model_file in self.control_files[model_file.model_type].control_files:
            raise AttributeError('model_file already exists in this ControlFile')

        self.control_files[model_file.model_type].addControlFile(
            model_file, control_file, **kwargs)
        self.control_files['TCF'].parts.add(model_file, **kwargs)


# class TuflowUtils(object):
#     """Utility functions for dealing with TuflowModel outputs."""
#
#     def __init__(self):
#         pass
#
#     @staticmethod
#     def resultsByParent(results):
#         """
#         """


class UserVariables(object):
    """Container for all user defined variables.

    Includes variable set in the control files with 'Set somevar ==' and the
    scenario and event variables.

    Note:
        Only the currently active scenario and event variables will be stored
        in this class.
    """

    def __init__(self):
        self.variable = {}
        self.scenario = {}
        self.event = {}
        self._names = []
        self.has_cmd_args = False

    def add(self, filepart, vtype=None):
        """Add a new variables to the class.

        Args:
            filepart(TuflowModelVariables or TuflowUserVariable):  

        Raises:
            TypeError - if filepart is not a TuflowModelVariable or TuflowUserVariable.
            ValueError - if filepart already exists.
        """
        if filepart._variable_name in self._names:
            raise ValueError('variable already exists with that name - use replace instead')

        if isinstance(filepart, TuflowUserVariable):
            self.variable[filepart.variable_name] = filepart
            self._names.append(filepart.variable_name)

        elif isinstance(filepart, TuflowModelVariable):
            if filepart._variable_type == 'scenario':
                if filepart._variable_name == 's1' or filepart._variable_name == 's':
                    if 's' in self._names or 's1' in self._names:
                        raise ValueError("variable already exists with that " +
                                         "name - use replace instead\n" +
                                         "note 's' and 's1' are treated the same.")
                self.scenario[filepart._variable_name] = filepart
                self.variable[filepart._variable_name] = filepart
                self._names.append(filepart.variable_name)

            else:
                if filepart._variable_name == 'e1' or filepart._variable_name == 'e':
                    if 'e' in self._names or 'e1' in self._names:
                        raise ValueError("variable already exists with that " +
                                         "name - use replace instead\n" +
                                         "note 'e' and 'e1' are treated the same.")
                self.event[filepart._variable_name] = filepart
                self.variable[filepart._variable_name] = filepart
                self._names.append(filepart.variable_name)
        else:
            raise TypeError('filepart must be of type TuflowUserVariable or TuflowModelVariable')

    def replace(self, filepart):
        """Replace an existing variable.

        Args:
            filepart(TuflowModelVariables or TuflowUserVariable):  

        Raises:
            TypeError - if filepart is not a TuflowModelVariable or TuflowUserVariable.
            ValueError - if filepart doesn't already exist.
        """

        # Make sure it actually already exists.
        # s & s1 and e & e1 are treated as the same name - same as tuflow
        temp_name = filepart._variable_name
        if temp_name == 's' or temp_name == 's1':
            if not 's' in self._names and not 's1' in self._names:
                raise ValueError("filepart doesn't seem to exist in UserVariables.")
        elif temp_name == 'e' or temp_name == 'e1':
            if not 'e' in self._names and not 'e1' in self._names:
                raise ValueError("filepart doesn't seem to exist in UserVariables.")
        elif not filepart._variable_name in self._names:
            raise ValueError("filepart doesn't seem to exist in UserVariables.")

        # Delete the old one and call add() with the new one
        if temp_name == 's' or temp_name == 's1':
            if 's' in self.scenario.keys():
                del self.scenario['s']
                del self.variable['e']
            if 's1' in self.scenario.keys():
                del self.scenario['s1']
                del self.variable['e1']
                self.add(filepart, 'scenario')
        if temp_name == 'e' or temp_name == 'e1':
            if 'e' in self.scenario.keys():
                del self.event['e']
                del self.variable['e']
            if 'e1' in self.scenario.keys():
                del self.event['e1']
                del self.variable['e1']
                self.add(filepart, 'event')
        else:
            del self.variable[temp_name]
            self.add(filepart)

    def variablesToDict(self):
        """Get the values of the variables.

        Note that, like tuflow, scenario and event values will be includes in
        the variables dict returned.

            {'name1': var1, 'name2': var2, 'nameN': name2}

        Return:
            dict - with variables names as key and values as values.
        """
        out = {}
        for vkey, vval in self.variable.items():
            out[vkey] = vval.variable
        return out

    def seValsToDict(self):
        """Get the values of the scenario and event variables.

        Returns the currently active scenario and event values only - not the
        placeholder keys - in a dictionary in the format::  
            {'scenario': [val1, val2, valN], 'event': [val1, val2, valN]}

        Return:
            dict - of scenario and event values.
        """
        scenario = [s.variable for s in self.scenario.values()]
        event = [e.variable for e in self.event.values()]
        return {'scenario': scenario, 'event': event}

    def remove(self, key):
        """Remove the variable stored at the given key.

        Args:
            key(str): key for either the scenario, event, or variables dict.
        """
        if key in self.scenario.keys():
            self._names.remove(self.scenario[key]._variable_name)
            del self.scenario[key]
        if key in self.event.keys():
            self._names.remove(self.scenario[key]._variable_name)
            del self.event[key]
        if key in self.variable.keys():
            self._names.remove(self.scenario[key]._variable_name)
            del self.variable[key]

    def get(self, key, vtype=None):
        """Return the TuflowPart at the given key.

        Args:
            key(str): the key associated with the required TuflowPart.
            vtype=None(str): the type of part to return. If None it will return
                a 'variable' type. Other options are 'scenario' and 'event'.

        Return:
            TuflowPart - TuflowModelVariable or TuflowUserVariable type.
        """
        if vtype == 'scenario':
            if not key in self.scenario.keys():
                raise KeyError('key %s is not in scenario keys' % key)
            return self.scenario[key]
        elif vtype == 'event':
            if not key in self.event.keys():
                raise KeyError('key %s is not in event keys' % key)
            return self.event[key]
        else:
            if not key in self.variable.keys():
                raise KeyError('key %s is not in variable keys' % key)
            return self.variable[key]


class TuflowFilepartTypes(object):
    """Contains key words from Tuflow files for lookup.

    This acts as a lookup table for the TuflowLoader class more than anything
    else. It is kept here as that seems to be most sensible.

    Contains methods for identifying whether a command given to it is known
    to the library and what type it is. i.e. what UNIT_CATEGORY it falls into.
    """

    def __init__(self):
        """Initialise the categories and known keywords"""
        self.ambiguous = {
            'WRITE CHECK FILES': [
                ['WRITE CHECK FILES INCLUDE', fpt.VARIABLE],
                ['WRITE CHECK FILES EXCLUDE', fpt.VARIABLE]
            ],
#             'WRITE CHECK FILES INCLUDE': ['WRITE CHECK FILES', fpt.RESULT],
#             'WRITE CHECK FILES EXCLUDE': ['WRITE CHECK FILES', fpt.RESULT],
            'DEFINE EVENT': [['DEFINE OUTPUT ZONE', fpt.SECTION_LOGIC]],
            'DEFINE OUTPUT ZONE': [['DEFINE EVENT', fpt.EVENT_LOGIC]],
#             'START 1D DOMAIN': ['START 2D DOMAIN', fpt.SECTION_LOGIC],
#             'START 2D DOMAIN': ['START 1D DOMAIN', fpt.SECTION_LOGIC],
        }
        self.ambiguous_keys = self.ambiguous.keys()

        self.types = {}
        self.types[fpt.MODEL] = [   
            'GEOMETRY CONTROL FILE', 'BC CONTROL FILE',
            'READ GEOMETRY CONTROL FILE', 'READ BC CONTROL FILE',
            'READ FILE', 'ESTRY CONTROL FILE',
            'EVENT FILE'
        ]
        self.types[fpt.RESULT] = [
            'OUTPUT FOLDER', 'WRITE CHECK FILES', 'LOG FOLDER'
        ]
        self.types[fpt.GIS] = [
            'READ MI', 'READ GIS', 'READ GRID', 'SHP PROJECTION', 
            'MI PROJECTION'
        ]
        self.types[fpt.DATA] = ['READ MATERIALS FILE', 'BC DATABASE']
        self.types[fpt.VARIABLE] = [
            'START TIME', 'END TIME', 'TIMESTEP', 'SET IWL', 
            'MAP OUTPUT INTERVAL', 'MAP OUTPUT DATA TYPES', 'CELL WET/DRY DEPTH',
            'CELL SIDE WET/DRY DEPTH', 'SET IWL', 'TIME SERIES OUTPUT INTERVAL',
            'SCREEN/LOG DISPLAY INTERVAL', 'CSV TIME', 'START OUTPUT', 
            'OUTPUT INTERVAL', 'STRUCTURE LOSSES', 'WLL APPROACH',
            'WLL ADJUST XS WIDTH', 'WLL ADDITIONAL POINTS',
            'DEPTH LIMIT FACTOR', 'CELL SIZE', 'SET CODE', 'GRID SIZE (X,Y)', 
            'SET ZPTS', 'SET MAT', 'MASS BALANCE OUTPUT', 'GIS FORMAT',
            'MAP OUTPUT FORMATS', 'END MAT OUTPUT', 'ASC START MAP OUTPUT', 
            'ASC END MAP OUTPUT', 'XMDF MAP OUTPUT DATA TYPES', 
            'WRITE PO ONLINE', 'ASC MAP OUTPUT DATA TYPES',
            'WRITE CHECK FILES INCLUDE', 'WRITE CHECK FILES EXCLUDE',
            'STORE MAXIMUMS AND MINIMUMS'
        ]
        self.types[fpt.IF_LOGIC] = [
            'IF SCENARIO', 'ELSE IF SCENARIO', 'IF EVENT',
            'ELSE IF EVENT', 'END IF', 'ELSE'
        ]
        self.types[fpt.EVENT_LOGIC] = ['DEFINE EVENT', 'END DEFINE']
        self.types[fpt.SECTION_LOGIC] = ['DEFINE OUTPUT ZONE', 'END DEFINE']
        self.types[fpt.DOMAIN_LOGIC] = [
           'START 1D DOMAIN', 'END 1D DOMAIN', 'START 2D DOMAIN', 
           'END 2D DOMAIN'
        ]
        self.types[fpt.USER_VARIABLE] = ['SET VARIABLE']
        self.types[fpt.EVENT_VARIABLE] = [
            'BC EVENT TEXT', 'BC EVENT NAME',
            'BC EVENT SOURCE', 
        ]
        self.types[fpt.MODEL_VARIABLE] = ['MODEL SCENARIOS', 'MODEL EVENTS', ]

    def find(self, find_val, file_type='*'):
        """Checks if the given value is known or not.

        The word to look for doesn't have to be an exact match to the given
        value, it only has to start with it. This means that we don't need to
        know whether it is a 'command == something' or just 'command something'
        (like: 'Estry Control File Auto') at this point.

        This helps to avoid unnecessary repitition. i.e. many files are like:
        'READ GIS' + another word. All of them are GIS type files so they all
        get dealt with in the same way.

        In some edge cases there are command that start the same. These are
        dealt with by secondary check to see if the next character is '=' or
        not.

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
            for key, part_type in self.types.items():
                found = [i for i in part_type if find_val.startswith(i)]
                if found:
                    retval = key
                    if found[0] in self.ambiguous_keys:
                        retval = self._checkAmbiguity(found[0], find_val, key)
                    return True, retval
            return (False, None)
        else:
            found = [i for i in self.types[file_type] if find_val.startswith(i)]
            if found:
                return True, file_type
            return (False, None)

    def _checkAmbiguity(self, found, find_val, key):
        """Resolves any ambiguity in the keys."""
        f = find_val.replace(' ', '')
        f2 = found.replace(' ', '') + '='
        if f.startswith(f2):
            return key
        else:
            alternatives = self.ambiguous[found]
            for i, a in enumerate(alternatives):
                if find_val.startswith(a[0]):
                    return self.ambiguous[found][i][1]
            return key

