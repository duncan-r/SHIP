"""

 Summary:
    Contains the HeadDataItem class. Used for storing data types, values,
    formatting and location of data stored in the head_data dict.

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

from ship.datastructures import DATA_TYPES as dt
from ship.utils import utilfunctions as uf



class HeadDataItem(object):
    """Objects stored in the head_data dict in AUnit's.

    Allow for formatting variables and value checks to be encapsulated in one
    place rather than littered around all subclasses of AUnit.
    """

    def __init__(self, initial_value, format_str, line_no, col_no, **kwargs):
        """Constructor.

        A few checks of the validity of the value given will be made against
        the initial_value given.

        **kwargs:
            dtype(int): one of the datatructures.DATA_TYPES.
            default: a default value to apply when none is given.
            allow_blank(bool): whether to allow blank/non-value entries.
            update_callback(func): a function to vall when a value is updated.
                This is not currently used.

        Args:
            initial_value: the initial value to set.
            format_str(str): the format to return the item with. Should be in
                the form '{:>10}'. Use '' for no formatting.
            line_no(int): the line number that the value occurs in the head_data.
                0 indexed.
            col_no(int): the column that the value occurs in - 0 indexed.
        """

        kkeys = kwargs.keys()
        dtype = kwargs.get('dtype', dt.STRING)
        default = kwargs.get('default', None)
        self.allow_blank = kwargs.get('allow_blank', False)
        if dtype == dt.CONSTANT:
            if not 'choices' in kkeys:
                raise AttributeError("Keyword args must contain 'choices=(str1, str2, strN)' when dtype == CONSTANT")
            elif not isinstance(kwargs['choices'], tuple):
                raise ValueError('choices must be a tuple')

        self.dtype = dtype
        self.format_str = format_str
        self.line_no = line_no
        self.col_no = col_no
        self.kwargs = kwargs

        value = self._checkValue(initial_value)
        self._value = value
        self._update_callback = kwargs.get('update_callback', None)


    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        """Property for setting the value.

        Raises:
            ValueError: if value is not the correct type.
        """
        val = self._checkValue(val)
        self._value = val

    def format(self, auto_newline=False):
        """Return the value converted to unicode str and formatted.

        Formatting uses the self.format_str variable.

        A newline char '\n' will be appended to the start of the returned
        string if it's col_no == 0 and auto_newline == True.
        """
        out = ''
        if self.allow_blank and self._value == '':
            if auto_newline and self.col_no == 0:
                return '\n' + out
            else:
                return out

        if self.dtype == dt.FLOAT:
            dps = self.kwargs.get('dps', 1)
            decimal_format = '%0.' + str(dps) + 'f'
            value =  decimal_format % float(self._value)
            out = self.format_str.format(value)
        else:
            out = self.format_str.format(self._value)

        if auto_newline and self.col_no == 0:
            out = '\n' + out

        return self.format_str.format(out)


    def compare(self, compare_val):
        """Check equality of given value against self.value.

        Args:
            compare_val: value to compare with self.value.

        Return:
            bool - true if equal, false if not.

        Raises:
            ValueError: if value is not the correct type.
        """
        if compare_val == self._value:
            return True
        else:
            return False


    def _checkValue(self, value, **kwargs):
        if self.allow_blank and value == '': return value
        dtype = self.kwargs.get('dtype', dt.STRING)
        default = self.kwargs.get('default', None)

        if dtype == dt.STRING:
            if not uf.isString(value):
                if default is not None: return default
                raise ValueError('value %s is not compatible with dtype STRING' % value)
            else:
                return value
        if dtype == dt.INT:
            if not uf.isNumeric(value):
                if default is not None: return default
                raise ValueError('value %s is not compatible with dtype INT' % value)
            else:
                return int(value)
        if dtype == dt.FLOAT:
            if not uf.isNumeric(value):
                if default is not None: return default
                raise ValueError('value %s is not compatible with dtype FLOAT' % value)
            else:
                return float(value)
        if dtype == dt.CONSTANT:
            choices = self.kwargs['choices']
            if not value in choices:
                raise ValueError("value %s is not in CONSTANT 'choices' tuple %s" % (value, choices))
            else:
                return  value




