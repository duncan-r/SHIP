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

import re
import os

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


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
    return type('Enum', (), enums)

    
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
    
    
    

