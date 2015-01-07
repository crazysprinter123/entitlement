import ldtp, time
from utils import *
from utils.tools.shell.command import Command
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from utils.exception.failexception import FailException

class RHSMGuiBase(unittest.TestCase):
    # ========================================================
    #     0. LDTP GUI Common Functions
    # ========================================================
    def restore_gui_environment(self):
        self.close_rhsm_gui()
        self.unregister()

    def close_rhsm_gui(self):
        cmd = "killall -9 subscription-manager-gui"
        (ret, output) = Command().run(cmd)
        if ret == 0:
            logger.info("It's successful to close subscription-manager-gui.")

    def unregister(self):
        # close subscription-manager-gui
        cmd = "subscription-manager unregister"
        (ret, output) = Command().run(cmd)
        if ret == 0:
            logger.info("It's successful to unregister system.")

    def capture_image(self, image_name="", window=""):
        # capture image and name it by time
        time.sleep(5.0)
        image_path = GUI_IMG_PATH
        if not os.path.exists(GUI_IMG_PATH):
            os.makedirs(GUI_IMG_PATH)
        picture_name = time.strftime('%Y%m%d%H%M%S') + "-" + image_name + ".png"
        ldtp.imagecapture(window, image_path + "/" + picture_name)
        logger.info("capture image: %s to runtime directory" % picture_name)

    def list_objects(self, window):
        logger.info("get objects list in window: %s" % window)
        all_objects_list = self.__parse_objects(ldtp.getobjectlist(RHSMGuiLocator().get_locator(window)))
        logger.info("sorted all_objects_list: %s" % all_objects_list)

    def __parse_objects(self, objects_list):
        logger.info("parse objects list")
        window_list = []
        tab_list = []
        button_list = []
        table_list = []
        text_list = []
        menu_list = []
        checkbox_list = []
        label_list = []
        others_list = []
        parsed_objects_list = [window_list, tab_list, button_list, table_list, text_list, menu_list, checkbox_list, label_list, others_list]
        for item in objects_list:
            if item.startswith("frm") or item.startswith("dlg"):
                window_list.append(item)
            elif item.startswith("ptab"):
                tab_list.append(item)
            elif item.startswith("btn"):
                button_list.append(item)
            elif item.startswith("ttbl") or item.startswith("tbl"):
                table_list.append(item)
            elif item.startswith("txt"):
                text_list.append(item)
            elif item.startswith("mnu"):
                menu_list.append(item)
            elif item.startswith("chk"):
                checkbox_list.append(item)
            elif item.startswith("lbl"):
                label_list.append(item)
            else:
                others_list.append(item)
        return parsed_objects_list

    def check_window_exist(self, window):
        ldtp.waittillguiexist(RHSMGuiLocator().get_locator(window))

    def close_window(self, window):
        ldtp.closewindow(RHSMGuiLocator().get_locator(window))
        self.check_window_closed(window)

    def check_window_closed(self, window):
        ldtp.waittillguinotexist(RHSMGuiLocator().get_locator(window))

    def check_window_open(self, window):
        self.check_window_exist(window)
        return ldtp.guiexist(RHSMGuiLocator().get_locator(window))

    def check_element_exist(self, window, type, name):
        logger.info("check_element_exist")
        logger.info(ldtp.getobjectlist(RHSMGuiLocator().get_locator(window)))
        return ldtp.guiexist(RHSMGuiLocator().get_locator(window), type + name)

    def click_button(self, window, button_name):
        ldtp.click(RHSMGuiLocator().get_locator(window), RHSMGuiLocator().get_locator(button_name))

    def click_menu(self, window, menu_name):
        ldtp.click(RHSMGuiLocator().get_locator(window), RHSMGuiLocator().get_locator(menu_name))

    def check_checkbox(self, window, checkbox_name):
        ldtp.check(RHSMGuiLocator().get_locator(window), RHSMGuiLocator().get_locator(checkbox_name))

    def uncheck_checkbox(self, window, checkbox_name):
        ldtp.uncheck(RHSMGuiLocator().get_locator(window), RHSMGuiLocator().get_locator(checkbox_name))

    def verifycheck_checkbox(self, window, checkbox_name):
        return ldtp.verifycheck(RHSMGuiLocator().get_locator(window), RHSMGuiLocator().get_locator(checkbox_name))

    # ========================================================
    #     1. LDTP GUI Keyword Functions
    # ========================================================
    def open_subscription_manager(self):
        logger.info("open_subscription_manager")
        if int(RHSMGuiLocator().get_os_serials()) == "5":
            ldtp.launchapp2("subscription-manager-gui")
        else:
            ldtp.launchapp("subscription-manager-gui")
        self.check_window_exist("main-window")

    def open_firstboot(self):
        logger.info("open_firstboot")
        self.set_os_release()
        ldtp.launchapp("firstboot")
        self.check_window_exist('firstboot-main-window')

    def close_firstboot(self):
        logger.info("close_firstboot")
        cmd = "killall -9 firstboot"
        (ret, output) = Command().run(cmd)
        if ret == 0:
            logger.info("It's successful to close firstboot-gui.")

    def register_in_gui(self, username, password):
        self.click_register_button()
        self.click_dialog_next_button()
        self.input_username(username)
        self.input_password(password)
        self.click_dialog_register_button()
        self.click_dialog_next_button()
        self.click_dialog_cancle_button()

    def register_and_autosubscribe_in_gui(self, username, password):
        self.click_register_button()
        self.click_dialog_next_button()
        self.input_username(username)
        self.input_password(password)
        self.click_dialog_register_button()
        self.click_dialog_next_button()
        self.click_dialog_subscribe_button()
        time.sleep(10)

    def click_register_button(self):
        self.click_button("main-window", "register-button")
        self.check_window_exist("register-dialog")
        logger.info("click_register_button")

    def click_autoattach_button(self):
        logger.info("click_autoattach_button")
        self.click_button("main-window", "auto-subscribe-button")
        self.check_window_exist("register-dialog")
        self.wait_until_button_enabled("register-dialog", "dialog-register-button")

    def click_attach_button(self):
        logger.info("click_attach_button")
        self.click_button("register-dialog", "dialog-register-button")
        self.check_window_closed("register-dialog")
        time.sleep(20)

    def click_remove_subscriptions_button(self):
        logger.info("click_remove_subscriptions_button")
        self.click_button("main-window", "remove-subscriptions-button")
        self.check_window_exist("question-dialog")
        self.click_button("question-dialog", "yes-button")
        self.check_window_closed("question-dialog")

    def click_ImportCertificate_button(self):
        logger.info("click_ImportCertificate_menu")
        self.click_menu("main-window", "importcert-menu")
        self.check_window_exist("import-cert-dialog")

