"""

 Summary:
    Contains the RiverUnit class.
    This holds all of the data read in from the river units in the dat file.
    Can be called to load in the data and read and update the contents 
    held in the object.

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

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""

from ship.data_structures import DATA_TYPES as dt
from ship.utils import utilfunctions as uf


class HeadData(object):
    
    
    __slots__ = () # no __dict__ - that would be redundant
    
    def __init__(self, name, name_ds=None):
        self.name = name
        self.name_ds = name_ds
        self.data = {}
    
    @classmethod
    def setup(cls, name, data_items, name_ds=None):
        d = HeadData(name, name_ds)
        for d in data_items:
            hd.add(d)
        return d
        
    def add(self, data_item):
        self.data[data_item.key] = data_item   

    def get(self, key):
        return self.data[key]
    

    '''
        dict interface methods
    '''
#     @staticmethod # because this doesn't make sense as a global function.
#     def _process_args(mapping=(), **kwargs):
#         if hasattr(mapping, items):
#             mapping = getattr(mapping, items)()
#         return ((k, v) for k, v in chain(mapping, getattr(kwargs, items)()))
# 
#     def __init__(self, mapping=(), **kwargs):
#         super(HeadData, self).__init__(self._process_args(mapping, **kwargs))
# 
#     def __getitem__(self, k):
#         return super(HeadData, self).__getitem__(k).value
# 
#     def __setitem__(self, k, v):
#         self.
#         return super(HeadData, self).__setitem__(k.value, v)
# 
#     def __delitem__(self, k):
#         return super(HeadData, self).__delitem__(k)
# 
#     def get(self, k, default=None):
#         return super(HeadData, self).get(k.value, default)
# 
#     def setdefault(self, k, default=None):
#         return super(HeadData, self).setdefault(k, default)
# 
#     def pop(self, k):
#         return super(HeadData, self).pop(k)
# 
#     def update(self, mapping=(), **kwargs):
#         super(HeadData, self).update(self._process_args(mapping, **kwargs))
# 
#     def __contains__(self, k):
#         return super(HeadData, self).__contains__(k)
# 
#     @classmethod
#     def fromkeys(cls, keys):
#         return super(HeadData, cls).fromkeys(k for k in keys)
    

class HeadDataItem(object):
    
    def __init__(self, key, value, format_str, line_no, col_no, dtype=dt.STRING, 
                 choices=()):
        if not HeadDataItem.checkValue(value, dtype): 
            raise ValueError('value %s is not compatible with given dtype' % value)
        self.key = key
        self.value = value
        self.dtype = dtype
        self.format_str = format_str
        self.dtype = dtype
        self.choices = choices
        self.width = width
        self.line_no = line_no
        self.col_no = col_no
    
    @staticmethod
    def checkValue(self, dtype, value): 
        if dtype == dt.STRING: return uf.isString(value)
        if dtype == dt.INT: return uf.isNumeric(value)
        if dtype == dt.FLOAT: return uf.isNumeric(value)
        if dtype == dt.CONSTANT: return isinstance(value, tuple)

        
        
        
        