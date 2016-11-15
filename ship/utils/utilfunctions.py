"""

 Summary:
    Utility Functions that could be helpful in any part of the API.

    All functions that are likely to be called across a number of classes
    and Functions in the API should be grouped here for convenience.

 Author:  
     Duncan Runnacles
     
  Created:  
     01 Apr 2016
 
 Copyright:  
     Duncan Runnacles 2016

 TODO: This module, like a lot of other probably, needs reviewing for how
         'Pythonic' t is. There are a lot of places where generators,
         comprehensions, maps, etc should be used to speed things up and make
         them a bit clearer.
         
         More importantly there are a lot of places using '==' compare that
         should be using 'in' etc. This could cause bugs and must be fixed
         soon.

 Updates:

"""
from __future__ import unicode_literals

import re
import os
import operator

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


# def resolveSeDecorator(se_vals, path):
#     """Decorator function for replacing Scen/Evt placholders.
#     
#     Checks fro scenario and event placeholders in the return value of a 
#     function and replaces them with corresponding values if found.
#     
#     Args:
#         se_vals(dict): standard scenario/event dictionary in the format:  
#             {'scenario': {
#     """
#     def seDecorator(func):
#         def seWrapper(*args, **kwargs):
#             result = func(*args, **kwargs)
# 
#             if '~' in result:
#                 # Check for scenarion stuff
#                 for key, val in self.se_vals['scenario'].items():
#                     temp = '~' + key + '~'
#                     if temp in result:
#                         result = result.replace(temp, val)
#                 # Check for event stuff
#                 for key, val in self.se_vals['event'].items():
#                     temp = '~' + key + '~'
#                     if temp in result:
#                         result = result.replace(temp, val)
#             return result
#         return seWrapper
#     return seDecorator


def formatFloat(value, no_of_dps, ignore_empty_str=True):
    """Format a float as a string to given number of decimal places.
    
    Args:
        value(float): the value to format.
        no_of_dps(int): number of decimal places to format to.
        ignore_empty_str(True): return a stripped blank string if set to True.
    
    Return:
        str - the formatted float.
        
    Raises:
        ValueError - if value param is not type float.
    """
    if ignore_empty_str and not isNumeric(value) and str(value).strip() == '': 
        return str(value).strip()
    if not isNumeric(value): raise ValueError
    decimal_format = '%0.' + str(no_of_dps) + 'f'
    value =  decimal_format % float(value)
    return value
    

def checkFileType(file_path, ext):
    """Checks a file to see that it has the right extension.
    
    Args:
        file_path (str): The file path to check.
        ext (List): list containing the extension types to match the file 
            against.   
        
    Returns:
        True if the extension matches the ext variable given or False if not.
    """
    file_ext = os.path.splitext(file_path)[1]
    logger.info('File ext = ' + file_ext)
    for e in ext:
        if e == file_ext:
            return True
    else:
        return False


def isNumeric(s): 
    """Tests if string is a number or not.
    
    Simply tries to convert it and catches the error if launched.
    
    Args:
        s (str): string to test number compatibility.
    
    Returns:
        Bool - True if number. False if not.
    """
    try:
        float(s)
        return True
    except ValueError:
        return False


def isString(value):
    """Tests a given value to see if it is an instance of basestring or not.

    It will return True for any value that contains unicode characters.
    
    Args:
        value: the variable to test.
    
    Returns:
        Bool - True if value is a unicode str (basestring type) 
    """
    if not isinstance(value, basestring):
        return False
    
    return True


def isList(value):
    """Test a given value to see if it is a list or not.
    
    Args:
        value: the variable to test for list type.
    
    Returns:
        True if value is of type list; False otherwise.
    """
    if not isinstance(value, list):
        return False
    
    return True
    
            
def arrayToString(self, str_array):
    """Convert a list to a String

    Creates one string by adding each part of the array to one string using 
    ', '.join()
    
    Args:
        str_array (List): to convert into single string.
    
    Returns:
        str - representaion of the array joined together.
    
    Raises:
        ValueError: if not contents of list are instances of basestring.
    """
    if not isinstance(str_array[0], basestring):
        raise ValueError ('Array values are not strings')
    
    out_string = ''
    out_string = ', '.join(str_array)        

    return out_string