#     def click_Certificate_Location(self):
#         logger.info("click_Certificate_Location")
#         self.click_button("import-cert-dialog", "type-pem-name-button")
#         time.sleep(30)
#         if ldtp.guiexist(RHSMGuiLocator().get_locator("import-cert-dialog"), RHSMGuiLocator().get_locator("location-text")):
#             pass

    def click_type_file_name_button(self):
        if ldtp.guiexist(RHSMGuiLocator().get_locator("import-cert-dialog"), RHSMGuiLocator().get_locator("location-text")) == 1:
            return
        else:
            logger.info("click_type_file_name_button")
            self.click_button("import-cert-dialog", "type-file-name-button")
            ldtp.waittillguiexist(RHSMGuiLocator().get_locator("import-cert-dialog"), RHSMGuiLocator().get_locator("location-text"))

    def click_import_cert_button(self):
        logger.info("click import cert button")
        self.click_button("import-cert-dialog", "import-file-button")
        self.check_window_exist("error-cert-dialog")

    def close_error_cert_dialog(self):
        self.click_button("error-cert-dialog", "ok-button")
        time.sleep(10)
        if not self.check_object_exist("error-cert-dialog", "error-cert-dialog"):
            logger.info("It's successful to close import-cert-error-dialog and it's successful to check importing wrong cert")

    def select_org_and_register(self):
        self.check_window_exist("register-dialog")
        ldtp.selectlastrow('register-dialog', 'orgs-view-table')
        logger.info("select ACME_Corporation org")
        self.click_button('register-dialog', 'dialog-register-button')
        logger.info("It's successful register, please check /etc/pki/consumer")

    def click_open_file_button(self):
        logger.info("click_open_file_button")
        self.click_button("import-cert-dialog", "import-button")
        self.check_window_exist("information-dialog")

    def click_dialog_next_button(self):
#         if RHSMGuiLocator().get_os_serials() == "5" or RHSMGuiLocator().get_os_serials() == "6" or RHSMGuiLocator().get_os_serials() == "7":
        logger.info("click_dialog_next_button")
        self.click_button("register-dialog", "dialog-register-button")
        self.check_window_exist("register-dialog")
        # logger.info(ldtp.getwindowlist())

    def click_configure_proxy_button(self):
#         if RHSMGuiLocator().get_os_serials() == "5" or RHSMGuiLocator().get_os_serials() == "6":
        logger.info("click_configure_proxy_button")
        self.click_button("register-dialog", "configure-proxy-button")
        self.check_window_exist("proxy-configuration-dialog")

    def click_dialog_register_button(self):
#         if RHSMGuiLocator().get_os_serials() == "5" or RHSMGuiLocator().get_os_serials() == "6":
        self.click_button("register-dialog", "dialog-register-button")
        self.wait_until_button_enabled("register-dialog", "dialog-register-button")
#         else:
#             logger.info("click_dialog_register_button")
#             self.click_button("register-dialog", "dialog-register-button")
#             self.check_window_exist("subscribe-dialog")

    def click_dialog_register_button_without_autoattach(self):
        logger.info("click_dialog_register_button_without_autoattach")
        self.click_button("register-dialog", "dialog-register-button")
        self.check_window_closed("register-dialog")

    def click_dialog_register_for_account_without_org_access(self):
        self.click_button('register-dialog', 'dialog-register-button')
        time.sleep(10)
        if self.check_object_exist('error-dialog', 'error-user-label'):
            return 1
        else:
            self.assert_(True, case_name)

    def click_dialog_subscribe_button(self):
        logger.info("click_dialog_subscribe_button")
        self.click_button("register-dialog", "dialog-register-button")
        self.check_window_closed("register-dialog")

    def click_dialog_cancle_button(self):
        logger.info("click_dialog_cancle_button")
#         if RHSMGuiLocator().get_os_serials() == "5" or RHSMGuiLocator().get_os_serials() == "6":
        self.click_button("register-dialog", "dialog-cancle-button")
        self.check_window_closed("register-dialog")
