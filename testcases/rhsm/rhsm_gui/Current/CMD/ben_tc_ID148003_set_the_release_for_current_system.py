##############################################################################
## Test Description
##############################################################################
"""
Setup:

1. The system is registered.
	
Breakdown:

Actions:

1. List available releases for current system.

# subscription-manager release --set=$release
	
Expected Results:

1. After step1, available releases for current system should display as follows.

# subscription-manager release --set=$release

Release set to: $release

Notes:
inputs --set and sees whether output message is success.  Does not check whether
system is actually changed.

"""
##############################################################################
from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID148003_set_the_release_for_current_system(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                
                self.open_subscription_manager()
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.register_and_autosubscribe_in_gui(username, password)
                
                self.extract_releases_and_check()          
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