def findSubstringInList(substr, the_list):
    """Returns a list containing the indices that a substring was found at.
    
    Uses a generator to quickly find all indices that str appears in.
    
    Args:
        substr (str): the sub string to search for.
        the_list (List): a list containing the strings to search.
    
    Returns:
        tuple - containing:
            * a list with the indices that the substring was found in 
                (this list can be empty if no matches were found).
            * an integer containing the number of elements it was found in.
    """
    indices = [i for i, s in enumerate(the_list) if substr in s] 
    return indices, len(indices)
    

def findMax(val1, val2):
    """Returns tuple containing min, max of two values
    
    Args:
        val1: first integer or float.
        val2: second integer or float.
    
    Returns:
        tuple - containing: 
            * lower value
            * higher value 
            * False if not same or True if the same.
    """
    if val1 == val2:
        return val1, val2, True
    elif val1 > val2:
        return val2, val1, False
    else:
        return val1, val2, False


def fileExtensionWithoutPeriod(filepath, name_only=False):
    """Extracts the extension without '.' from filepath.
    
    The extension will always be converted to lower case before returning.
    
    Args:
        filepath (str): A full filepath if name_only=False. Otherwise a file
            name with extension if name_only=True.
        name_only (bool): True if filepath is only filename.extension.
    """
    if name_only:
        file, ext = os.path.splitext(filepath)
    else:
        path, filename = os.path.split(filepath)
        file, ext = os.path.splitext(filename)

    ext = ext[1:]
    return ext.lower()


def findWholeWord(w):
    """Find a whole word amoungst a string."""
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search


def convertRunOptionsToSEDict(options):
    """Converts tuflow command line options to scenario/event dict.
    
    Tuflow uses command line option (e.g. -s1 blah -e1 blah) to set scenario
    values which can either be provided on the command line or through the
    FMP run form. The TuflowLoader can use these arguments but requires a 
    slightly different setup.
    
    This function converts the command line string into the scenarion and
    event dictionary expected by the TuflowLoader.
    
    Args:
        options(str): command line options.
        
    Return:
        dict - {'scenario': {'s1': blah}, 'event': {'e1': blah}}
    
    Raises:
        AttributeError: if both -s and -s1 or -e and -e1 occurr in the options
            string. -x and -x1 are treated as the same variable by tuflow and
            one of the values would be ignored.
    """
    
    if ' -s ' in options and ' -s1 ' in options:
        raise AttributeError
    if ' -e ' in options and ' -e2 ' in options:
        raise AttributeError
    
    outvals = {'scenario': {}, 'event': {}}
    vals = options.split(" ")
    for i in range(len(vals)):
        if vals[i].startswith('-s'):
            outvals['scenario'][vals[i][1:]] = vals[i+1]
        elif vals[i].startswith('-e'):
            outvals['event'][vals[i][1:]] = vals[i+1]
    
    return outvals