#         else:
#             self.click_button("subscribe-dialog", 'dialog-cancle-button')
#             self.check_window_closed("subscribe-dialog")

    def click_proxy_close_button(self):
        logger.info("click_proxy_close_button")
        self.click_button("proxy-configuration-dialog", "proxy-close-button")
        self.check_window_closed("proxy-configuration-dialog")

    def click_close_button(self):
        logger.info("click_close_button")
        self.click_button("system-preferences-dialog", "close-button")
        self.check_window_closed("system-preferences-dialog")

    def click_filter_close_button(self):
        logger.info("click_filter_close_button")
        self.click_button("filter-options-window", "close-button")
        self.check_window_closed("filter-options-window")

    def click_all_available_subscriptions_tab(self):
        logger.info("click_all_available_subscriptions_tab")
        self.click_tab('all-available-subscriptions')
        ldtp.wait(5)

    def click_update_button(self):
        logger.info("click_update_button")
        self.click_button("main-window", "update-button")
        self.check_window_exist("search-dialog")
        self.check_window_closed("search-dialog")

    def click_filters_button(self):
        logger.info("click_filters_button")
        self.click_button("main-window", "filters-button")
        self.check_window_exist("filter-options-window")

    def click_my_subscriptions_tab(self):
        logger.info("click_my_subscriptions_tab")
        self.click_tab('my-subscriptions')
        ldtp.wait(5)

    def click_my_installed_products_tab(self):
        logger.info("click_my_installed_products_tab")
        self.click_tab('my-installed-software')
        ldtp.wait(5)

    def input_location(self, location):
        logger.info("input_location")
        self.input_text("import-cert-dialog", "location-text", location)
        ldtp.wait(5)

    def input_username(self, username):
        logger.info("input_username")
        self.input_text("register-dialog", "login-text", username)

    def input_password(self, password):
        logger.info("input_password")
        self.input_text("register-dialog", "password-text", password)

    def input_HTTP_proxy(self, proxy):
        logger.info("input_HTTP_proxy")
        self.input_text("proxy-configuration-dialog", "proxy-location-text", proxy)

    def get_all_subscription_table_row_count(self):
        return self.get_table_row_count("main-window", 'all-subscription-table')

    def get_my_subscriptions_table_row_count(self):
        return self.get_table_row_count("main-window", 'my-subscription-table')

    def click_view_system_facts_menu(self):
#         if RHSMGuiLocator().get_os_serials() == "6":
        logger.info("click_view_system_facts_menu")
        self.click_menu("main-window", "system-menu")
        self.click_menu("main-window", "viewsystemfacts-menu")
        self.check_window_exist("system-facts-dialog")

    def click_import_cert_menu(self):
#         if RHSMGuiLocator().get_os_serials() == "6":
        logger.info("click_import_cert_menu")
        self.click_menu("main-window", "system-menu")
        self.click_menu("main-window", "importcert-menu")
        self.check_window_exist("import-cert-dialog")

    def click_preferences_menu(self):
#         if RHSMGuiLocator().get_os_serials() == "6":
        logger.info("click_preferences_menu")
        self.click_menu("main-window", "system-menu")
        self.click_menu("main-window", "preferences-menu")
        self.check_window_exist("system-preferences-dialog")

    def click_gettingstarted_menu(self):
#         if RHSMGuiLocator().get_os_serials() == "6":
        logger.info("click_gettingstarted_menu")
        self.click_menu("main-window", "help-menu")
        self.click_menu("main-window", "gettingstarted-menu")
        self.check_window_exist("subscription-manager-manual-window")

    def click_onlinedocumentation_menu(self):
#         if RHSMGuiLocator().get_os_serials() == "6":
        logger.info("click_onlinedocumentation_menu")
        self.click_menu("main-window", "help-menu")
        self.click_menu("main-window", "onlinedocumentation-menu")
        self.check_window_exist("onlinedocumentation-window")

    def click_about_menu(self):
#         if RHSMGuiLocator().get_os_serials() == "6":
        logger.info("click_about_menu")
        self.click_menu("main-window", "help-menu")
        self.click_menu("main-window", "about-menu")
        self.check_window_exist("about-subscription-manager-dialog")

    def click_unregister_menu(self):
        logger.info("click_unregister_menu")
        self.click_menu("main-window", "unregister-menu")
        self.check_window_exist("question-dialog")
        self.click_button("question-dialog", "yes-button")
        self.check_window_closed("question-dialog")

    def click_facts_view_tree(self, branch):
#         if RHSMGuiLocator().get_os_serials() == "6":
        logger.info("click_facts_view_tree")
        ldtp.doubleclickrow(RHSMGuiLocator().get_locator("system-facts-dialog"), RHSMGuiLocator().get_locator("facts-view-table"), branch)
        ldtp.wait(5)

    def check_manual_attach_checkbox(self):
        logger.info("check_manual_attach_checkbox")
        self.check_checkbox("register-dialog", "manual-attach-checkbox")

    def uncheck_manual_attach_checkbox(self):
        logger.info("uncheck_manual_attach_checkbox")
        self.uncheck_checkbox("register-dialog", "manual-attach-checkbox")

    def check_HTTP_proxy_checkbox(self):
        logger.info("check_HTTP_proxy_checkbox")
        self.check_checkbox("proxy-configuration-dialog", "proxy-checkbox")


    def get_my_subscriptions_table_my_subscriptions(self):
        for row in range(self.get_my_subscriptions_table_row_count()):
            return self.get_table_cell("main-window", 'my-subscription-table', row , 0)

    def check_content_in_all_subscription_table(self, content):
        for row in range(self.get_all_subscription_table_row_count()):
            if self.get_table_cell("main-window", 'all-subscription-table', row , 0) == content:
                logger.info("%s is listed in all-subscription-table" % content)
                return True
        return False

    def check_content_in_my_installed_products_table(self, content):
        for row in range(self.get_all_subscription_table_row_count()):
            if self.get_table_cell("main-window", 'installed-product-table', row , 0) == content:
                logger.info("%s is listed in my_installed_products_table" % content)
                return True
        return False

    def check_content_in_my_subscriptions_table(self, content):
        for row in range(self.get_my_subscriptions_table_row_count()):
            if self.get_table_cell("main-window", 'my-subscription-table', row , 0) == content:
                logger.info("%s is listed in my_subscriptions_table" % content)
                return True
        return False

    def check_list_item_selected(self, window, list, item):
