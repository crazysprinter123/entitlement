from utils import *
from testcases.rhsmgui.rhsmguibase import RHSMGuiBase
from testcases.rhsmgui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsmgui.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID190632_GUI_quit_subscription_manager_from_menu(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            try:
                self.open_subscription_manager()
                self.click_menu("main-window", "quit-menu")
                self.wait_seconds(5)
                if not self.check_object_exist("main-window", "main-window"):
                    logger.info("It's successful to check quit_subscription_manager_from_menu.")
                else:
                    raise FailException("Test Faild - Failed to check quit_subscription_manager_from_menu!")
                self.open_subscription_manager()
                self.click_my_subscriptions_tab()
                self.sendkeys("<ctrl>", "q")
                self.wait_seconds(5)
                if not self.check_object_exist("main-window", "main-window"):
                    logger.info("It's successful to check quit_subscription_manager_from_menu.")
                else:
                    raise FailException("Test Faild - Failed to check quit_subscription_manager_from_menu!")
                return 0
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                return -1
        finally:
            self.capture_image(case_name)
            self.restore_gui_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    tc_ID190632_GUI_quit_subscription_manager_from_menu().test_run()