def getSEResolvedFilename(filename, se_vals):
    """Replace a tuflow placeholder filename with the scenario/event values.
        
    Replaces all of the placholder values (e.g. ~s1~_~e1~) in a tuflow 
    filename with the corresponding values provided in the run options string.
    If the run options flags are not found in the filename their values will
    be appended to the end of the string.
    
    The setup of the returned filename is always the same:  
        - First replace all placeholders with corresponding flag values.
        - s1 == s and e1 == e.
        - Append additional e values to end with '_' before first and '+' before others.
        - Append additional s values to end with '_' before first and '+' before others.
    
    Args:
        filename(str): the filename to update.
        se_vals(str): the run options string containing the 's' and 
            'e' flags and their corresponding values. 
    
    Return:
        str - the updated filename.
    """
    if not 'scenario' in se_vals.keys(): se_vals['scenario'] = {}
    if not 'event' in se_vals.keys(): se_vals['event'] = {}
    
    # Format the key value pairs into a list and combine the scenario and
    # event list together and sort them into e, e1, e2, s, s1, s2 order.
    scen_keys = ['-' + a for a in se_vals['scenario'].keys()]
    scen_vals = se_vals['scenario'].values()
    event_keys = ['-' + a for a in se_vals['event'].keys()]
    event_vals = se_vals['event'].values()
    scen = [list(a) for a in zip(scen_keys, scen_vals)]
    event = [list(a) for a in zip(event_keys, event_vals)]
    se_vals = scen + event
    vals = sorted(se_vals, key=operator.itemgetter(0))
        
    # Build a new filename by replacing or adding the flag values
    outname = filename
    in_e = False
    for v in vals:
        placeholder = ''.join(['~', v[0][1:], '~'])
        
        if placeholder in filename:
            outname = outname.replace(placeholder, v[1])
        elif v[0] == '-e1' and '~e~' in filename and not '-e' in se_vals:
            outname = outname.replace('~e~', v[1])
        elif v[0] == '-s1' and '~s~' in filename and not '-s' in se_vals:
            outname = outname.replace('~s~', v[1])
        #DEBUG - CHECK THIS IS TRUE!
        elif v[0] == '-e' and '~e1~' in filename:
            outname = outname.replace('~e1~', v[1])
        elif v[0] == '-s' and '~s1~' in filename:
            outname = outname.replace('~s1~', v[1])
        
        else:
            if v[0].startswith('-e'):
                if not in_e: 
                    prefix = '_'
                else:
                    prefix = '+'
                in_e = True
            elif v[0].startswith('-s'):
                if in_e: 
                    prefix = '_'
                else:
                    prefix = '+'
                in_e = False
            outname += prefix + v[1]
        
    return outname
    

def enum(*sequential, **named):
    """Creates a new enum using the values handed to it.
    
    Taken from Alec Thomas on StackOverflow:
    http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python 
    
    Examples:
        Can be created and accessed using:
        
        >>> Numbers = enum('ZERO', 'ONE', 'TWO')
        >>> Numbers.ZERO
        0
        >>> Numbers.ONE
        1
        
        Or reverse the process o get the name from the value:
        
        >>> Numbers.reverse_mapping['three']
        'THREE'
    """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type(str('Enum'), (), enums)

    
class FileQueue(object):
    """Queueing class for storing data to go into the database
    """
    
    def __init__(self):
        self.items = []

    def isEmpty(self):
        """Returns True if list is empty
        """
        return self.items == []

    def enqueue(self, item):
        """Add an item to the queue
        """
        self.items.insert(0,item)

    def dequeue(self):
        """Pop an item from the front of the queue.
        """
        return self.items.pop()

    def size(self):
        """Get the size of the queue
        """
        return len(self.items)



class LoadStack(object):
    """Stack class for loading logic."""
    
    def __init__(self, max_size=-1):
        self.items = []
        self.max_size = max_size
        
    
    def isEmpty(self):
        """Return True if stack is empty."""
        return self.items == []
    
    
    def add(self, item):
        """Add an item to the stack.
        
        Args:
            item: the item to add to the stack.
            
        Raises:
            IndexError: if max_size has been set and adding another item would
                make the stack bigger than max size.
        """
        if not self.max_size == -1:
            if len(self.items) + 1 > self.max_size:
                raise IndexError
        self.items.append(item)
        
    
    def pop(self):
        """Get an item From the stack.
        
        Return:
            item from the top of the stack.
            
        Raises:
            IndexError: if the stack is empty.
        """
        if len(self.items) == 0:
            raise IndexError
        return self.items.pop()
        
    
    def peek(self):
        """See what the next item on the stack is, but don't remove it.
        
        Return:
            item from the top of the stack.
            
        Raises:
            IndexError: if the stack is empty.
        """
        if len(self.items) == 0:
            raise IndexError
        return self.items[-1]
    
    
    def size(self):
        """Return the number of items in the stack."""
        return len(self.items)
    
    
    

