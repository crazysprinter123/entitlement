##############################################################################
## Test Description
##############################################################################
"""
Setup:

1.Prepare an valid account  with no subscriptions

    e.g.

    username:stage_test_40

    password:redhat
	
Breakdown:
Actions:

1.register

#subscription-manager register --username=stage_test_40 --password=redhat

2.autosubscribe

#subscription-manager subscribe --auto
	
Expected Results:

1.After step 1, system have been registered successfully.

2.After step 2, failed to autosubscribe and a proper error message indicating the reason of failure should be displayed just like below:

[root@dhcp-15-25 ~]# subscription-manager attach --auto
Installed Product Current Status:
Product Name: Red Hat Enterprise Linux Server
Status:       Not Subscribed

Unable to find available subscriptions for all your installed products.

Notes:
Test assumes you used the suggested username and password listed above!
"""
##############################################################################
from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID190919_display_proper_error_message_when_autosubscribe_fails(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                self.check_error_when_autosubscribe_fails()      
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
