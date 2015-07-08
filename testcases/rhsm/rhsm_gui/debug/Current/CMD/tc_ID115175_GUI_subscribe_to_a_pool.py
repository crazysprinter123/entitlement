from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID115175_GUI_subscribe_to_a_pool(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.register_in_gui(username, password)
                productid = RHSMConstants().get_constant("productid")
#                 self.click_my_installed_products_tab()
#                 self.check_my_installed_products_and_details()
#                 self.click_my_subscriptions_tab()
#                 self.check_my_subscriptions_and_details()
#                 for item in self.sub_listavailpools(productid):
#                     if not self.check_content_in_all_subscription_table(item["SubscriptionName"]):
#                         raise FailException("Test Faild - Failed to list %s in all-subscription-table" % item["SubscriptionName"])
#                 if self.get_my_subscriptions_table_row_count() >= 1:
#                     logger.info("It's successful to auto subscribe: %s" % self.get_my_subscriptions_table_my_subscriptions())
#                 else:
#                     raise FailException("Test Faild - Failed to register and auto subscribe via GUI!")
                raise FailException("Not completed yet ......")
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