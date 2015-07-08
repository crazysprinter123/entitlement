##############################################################################
## Test Description
##############################################################################
"""
Setup:

Breakdown:

Actions:

1. Start Firstboot
2. Click Next go to subscription-manager-firstboot page
3. Click Next button. 

    
Expected Results:

1After step3 There should be a forward button on the bottom right not "Finish". Finshs should be displayed in the last screen

Notes:
Completed.
"""
##############################################################################
from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID324773_firstboot_appears_in_gui(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                self.open_firstboot()
                self.click_firstboot_fwd_button()
                self.check_object_exist('firstboot-main-window', 'firstboot-fwd-button')
                self.close_firstboot()
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.capture_image(case_name)
            #need to restore firstboot environment
            self.restore_firstboot_environment()
            self.restore_gui_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