#         for row in range(self.get_all_subscription_table_row_count()):
#             if RHSMGuiLocator().get_locator_cell("main-window", 'my-subscription-table', row , 0) == content:
#                 logger.info("%s is listed in my_subscriptions_table" % content)
#                 return True
         return False

    def check_item_in_list(self, window, list, item):
#         for row in range(self.get_all_subscription_table_row_count()):
#             if RHSMGuiLocator().get_locator_cell("main-window", 'my-subscription-table', row , 0) == content:
#                 logger.info("%s is listed in my_subscriptions_table" % content)
#                 return True
         return False

    def check_org_displayed_in_facts(self, username, password):
        cmd = "subscription-manager orgs --user=%s --password=%s | grep Key" % (username, password)
        (ret, output) = Command().run(cmd)
        org_in_cml = output.split(":")[1].strip()
        if ret == 0:
            logger.info("It's successful to get org %s by CML" % org_in_cml)
        else:
            raise FailException("Test Failed - Failed to get org by CML.")
        # current we can not get orgs label, instead we got "lblOrganizationValue"
        org_in_cml = "OrganizationValue"
        if self.check_element_exist("system-facts-dialog", "lbl", org_in_cml):
            logger.info("It's successful to get org %s in system facts" % org_in_cml)
        else:
            raise FailException("Test Failed - Failed to get org %s in system facts." % org_in_cml)

    def check_system_uuid_displayed_in_facts(self):
        cmd = "subscription-manager identity | grep 'Current identity is'"
        (ret, output) = Command().run(cmd)
        if ret == 0:
            system_uuid = output.split(":")[1].strip()
            logger.info("It's successful to get system identity %s by CML" % system_uuid)
        else:
            raise FailException("Test Failed - Failed to get system identity by CML.")
        if self.get_facts_value_by_name("system.uuid") == system_uuid:
            return True
        else:
            return False

    def get_facts_value_by_name(self, facts_name):
#         if RHSMGuiLocator().get_os_serials() == "6":
        for row in range(ldtp.getrowcount(RHSMGuiLocator().get_locator("system-facts-dialog"), RHSMGuiLocator().get_locator("facts-view-table"))):
            if(ldtp.getcellvalue(RHSMGuiLocator().get_locator("system-facts-dialog"), RHSMGuiLocator().get_locator("facts-view-table"), row, 0).strip() == facts_name):
                logger.info("get_facts_value_by_name")
                return ldtp.getcellvalue(RHSMGuiLocator().get_locator("system-facts-dialog"), RHSMGuiLocator().get_locator("facts-view-table"), row, 1)
        raise FailException("Test Failed - Failed to get_facts_value_by_name.")

    def check_server_url(self, server_url):
        if ldtp.gettextvalue(RHSMGuiLocator().get_locator("register-dialog"), RHSMGuiLocator().get_locator("server-url-text")) == server_url:
            return True
        else:
            return False

    def check_table_value_exist(self, window, table, cellvalue):
        return ldtp.doesrowexist(RHSMGuiLocator().get_locator(window), RHSMGuiLocator().get_locator(table), cellvalue)

    def check_object_exist(self, window, object_name):
        logger.info("check_object_exist")
        return ldtp.guiexist(RHSMGuiLocator().get_locator(window), RHSMGuiLocator().get_locator(object_name))

    def check_menu_enabled(self, window, menu_name):
        logger.info("check_menu_enabled")
        return ldtp.menuitemenabled(RHSMGuiLocator().get_locator(window), RHSMGuiLocator().get_locator(menu_name))

    def check_object_status(self, window, object_name, status):
        if status == "ENABLED":
            real_status = ldtp.state.ENABLED
        elif status == "VISIBLE":
            real_status = ldtp.state.VISIBLE
        return ldtp.hasstate(RHSMGuiLocator().get_locator(window), RHSMGuiLocator().get_locator(object_name), real_status)

    def wait_until_button_enabled(self, window, button_name):
