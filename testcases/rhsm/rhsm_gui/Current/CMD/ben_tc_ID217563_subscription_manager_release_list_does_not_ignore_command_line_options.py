##############################################################################
## Test Description
##############################################################################
"""
Setup:

1.System has been successfully registered to a candlepin server, and subscribed some subscriptions.
	
Breakdown:

Actions:

1.run subscription-manager release --list with porxy option
#subscription-manager release --list --proxy REDHAT:PORT
	
Expected Results:
1.After step1.the out put should be:
[root@dhcp-15-25 ~]# subscription-manager release --list --proxy squid.corp.redhat.com:3128


Network error, unable to connect to server. Please see /var/log/rhsm/rhsm.log for more information.

Notes:
Assumes you will run subscription-manager release --list --proxy squid.corp.redhat.com:3128 on cli

"""
##############################################################################
from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID217563_subscription_manager_release_list_does_not_ignore_command_line_options(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.register_and_autosubscribe_in_gui(username, password)
                self.run_release_with_proxy_and_check()
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
