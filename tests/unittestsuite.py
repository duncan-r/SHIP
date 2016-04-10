"""

 Summary:
    Intro point for all the tests been run on the library.
    Every time that updates are made or new parts are added to the library
    these tests should be run to make sure that they have not caused any
    problems in the rest of the modules.

    If new modules are added to the library they should have a test class
    created and placed in the tests.maintests package with tests for
    all of the functions within. The new test module should then be added to
    the testsuite in this module.
    If any data is needed for running the tests it should be kept in the
    /tests/testinputdata/ folder.

 Author:  
     Duncan Runnacles

  Created:  
     01 Apr 2016

 Copyright:  
     Duncan Runnacles 2016

 TODO:

 Updates:

"""

import unittest

if __name__ == '__main__':

    # use the default shared TestLoader instance
    test_loader = unittest.defaultTestLoader

    # use the basic test runner that outputs to sys.stderr
    test_runner = unittest.TextTestRunner()

    # automatically discover all tests in the current dir of the form test*.py
    test_suite = test_loader.discover('.')

    # run the test suite
    test_runner.run(test_suite)
    
    
