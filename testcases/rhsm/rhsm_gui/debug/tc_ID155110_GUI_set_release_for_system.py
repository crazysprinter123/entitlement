from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID155110_GUI_set_release_for_system(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.register_and_autosubscribe_in_gui(username, password)
                self.click_preferences_menu()
                for item in self.get_available_release():
                    if self.select_combo_item("system-preferences-dialog", "release-version-combobox", item):
                        logger.info("It's successful to set_release_for_system as %s." % item)
                    else:
                        raise FailException("Test Faild - Failed to set_release_for_system as %s." % item)
                    self.click_close_button()
                    self.click_preferences_menu()
                    if self.check_combo_item_selected("system-preferences-dialog", "release-version-combobox", item):
                        logger.info("It's successful to set_release_for_system as %s after reopen preferences dialog." % item)
                    else:
                        raise FailException("Test Faild - Failed to set_release_for_system as %s after reopen preferences dialog." % item)
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
