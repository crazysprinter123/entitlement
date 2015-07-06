 ##############################################################################
## Test Description
##############################################################################
"""
Setup:

System has been registered to a candlepin server and subscribed some subscriptions
	
Breakdown:

Actions:

1. run subscription-manager release --list command

# subscription-manager release --list

 
	
Expected Results:

1. release should be listed and no error message display as :

[root@mfalesnik-laptop rhsm]# subscription-manager release --list
(32, 'Roura p\xc5\x99eru\xc5\xa1ena (SIGPIPE)')

Notes:
Only checks whether the error message shows.  If it does, the test will fail.

"""
##############################################################################
from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID218491_proper_error_message_should_display_when_error_happens_after_running_release(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try: 
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.register_and_autosubscribe_in_gui(username, password)
                self.run_release_list_and_check()           
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
