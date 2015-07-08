##############################################################################
## Test Description
##############################################################################
"""
Setup:
    
Breakdown:
Actions:

1.go to firstboot

2.press next to go to subscription-manager-firstboot
    
Expected Results:

1.After step2, the page should provided a function to skip choosing a server for Red Hat Registration updates.


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
