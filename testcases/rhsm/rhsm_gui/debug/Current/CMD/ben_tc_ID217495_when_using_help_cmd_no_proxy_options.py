##############################################################################
## Test Description
##############################################################################
"""
Setup:
	
Breakdown:

Actions:
1.run command
#subscription-manager unregister --help

2.run command
#subscription-manager unsubscribe --help

3.run command
#subscritpion-manager facts --help

4.run command
#subscription-manager identity --help

5.run command
#subscription-manager service-Level --help
	
Expected Results:

1.After step1. the output should have no "proxy"  text  in it.
1.After step2. the output should have no "proxy"  text  in it.
1.After step3. the output should have no "proxy"  text  in it.
1.After step4. the output should have no "proxy"  text  in it.
1.After step5. the output should have no "proxy"  text  in it.

Notes:
Completed, but this test seems to fail.  Not sure if it is different in RHEL 7.1

"""
##############################################################################
from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID217495_when_using_help_cmd_no_proxy_options(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                self.run_five_cmds_check_for_proxy()        
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.capture_image(case_name)
            self.restore_gui_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