#         if RHSMGuiLocator().get_os_serials() == "5" or RHSMGuiLocator().get_os_serials() == "6":
        while ldtp.hasstate(RHSMGuiLocator().get_locator(window), RHSMGuiLocator().get_locator(button_name), ldtp.state.ENABLED) == 0:
            ldtp.wait(5)

    def input_text(self, window, text, text_value):
        ldtp.settextvalue(RHSMGuiLocator().get_locator(window), RHSMGuiLocator().get_locator(text), text_value)

    def verify_text(self, window, text, text_value):
        ldtp.verifysettext(RHSMGuiLocator().get_locator(window), RHSMGuiLocator().get_locator(text), text_value)

    def click_tab(self, tab_name):
        ldtp.selecttab(RHSMGuiLocator().get_locator("main-window"), RHSMGuiLocator().get_locator("all-tabs"), RHSMGuiLocator().get_locator(tab_name))

    def get_table_row_count(self, window, table_name):
        return ldtp.getrowcount(RHSMGuiLocator().get_locator(window), RHSMGuiLocator().get_locator(table_name))

    def get_table_cell(self, window, table_name, row, colomn):
        return ldtp.getcellvalue(RHSMGuiLocator().get_locator(window), RHSMGuiLocator().get_locator(table_name), row, colomn)

    def sendkeys(self, key1, key2="", key3=""):
        ldtp.keypress(key1)
        if not key2 == "":
            ldtp.keypress(key2)
            if not key3 == "":
                ldtp.keypress(key3)
                ldtp.keyrelease(key3)
            ldtp.keyrelease(key2)
        ldtp.keyrelease(key1)

    def wait_seconds(self, seconds):
        ldtp.wait(seconds)

     # ## firstboot gui
    def welcome_forward_click(self):
        self.click_button('firstboot-main-window', 'firstboot-fwd-button')
        if self.check_object_exist('firstboot-main-window', 'firstboot-agr-button'):
            logger.info("It's successful to click welcome-forward button")
        else:
            raise FailException("TestFailed - Failed to check agree-license-button")

    def license_forward_click(self):
        self.click_button('firstboot-main-window', 'firstboot-fwd-button')
        if self.check_object_exist('firstboot-main-window', 'firstboot-registeration-warning-label') or self.check_object_exist("firstboot-main-window", "firstboot-register-now-button"):
            logger.info("It's successful to click license-forward button")
        else:
            raise FailException("TestFailed - Failed to check registeration-warning-label or register-now-button")

    def software_update_forward_click(self):
        self.click_button('firstboot-main-window', 'firstboot-fwd-button')
        if self.check_object_exist('firstboot-main-window', "firstboot_creat_user-label") or self.check_object_exist('firstboot-main-window', "firstboot-register-rhsm-button"):
            logger.info("It's successful to click software_update_forward button")
        else:
            raise FailException("TestFailed - Failed to check firstboot_creat_user-label or firstboot-register-rhsm-button")

    def create_user_forward_click(self):
        self.click_button('firstboot-main-window', 'firstboot-fwd-button')
        self.check_window_exist('firstboot-wng-dialog')
        if self.check_object_exist('firstboot-wng-dialog', 'firstboot-wng-dialog'):
            logger.info("It's successful to click create_user_forward button")
        else:
            raise FailException("TestFailed - Failed to check create-user-warning-dialog")

    def donot_set_user_yes_button(self):
        self.click_button('firstboot-wng-dialog', 'firstboot-yes-button')
        if not self.check_object_exist('firstboot-wng-dialog', 'firstboot-wng-dialog'):
            logger.info("It's successful to click donot_set_user_yes_button")
        else:
            raise FailException("TestFailed - Failed to check create-user-warning-dialog disappear")

    def date_time_forward_click(self):
        self.click_button('firstboot-main-window', 'firstboot-fwd-button')
        self.check_window_exist('firstboot-err-dialog')
        if self.check_object_exist('firstboot-err-dialog', 'firstboot-err-dialog'):
            logger.info("It's successful to click date_time_forward button")
        else:
            raise FailException("TestFailed - Failed to check date-time-error-dialog")

    def kdump_ok_button(self):
        self.click_button('firstboot-err-dialog', 'firstboot-ok-button')
        if not self.check_object_exist('firstboot-err-dialog', 'firstboot-err-dialog'):
            logger.info("It's successful to click kdump_ok_button")
        else:
            raise FailException("TestFailed - Failed to check date-time-error-dialog disappear")

    def kdump_finish_button(self):
        self.click_button('firstboot-main-window', 'firstboot-finish-button')
        if not self.check_object_exist("firstboot-main-window", "firstboot-main-window"):
            logger.info("It's successful to click kdump_finish_button")
        else:
            raise FailException("TestFailed - Failed to check firstboot-main-window disappear")

    def choose_service_forward_click(self):
        self.click_button('firstboot-main-window', 'firstboot-fwd-button')
        time.sleep(10)
        if self.check_object_exist('firstboot-main-window', "firstboot_activationkey-checkbox") or self.check_object_exist('firstboot-main-window', "classic-login-text"):
            logger.info("It's successful to click choose_service_forward button")
        else:
            raise FailException("TestFailed - Failed to check firstboot_activationkey-checkbox")

    def registeration_with_forward_click(self):
        self.click_button('firstboot-main-window', 'firstboot-fwd-button')
        if self.check_object_exist('firstboot-main-window', "firstboot-manual-checkbox"):
            logger.info("It's successful to click registeration_with_forward button")
        else:
            raise FailException("TestFailed - Failed to check firstboot-manual-checkbox")

    def input_firstboot_username(self, username):
        self.input_text("firstboot-main-window", "firstboot-login-text", username)
        logger.info("It's successful to input username")

    def input_firstboot_password(self, password):
        self.input_text("firstboot-main-window", "firstboot-password-text", password)
        logger.info("It's successful to input password")

    def check_firstboot_manual(self):
        self.check_checkbox("firstboot-main-window", "firstboot-manual-checkbox")
        logger.info("It's successful to check manual-attach-checkbox")

    def enter_account_info_forward_click(self):
        self.click_button('firstboot-main-window', 'firstboot-fwd-button')
        time.sleep(20)
        if self.check_object_exist('firstboot-main-window', 'firstboot-skip-auto-label'):
            logger.info("It's successful to click enter_account_info_forward button")
        else:
            raise FailException("TestFailed - Failed to check firstboot-skip-auto-label")

    def skip_auto_forward_click(self):
        self.click_button('firstboot-main-window', 'firstboot-fwd-button')
        time.sleep(10)
        if self.check_object_exist("firstboot-main-window", "firstboot_creat_user-label"):
            logger.info("It's successful to click skip_auto_forward button")
        else:
            raise FailException("TestFailed - Failed to check firstboot_creat_user-label")

    def select_classic_mode(self):
        self.click_button('firstboot-main-window', 'firstboot-classic-select-button')
        logger.info("It's successful to click classic mode registeration button")

    def input_firstboot_classic_username(self, username):
        self.input_text("firstboot-main-window", "classic-login-text", username)
        logger.info("It's successful to input classic username")

    def input_firstboot_classic_password(self, password):
        self.input_text("firstboot-main-window", "classic-password-text", password)
        logger.info("It's successful to input classic password")

    def firstboot_classic_redhat_account_forward_button_click(self):
        self.click_button('firstboot-main-window', 'classic-forward-button')
        time.sleep(20)
        if self.check_object_exist("firstboot-main-window", "classic-OS-realeaseversion-label"):
            logger.info("It's successful to click redhat-account-forward button")
        else:
            raise FailException("TestFailed - TestFailed to enable redhat-account-forward-label")

    def firstboot_classic_os_release_forward_button_click(self):
        self.click_button('firstboot-main-window', 'classic-forward-button')
        if self.check_object_exist('firstboot-main-window', "classic-set-systemname-text"):
            logger.info("It's successful to click firstboot-classic-os-release-forward-button")
        else:
            raise FailException("TestFailed - Failed to check system text")

    def firstboot_classic_profile_forward_button_click(self):
        self.click_button('firstboot-main-window', 'classic-forward-button')
        time.sleep(70)
        if self.check_object_exist('firstboot-main-window', "firstboot-classic-reviewsubscription-label"):
            logger.info("It's successful to click firstboot_classic_profile_forward_button")
        else:
            raise FailException("TestFailed - Failed to check firstboot-classic-reviewsubscription-label")

    def firstboot_classic_input_systemname(self):
        self.input_text("firstboot-main-window", "classic-set-systemname-text", "zhangqq")
        logger.info("It's successful to set system name")

    def firstboot_classic_reviewsubscription_forward_button_click(self):
        self.click_button('firstboot-main-window', 'classic-forward-button')
        if self.check_object_exist('firstboot-main-window', "firstboot-classic-finishupdate-label"):
            logger.info("It's successful to click firstboot_classic_profile_forward_button")
        else:
            raise FailException("TestFailed - Failed to check firstboot-classic-finishupdate-label")

    def firstboot_classic_finishupdate_forward_button_click(self):
        self.click_button('firstboot-main-window', 'classic-forward-button')
        if self.check_object_exist('firstboot-main-window', "firstboot_creat_user-label"):
            logger.info("It's successful to click finishupdate_forward_button")
        else:
            raise FailException("TestFailed - Failed to check firstboot_creat_user-label")

    # ## rhn_classic register and unregister function
    def register_rhn_classic(self, username, password):
        # open rhn_register gui
        self.set_os_release()
        ldtp.launchapp("rhn_register")
        self.check_window_exist("classic-main-window")
        if self.check_object_status("classic-main-window", "classic-software-update-label", 'ENABLED'):
            logger.info("It's successful to open rhn-classic-registeration-gui")
        else:
            raise FailException("TestFailed - TestFailed to open rhn-classic-registeration-gui")

        # click software-update-forward button
        self.click_button('classic-main-window', 'classic-forward-button')
        if self.check_object_status("classic-main-window", "classic-choose-service-label", 'ENABLED'):
            logger.info("It's successful to click softwaref update forward button")
        else:
            raise FailException("TestFailed - TestFailed to enable classic-software-update-label")

        # click choose-service-forward button
        self.click_button('classic-main-window', 'classic-forward-button')
        time.sleep(5)
        if self.check_object_status("classic-main-window", "classic-redhat-account-label", 'ENABLED'):
            logger.info("It's successful to click choose-service-forward button")
        else:
            raise FailException("TestFailed - TestFailed to enable classic-redhat-account-label")

        # input account info
        self.input_text("classic-main-window", "classic-login-text", username)
        logger.info("It's successful to input username")
        self.input_text("classic-main-window", "classic-password-text", password)
        logger.info("It's successful to input password")

        # click redhat-account-forward button
        self.click_button('classic-main-window', 'classic-forward-button')
        time.sleep(20)
        if self.check_object_status("classic-main-window", "classic-OS-realeaseversion-label", 'ENABLED'):
            logger.info("It's successful to click redhat-account-forward button")
        else:
            raise FailException("TestFailed - TestFailed to enable redhat-account-forward-label")

        # click OS-releaseversion-forward button
        self.click_button('classic-main-window', 'classic-forward-button')
        self.check_window_exist("classic-confirm-osrelease-window")
        if self.check_object_exist("classic-confirm-osrelease-window", "classic-confirm-osrelease-window"):
            logger.info("It's successful to click OS-releaseversion-forward button")
        else:
            raise FailException("TestFailed - TestFailed to prompt classic-confirm-osrelease-window")

        # click classic-confirm-osrelease-window yes-continue button
        self.click_button('classic-confirm-osrelease-window', 'classic-confirm-osrelease-yes-button')
        time.sleep(10)
        if self.check_object_status("classic-main-window", "classic-create-profile-label", 'ENABLED'):
            logger.info("It's successful to click classic-confirm-osrelease-window yes-continue button")
        else:
            raise FailException("TestFailed - TestFailed to enable classic-confirm-osrelease-window yes-continue button")

        # set system name
        self.input_text("classic-main-window", "classic-set-systemname-text", "zhangqq")
        logger.info("It's successful to set system name")

        # click create-profile-forward button
        self.click_button('classic-main-window', 'classic-forward-button')
        time.sleep(50)
        if self.check_object_status("classic-main-window", "classic-review-subscription-label", 'ENABLED'):
            logger.info("It's successful to click create-profile-forward button")
        else:
            raise FailException("TestFailed - TestFailed to enable classic-review-subscription-label")

        # click review-subscription-forward button
        self.click_button('classic-main-window', 'classic-forward-button')
        if self.check_object_exist("classic-updates-configured-window", "classic-updates-configured-window"):
            logger.info("It's successful to click review-subscription-forward button")
        else:
            raise FailException("TestFailed - TestFailed to prompt updates-configured-window")

        # click updates-configured-finish button
        self.click_button('classic-updates-configured-window', 'classic-updates-configured-finish-button')
        if not self.check_object_exist("classic-updates-configured-window", "classic-updates-configured-window"):
            logger.info("It's successful to register using firstboot with rhn-classic mode")
        else:
            raise FailException("TestFailed - TestFailed to close updates-configured window")

    def unregister_rhn_classic(self):
        cmd = "subscription-manager identity"
        (ret, output) = Command().run(cmd)
        if ret == 0 and "server type: RHN Classic" in output:
            logger.info("It's successful to check the system has been registered with rhn_classic mode, and begin to unregister now")
        else:
            raise FailException("TestFailed - TestFailed to check if the system has been registered with rhn_classic mode")

        cmd = "rm -f /etc/sysconfig/rhn/systemid"
        (ret, output) = Command().run(cmd)
        if ret == 0:
            logger.info("It's successful to remove /etc/sysconfig/rhn/systemid")

        cmd = "sed -i 's/enabled =.*/enabled = 0/g' /etc/yum/pluginconf.d/rhnplugin.conf"
        (ret, output) = Command().run(cmd)
        if ret == 0:
            logger.info("It's successful to configure /etc/yum/pluginconf.d/rhnplugin.conf")

        cmd = "subscription-manager identity"
        (ret, output) = Command().run(cmd)
        if "server type: RHN Classic" not in output:
            logger.info("It's successful to unregister rhn_classic")
        else:
            raise FailException("TestFailed - TestFailed to unregister rhn_classic")

    def check_consumer_cert_files(self, exist=True):
        cmd = "ls /etc/pki/consumer"
        (ret, output) = Command().run(cmd)
        if exist:
            if ret == 0 and "cert.pem" in output and "key.pem" in output:
                logger.info("It is successful to check certificate files in /etc/pki/consumer!")
            else:
                raise FailException("Failed to check certificate files in /etc/pki/consumer!")
        else:
            if ret != 0 or not ("cert.pem" in output or "key.pem" in output):
                logger.info("It is successful to check certificate files in /etc/pki/consumer!")
            else:
                raise FailException("Failed to check certificate files in /etc/pki/consumer!")

    def check_entitlement_cert_files(self, exist=True):
        cmd = "ls /etc/pki/entitlement"
        (ret, output) = Command().run(cmd)
        if exist:
            if ret == 0 and "pem" in output and "key.pem" in output:
                logger.info("It is successful to check certificate files in /etc/pki/entitlement")
            else:
                raise FailException("Failed to check certificate files in /etc/pki/entitlement")
        else:
            if not (ret == 0 and "pem" in output and "key.pem" in output):
                logger.info("It is successful to check certificate files in /etc/pki/entitlement")
            else:
                raise FailException("Failed to check certificate files in /etc/pki/entitlement")

    def get_service_level_menu(self):
        cmd = "subscription-manager service-level --show"
        (result, output) = Command().run(cmd)
        if result == 0:
            if "Service level preference not set" in output:
                service_level_menu = "sl-notset-menu"
            elif "Current service level:" in output:
                service_level_menu = output.split(":")[1].strip().lower() + "-menu"
            logger.info("It's successful to get current service level menu by cmd: %s." % service_level_menu)
            return service_level_menu
        else:
            raise FailException("Test Failed - Failed to get current service level by cmd.")

    def set_service_level(self, servicelevel):
        cmd = "subscription-manager service-level --set=%s" % servicelevel
        (ret, output) = Command().run(cmd)
        if ret == 0 and "Service level set to: %s" % servicelevel in output:
            logger.info("It's successful to set service level %s." % servicelevel)
        else:
            raise FailException("Test Failed - Failed to set service level %s." % servicelevel)

    def sub_listinstalledpools(self):
        cmd = "subscription-manager list --installed"
        (ret, output) = Command().run(cmd)
        if ret == 0:
            logger.info("The right installed pools are listed successfully.")
            pool_list = self.__parse_listavailable_output(output)
            return pool_list
        else:
            raise FailException("Test Failed - Failed to list installed pools.")

    def sub_listconsumedpools(self):
        cmd = "subscription-manager list --consumed"
        (ret, output) = Command().run(cmd)
        if ret == 0:
            logger.info("The right consumed pools are listed successfully.")
            pool_list = self.__parse_listavailable_output(output)
            return pool_list
        else:
            raise FailException("Test Failed - Failed to list consumed pools.")

    def sub_listavailpools(self, productid):
        cmd = "subscription-manager list --available"
        (ret, output) = Command().run(cmd)
        if ret == 0:
            if "no available subscription pools to list" not in output.lower():
                if productid in output:
                    logger.info("The right available pools are listed successfully.")
                    pool_list = self.__parse_listavailable_output(output)
                    return pool_list
                else:
                    raise FailException("Not the right available pools are listed!")
            else:
                logger.info("There is no Available subscription pools to list!")
                return None
        else:
            raise FailException("Test Failed - Failed to list available pools.")

    def __parse_listavailable_output(self, output):
        datalines = output.splitlines()
        data_list = []
        # split output into segmentations for each pool
        data_segs = []
        segs = []
        tmpline = ""
        for line in datalines:
            if ("Product Name:" in line) or ("ProductName" in line) or ("Subscription Name" in line):
                tmpline = line
            elif line and ":" not in line:
                tmpline = tmpline + ' ' + line.strip()
            elif line and ":" in line:
                segs.append(tmpline)
                tmpline = line
            if ("Machine Type:" in line) or ("MachineType:" in line) or ("System Type:" in line) or ("SystemType:" in line):
                segs.append(tmpline)
                data_segs.append(segs)
                segs = []
        for seg in data_segs:
            data_dict = {}
            for item in seg:
                keyitem = item.split(":")[0].replace(' ', '')
                valueitem = item.split(":")[1].strip()
                data_dict[keyitem] = valueitem
            data_list.append(data_dict)
        return data_list

    def remove_proxy(self):
        cmd = "sed -i -e 's/proxy_hostname =.*/proxy_hostname =/g' -e 's/proxy_port =.*/proxy_port =/g' /etc/rhsm/rhsm.conf"
        (ret, output) = Command().run(cmd)
        if ret == 0:
            logger.info("It's successful to remove proxy.")
        else:
            raise FailException("Test Failed - Failed to Remove proxy")

    def get_available_release(self):
        cmd = "subscription-manager release --list"
        (ret, output) = Command().run(cmd)
        if ret == 0:
            logger.info("It's successful to list available releases.")
            return output.strip().split('\n')[3:]
        else:
            raise FailException("Test Failed - Failed to list available releases.")

    def open_subscription_manager_by_cmd(self):
        cmd = "subscription-manager-gui &"
        (ret, output) = Command().run(cmd)
        if ret == 0:
            logger.info("It's successful to run subscription-manager-gui the first time.")
        else:
            raise FailException("Test Failed - Failed to run subscription-manager-gui the first time")

    def open_subscription_manager_twice(self):
        cmd = "subscription-manager-gui"
        (ret, output) = Command().run(cmd)
        if ret == 0 and "subscription-manager-gui is already running" in output:
            logger.info("It's successful to check message when run_subscription_manager_gui_twice.")
        else:
            raise FailException("Test Failed - Failed to check message when run_subscription_manager_gui_twice")

    def set_hostname(self, hostname):
        cmd = "hostname %s" % hostname
        (ret, output) = Command().run(cmd)
        if ret == 0:
            logger.info("It's successful to restore hostname to %s." % hostname)
        else:
            raise FailException("Test Failed - Failed to restore hostname to %s." % hostname)

    def get_hostname(self):
        cmd = "hostname"
        (ret, output) = Command().run(cmd)
        if ret == 0:
            logger.info("It's successful to get system hostname")
            return output
        else:
            raise FailException("Test Failed - Failed to get system hostname")

    def generate_cert(self):
        cmd = "cat /etc/pki/entitlement/* > /tmp/test.pem"
        (ret, output) = Command().run(cmd)
        if ret == 0:
            logger.info("It's successful to generate entitlement cert")
            return "/tmp/test.pem"
        else :
            raise FailException("Test Failed - error happened when generate entitlement certs")

    def check_entitlement_cert(self, productid):
        if self.check_rct() :
            cmd = "for i in $(ls /etc/pki/entitlement/ | grep -v key.pem); do rct cat-cert /etc/pki/entitlement/$i; done | grep %s" % (productid)
        else:
            cmd = "for i in $(ls /etc/pki/entitlement/ | grep -v key.pem); do openssl x509 -text -noout -in /etc/pki/entitlement/$i; done | grep %s" % (productid)
        (ret, output) = Command().run(cmd)
        if ret == 0:
            if productid in output:
                logger.info("It's successful to check entitlement certificates.")
            else:
                raise FailException("Test Failed - The information shown entitlement certificates is not correct.")
        else:
            raise FailException("Test Failed - Failed to check entitlement certificates.")

    def check_rct(self):
        cmd = "rct cat-cert --help"
        (ret, output) = Command().run(cmd)
        if ret == 0:
            logger.info("rct cat-cert command can be used in the system")
            return True
        else:
            logger.info("rct cat-cert command can not be used in the system")
            return False


    def sub_unregister(self):
        cmd = "subscription-manager unregister"
        (ret, output) = Command().run(cmd)
        if ret == 0:
            if ("System has been unregistered." in output) or ("System has been un-registered." in output):
                logger.info("It's successful to unregister.")
            else:
                raise FailException("Test Failed - The information shown after unregistered is not correct.")
        else:
            raise FailException("Test Failed - Failed to unregister.")
