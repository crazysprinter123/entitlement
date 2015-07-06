from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID190648_GUI_rhsmicon_dialog_should_display_when_unsubscribe(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.register_and_autosubscribe_in_gui(username, password)
                self.click_my_subscriptions_tab()
                if self.get_my_subscriptions_table_row_count() >= 1:
                    logger.info("It's successful to auto subscribe: %s" % self.get_my_subscriptions_table_my_subscriptions())
                else:
                    raise FailException("Test Faild - Failed to register and auto subscribe via GUI!")
                self.click_remove_subscriptions_button()
                self.check_window_exist("rhsm-notification-dialog")
                if self.check_object_exist("rhsm-notification-dialog", "rhsm-notification-dialog") :
                    logger.info("It's successful to check rhsm-notification-dialog exist")
                else:
                    raise FailException("Test Faild - Failed to check rhsm-notification-dialog exist")
                if self.get_my_subscriptions_table_row_count() == 0:
                    logger.info("It's successful to check unsubscribed product disappear from the table")
                else:
                    raise FailException("Test Faild - Failed to check unsubscribed product disappear from the table")
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