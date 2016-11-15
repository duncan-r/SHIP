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

import os
import operator

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
        


    def checkPathsExist(self):
        """Test that all of the filepaths in the TuflowModel exist."""
        failed = []
        for c in self.control_files:
            failed.extend(c.checkPathsExist()) 
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
        for c in self.control_files:
            c.updateRoot(root)
            
    @property
    def root(self):
        return self._root
    
    @root.setter
    def root(self, value):
        self._root = value
        self.updateRoot(value)


class UserVariables(object):
    """
    """
    
    def __init__(self):
        self.variable = {}
        self.scenario = {}
        self.event = {}
        self.has_cmd_args = False
    
    def add(self, filepart, vtype=None):
        if isinstance(filepart, TuflowUserVariable):
            self.variable[filepart.variable_name] = filepart
        elif isinstance(filepart, TuflowModelVariable):
            if filepart._variable_type == 'scenario':
                self.scenario[filepart._variable_name] = filepart
            else:
                self.event[filepart._variable_name] = filepart
        else:
            raise TypeError('filepart must be of type TuflowUserVariable or TuflowModelVariable')
        
    def scenarioEventValuesToDict(self):
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
            del self.scenario[key]
        if key in self.event.keys():
            del self.event[key]
        if key in self.variable.keys():
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


class TuflowTypes(object):
    """Contains key words from Tuflow files for lookup.
    
    This acts as a lookup table for the TuflowLoader class more than anything
    else. It is kept here as that seems to be most sensible.
    
    Contains methods for identifying whether a command given to it is known
    to the library and what type it is. i.e. what category it falls into.
    """
    
    def __init__(self):
        """Initialise the categories and known keywords"""
        self.ambiguous = {
            'WRITE CHECK FILES': ['WRITE CHECK FILES INCLUDE', fpt.VARIABLE],
            'WRITE CHECK FILES INCLUDE': ['WRITE CHECK FILES', fpt.RESULT],
            'DEFINE EVENT': ['DEFINE OUTPUT ZONE', fpt.SECTION_LOGIC],
            'DEFINE OUTPUT ZONE': ['DEFINE EVENT', fpt.EVENT_LOGIC],
        }
        self.ambiguous_keys = self.ambiguous.keys()

        self.types = {}
        self.types[fpt.MODEL] = ['GEOMETRY CONTROL FILE', 'BC CONTROL FILE',
                                'READ FILE', 'ESTRY CONTROL FILE', 
                                'EVENT FILE']
        self.types[fpt.RESULT] = ['OUTPUT FOLDER', 'WRITE CHECK FILES',
                                 'LOG FOLDER']
        self.types[fpt.GIS] = ['READ MI', 'READ GIS', 'READ GRID',
                              'SHP PROJECTION', 'MI PROJECTION']
        self.types[fpt.DATA] =  ['READ MATERIALS FILE', 
                                'BC DATABASE']
        self.types[fpt.VARIABLE] =  ['START TIME', 'END TIME', 'TIMESTEP',
                                    'SET IWL', 'MAP OUTPUT INTERVAL', 
                                    'MAP OUTPUT DATA TYPES', 'CELL WET/DRY DEPTH',
                                    'CELL SIDE WET/DRY DEPTH', 'SET IWL',
                                    'TIME SERIES OUTPUT INTERVAL',
                                    'SCREEN/LOG DISPLAY INTERVAL', 'CSV TIME',
                                    'START OUTPUT', 'OUTPUT INTERVAL',
                                    'STRUCTURE LOSSES', 'WLL APPROACH',
                                    'WLL ADJUST XS WIDTH', 'WLL ADDITIONAL POINTS',
                                    'DEPTH LIMIT FACTOR', 'CELL SIZE', 'SET CODE',
                                    'GRID SIZE (X,Y)', 'SET ZPTS', 'SET MAT',
                                    'MASS BALANCE OUTPUT', 'GIS FORMAT',
                                    'MAP OUTPUT FORMATS', 'END MAT OUTPUT',
                                    'ASC START MAP OUTPUT', 'ASC END MAP OUTPUT',
                                    'XMDF MAP OUTPUT DATA TYPES', 'WRITE PO ONLINE', 
                                    'ASC MAP OUTPUT DATA TYPES',
                                    'WRITE CHECK FILES INCLUDE',
                                    'STORE MAXIMUMS AND MINIMUMS']
        self.types[fpt.IF_LOGIC] = ['IF SCENARIO', 'ELSE IF SCENARIO', 'IF EVENT', 
                                    'ELSE IF EVENT', 'END IF', 'ELSE']
        self.types[fpt.EVENT_LOGIC] = ['DEFINE EVENT', 'END DEFINE']
        self.types[fpt.SECTION_LOGIC] = ['DEFINE OUTPUT ZONE', 'END DEFINE']
        self.types[fpt.USER_VARIABLE] = ['SET VARIABLE']
        self.types[fpt.EVENT_VARIABLE] = ['BC EVENT TEXT', 'BC EVENT NAME', 
                                           'BC EVENT SOURCE',]
        self.types[fpt.MODEL_VARIABLE] = ['MODEL SCENARIOS', 'MODEL EVENTS',]
        
        
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
            return self.ambiguous[found][1]

        