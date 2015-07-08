##############################################################################
## Test Description
##############################################################################
"""
Setup:

1.System has been successfully registered to a candlepin server, and subscribed some subscriptions,
	
Breakdown:
Actions:

1.run cmd subscription-manager release --list

#subscription-manager release --list
	
Expected Results:

1.After step1. the out put should like below

+-------------------------------------------+
               Available Releases
+-------------------------------------------+
5.7
5.8
5Server
6.0
6.1
6.2
6.3
6Server
"""

##############################################################################
from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID217491_list_output_has_new_text_output_banner(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.register_and_autosubscribe_in_gui(username, password)
                self.extract_releases_and_check_banner()  
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
