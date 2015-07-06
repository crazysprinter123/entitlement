##############################################################################
## Test Description
##############################################################################
"""
Setup:

1.Prepare a registered machine.
	
Breakdown:

Actions:

1.List identity cert info for the machine.
   # subscription-manager identity
	
Expected Results:

1.The correct org name should display as follows.
   Current identity is: e4defb29-ec53-47ab-95d4-afd7f0867280 
   name: localhost.localdomain 
   org name: Admin Owner 
   org id: ff80808131d2b8e70131d2b9066a0006


Notes: 
Test case does not follow expected results as it is different from 
current machine?  Maybe because my version is Linux 7?  Need to check later.
"""
##############################################################################
from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID115128_display_org_name_with_identity_command_via_cli(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.register_and_autosubscribe_in_gui(username, password)
                self.get_org_through_cli()
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
