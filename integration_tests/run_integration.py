"""

 Summary:
     This is the main class for the integration tests.
     
     It calls a suite of tests that work on an actual loaded TuflowModel to
     check that it functions properly in the 'real world'.
     
     Note that one of the tests will attempt to write out the model to a folder
     called 'test_output' in the integration_tests directory. This folder is
     added to the .gitignore file. If your python path is different in may go
     elsewhere as it uses the getcwd() function...so keep an eye on it!

 Author:  
     Duncan Runnacles

  Created:  
     01 Apr 2016

 Copyright:  
     Duncan Runnacles 2016

 TODO:

 Updates:

"""

from integration_tests import test_tuflowload as tuflowload
from integration_tests import test_tuflowupdate as tuflowupdate
from integration_tests import test_updatetcfmodelfile as tcfmodelfile
from integration_tests import test_datload as datload
from integration_tests.test_tuflowupdate import TestError

if __name__ == '__main__':
    
    # FMP
    print ('*************************************************************')
    print ('Running fmp package integration tests...')
    print ('*************************************************************')
    dl = datload.DatLoadTests().runTests()
    
    print ('\n*************************************************************')
    print ('fmp package integration tests complete.')
    print ('*************************************************************\n\n')
    
    # TUFLOW
    print ('*************************************************************')
    print ('Running tuflow package integration tests...')
    print ('*************************************************************\n')
    tt = tuflowload.TuflowLoadTests().runTests()
    tu = tuflowupdate.TuflowUpdateTests().runTests()
    tu = tcfmodelfile.UpdateTcfModelFile().runTests()

    print ('\n*************************************************************')
    print ('tuflow package integration tests complete.')
    print ('*************************************************************\n\n')

    
