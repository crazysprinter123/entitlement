##############################################################################
## Test Description
##############################################################################
"""
Setup:

1.Using an avalid account with no subscription to register system to a candlepin server. 
	
Breakdown:
Actions:

1.open subscription-manager-gui

#subscription-manager-gui

2.2. Click "All Available Subscriptions" tab in GUI, then click "update"
	
Expected Results:

1.After step 1, subscription-manager-gui dialog should display.

2.After step 2, a message "no subscriptions match current filters" should be displayed to tell user the result.

Notes:
OBJECT LIST ONLY REFRESHES AFTER PYTHON IS RESTARTED MANUALLY.  THEREFORE, MY TEST WILL ALWAYS FAIL.
PLEASE SEE IF YOU CAN FIX IT!!!!
"""
##############################################################################
from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException
import ldtp
import sys
import time

class tc_ID272161_rhsm_gui_should_launch_although_CA_cert_invalid(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                if not(self.check_window_exist_fast('main-window')):
                    self.open_subscription_manager()
                    self.register_in_gui(username, password)
                    self.click_all_available_subscriptions_tab()
                    self.click_filters_button()
                    #input garbage in the filter box
                    self.input_text('filter-options-window','filter-subscriptions-text','asfsadfasdfasdf')
                    self.click_filter_close_button()
                    self.click_update_button()
                    ldtp.wait()
                    os.execv(__file__, sys.argv)

                #check if the no subscriptions label is there
                #THE OBJECT LIST PRINTED HERE IS BUGGY AND WILL NOT REFRESH UNTIL PYTHON IS RESTARTED!
                #Therefore, we will need to do the check AFTER restarting python, which the following code will handle
                else:
                    if not(self.check_object_exist('main-window','nosubscriptions-in-filter-label')):
                        raise FailException("FAILED: Can't find No-subscriptions-label!")


            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.capture_image(case_name)
            self.restore_gui_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
