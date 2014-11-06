from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID115137_GUI_import_existing_certificates(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.register_and_autosubscribe_in_gui(username, password)
                cert = self.generate_cert()
                self.sub_unregister()
                self.close_rhsm_gui()
                self.open_subscription_manager()
                self.click_register_button()
                self.click_dialog_next_button()
                self.input_username(username)
                self.input_password(password)
                self.click_dialog_register_button()
                self.click_dialog_cancle_button()
                self.click_import_cert_menu()
                self.click_type_file_name_button()
                self.input_location(cert)
                self.click_import_cert_button()
                if self.check_window_open("information-dialog") and self.check_object_exist("information-dialog", "import-cert-success-label"):
                    logger.info("It's successful to check prompt message displayed ")
                else:
                    raise FailException("Test Faild - Failed to check prompt message displayed")
                # check whether entitlement certificates generated and productid in them or not
                productid = RHSMConstants().get_constant["productid"]
                self.check_entitlement_cert()
                self.click_my_subscriptions_tab()
                if self.get_my_subscriptions_table_my_subscriptions() == productid:
                    logger.info("It's successful to check subscriptions under my_subscriptions tab")
                else:
                    raise FailException("Test Faild - Failed to check subscriptions under my_subscriptions tab")
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
