"""

 Summary:

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
from integration_tests.test_tuflowupdate import TestError

if __name__ == '__main__':
    
    print ('\nRunning tuflow package integration tests...\n')
    tt = tuflowload.TuflowLoadTests().runTests()
    tu = tuflowupdate.TuflowUpdateTests().runTests()
    tu = tcfmodelfile.UpdateTcfModelFile().runTests()
#     tt.runTests()
    print ('\ntuflow package integration tests complete.\n')

    
