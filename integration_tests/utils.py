import traceback
import sys

global assertionErrors


def softAssertion(var, value, testEqual=True):
    try:
        if testEqual:
            assert(var == value)
        else:
            assert(var != value)
    except AssertionError as err:
        global assertionErrors
        assertionErrors += 1
        traceback.print_stack()
        
def softAssertionIn(var, value, testIn=True):
    try:
        if testIn:
            assert(var in value)
        else:
            assert(var not in value)
    except AssertionError as err:
        global assertionErrors
        assertionErrors += 1
        traceback.print_stack()
        