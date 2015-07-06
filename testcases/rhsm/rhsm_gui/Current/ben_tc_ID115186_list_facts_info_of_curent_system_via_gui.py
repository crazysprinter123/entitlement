##############################################################################
## Test Description
##############################################################################
"""
Setup:
	
Breakdown:

Actions:

1.# subscription-manager-gui
2.Click "View System Facts" button.

Expected Results:

1.After step1, the subscription-manager GUI is opened.
2.After step2, the "Facts" dialog pops up and facts info of the current system should successfully display.

Notes:
Works for RHEL 7 and 6 only.  If there is a 5 version, may need to change lines 45-46 and the check_object_status function
"""
##############################################################################
from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID115186_list_facts_info_of_current_system_via_gui(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.register_and_autosubscribe_in_gui(username, password)
                self.click_view_system_facts_menu()
                #check object status handles whether 7 or 6 version
                self.check_window_exist('system-facts-dialog')
                self.check_object_status("main-window", "system-facts-dialog","VISIBLE")
                logger.info("System facts visible!")
                self.check_object_status("main-window", "system-facts-dialog","ENABLED")
                logger.info("System facts enabled!")
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
