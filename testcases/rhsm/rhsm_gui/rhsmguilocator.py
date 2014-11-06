from utils import *
from utils.tools.shell.command import Command

class RHSMGuiLocator(object):

    # ========================================================
    #       RHSM GUI test elements
    # ========================================================
    element_locators = {
    ######## Window Elements ########
    'main-window-5':                         'Subscription Manager',
    'main-window-6':                         'frmSubscriptionManager',
    'register-dialog-5':                     'register_dialog',
    'register-dialog-6':                     'dlgregister_dialog',
    'subscribe-dialog-5':                    'Subscribe System',
    'subscribe-dialog-6':                    'frmSubscribeSystem',
    'import-cert-dialog':                    'dlgImportCertificates',
    'select-file-dialog':                    'dlgSelectAFile',
    'system-facts-dialog':                   'dlgfacts_dialog',
    'search-dialog':                         'frmSearching',
    'proxy-configuration-dialog':            'dlgProxyConfiguration',
    'information-dialog':                    'dlgInformation',
    'question-dialog':                       'dlgQuestion',
    'error-dialog':                          'dlgError',
    'system-preferences-dialog':             'dlgSystemPreferences',
    'subscription-manager-manual-window':    'frmSubscriptionManagerManual',
    'onlinedocumentation-window':            'frmRedHatSubscriptionManagement-RedHatCustomerPortal-MozillaFireFox',
    'security-warning-dialog':               'dlgSecurityWarning',
    'about-subscription-manager-dialog':     'dlgAboutSubscriptionManager',
    'rhsm-notification-dialog':              'dlgNotification',
    'filter-options-window':                 'frmFilterOptions',
    'error-cert-dialog':                     'dlgError',
    'sm-gui-warning-classic-dialog':         'dlgWarning',
    'firstboot-main-window':                 'frm0',
    'firstboot-wng-dialog':                  'dlgWarning',
    'firstboot-err-dialog':                  'dlgError',
    'classic-main-window':                   'frmSystemRegistration',
    'classic-confirm-osrelease-window':      'dlgConfirmoperationsystemreleaseselection',
    'classic-updates-configured-window':     'frmUpdatesConfigured',

    ######## Tab Elements ########
    'all-tabs':                              'ptl0',
    'my-installed-software-5':               'My Installed Products',
    'my-installed-software-6':               'ptabMyInstalledSoftware',
    'my-subscriptions-5':                    'My Subscriptions',
    'my-subscriptions-6':                    'ptabMySubscriptions',
    'all-available-subscriptions-5':         'All Available Subscriptions',
    'all-available-subscriptions-6':         'ptabAllAvailableSubscriptions',
    'my-installed-software-6':               'ptabMyInstalledProducts',

    ######## Button Elements ########
    # button in main window
    'register-button-5':                     'Register System',
    'register-button-6':                     'btnRegisterSystem',
    'unregister-button-5':                   'btnUnregister',
    'unregister-button-6':                   'btnUnregister',
    'auto-subscribe-button-5':               'Auto-subscribe',
    'auto-subscribe-button-6':               'btnAuto-attach',
    'unsubscribe-button':                    'btnUnsubscribe',
    # button in register dialog
    'dialog-register-button-5':              'register_button',
    'dialog-register-button-6':              'btnregisterbutton',
    'dialog-cancle-button-5':                'cancel_button',
    'dialog-cancle-button-6':              'btncancelbutton',
    # button in subscribe dialog
    'dialog-subscribe-button-5':             'btnSubscribe',
    'dialog-subscribe-button-6':             'btnSubscribe',
    'dialog-back-button':                    'btnBack',
    # button in register dialog
    'configure-proxy-button-6':              'btnproxybutton',
    # button in import-certificate-dialog
    'ok-button-6':                           'btnOK',
    'import-file-button':                    'btnImport',
    'type-pem-name-button-6':                'tbtnTypefilename',
    'certificate-location-button-6':         'btn(None)',
    # button in select-file-dialog
    'type-file-name-button-6':               'tbtnTypeafilename',
    'open-file-button':                      'btnOpen',
    'proxy-close-button-6':                  'btnCloseButton',
    'yes-button-6':                          'btnYes',
    # button in system-preferences-dialog
    'close-button-6':                        'btnClose',
    # button in firstboot gui
    'firstboot-fwd-button-6':                'btnForward',
    'firstboot-agr-button-6':                'rbtnYes,IagreetotheLicenseAgreement',
    'firstboot-yes-button-6':                'btnYes',
    'firstboot-ok-button-6':                 'btnOK',
    'firstboot-finish-button-6':             'btnFinish',
    'firstboot-register-now-button-6':       'rbtnYes,I\'dliketoregisternow',
    'firstboot-register-rhsm-button-6':      'rbtnRedHatSubscriptionManagement',
    'firstboot-classic-select-button-6':     'rbtnRedHatNetwork(RHN)Classic',
    # button in rhn_classic gui
    'classic-forward-button-6':              'btnForward',
    'classic-confirm-osrelease-yes-button-6':            'btnYes,Continue',
    'classic-updates-configured-finish-button-6':        'btnFinish',
    # else
    'remove-subscriptions-button-6':     'btnRemove',
    'system-preferences-button-6':       'btnSystemPreferences',
    'proxy-configuration-button-6':      'btnProxyConfiguration',
    'view-system-facts-button-6':        'btnViewSystemFacts',
    'import-certificate-button-6':       'btnImportCertificate',
    'help-button-6':                     'btnHelp',
    'update-button-6':                   'btnSearch',
    'filters-button-6':                  'btnFilters',

    ######## Table Elements ########
    'my-product-table-5':                    'Installed View',
    'my-product-table-6':                    'tblBundledProductsTable',
    'my-subscription-table-5':               'My Subscriptions View',
    'my-subscription-table-6':               'ttblMySubscriptionsView',
    'all-subscription-table-5':              'AllSubscriptionsView',
    'all-subscription-table-6':              'ttblAllSubscriptionsView',
    'all-product-table-5':                   'tblAllAvailableBundledProductTable',
    'all-product-table-6':                   'tblAllAvailableBundledProductTable',
    'installed-product-table-5':             'tblInstalledView',
    'installed-product-table-6':             'tblInstalledView',
    'facts-view-table-6':                    'ttblfactsview',
    'orgs-view-table-6':                     'tblownertreeview',

     ######## Text Elements ########
    'login-text-5':                          'txtaccountlogin',
    'login-text-6':                          'account_login',
    'password-text-5':                       'txtaccountpassword',
    'password-text-6':                       'account_password',
    # text in select-file-dialog
    'location-text-6':                       'txtLocation',
    'proxy-location-text-6':                 'txtProxyLocation',
    'server-url-text-6':                     'txtserverentry',
    # firstboot
    'firstboot-login-text-6':                'txtaccountlogin',
    'firstboot-password-text-6':             'txtaccountpassword',
    # rhn_classic
    'classic-login-text-6':                  'txtLogin',
    'classic-password-text-6':               'txtPassword',
    'classic-set-systemname-text-6':         'txtSystemName',

    ######## Menu Elements ########
    # under System menu
    'system-menu-6':                         'mnuSystem',
    'register-menu-6':                       'mnuRegister',
    'unregister-menu-6':                     'mnuUnregister',
    'importcert-menu-6':                     'mnuImportCert',
    'viewsystemfacts-menu-6':                'mnuViewSystemFacts',
    'configureproxy-menu-6':                 'mnuConfigureProxy',
    'preferences-menu-6':                    'mnuPreferences',
    'quit-menu-6':                           'mnuQuit',
    # under Help menu
    'help-menu-6':                           'mnuHelp',
    'gettingstarted-menu-6':                 'mnuGettingStarted',
    'onlinedocumentation-menu-6':            'mnuOnlineDocumentation',
    'about-menu-6':                          'mnuAbout',
    # service level menu
    'sl-notset-menu':                        'mnuNotSet1',
    'none-menu':                             'mnuNone',
    'premium-menu':                          'mnuPremium',
    'standard-menu':                         'mnuStandard',
    'self-support-menu':                     'mnuSelf-Support',
    'layered-menu':                          'mnuLayered',

    # release version menu
    'rv-notset-menu':                       'mnuNotSet',
    '6.1-menu':                             'mnu61',
    '6.2-menu':                             'mnu62',
    '6.3-menu':                             'mnu63',
    '6.4-menu':                             'mnu64',
    '6.5-menu':                             'mnu65',
    '6server-menu':                         'mnu6Server',
    # import cert
    'ImportCertificate-menu-6':              'mnuImportCert',

    ######## Checkbox Element ########
    'manual-attach-checkbox-6':              'chkautobind',
    'proxy-checkbox-6':                      'chkProxyCheckbox',
    'match-system-checkbox-6':               'chkMatchSystem',
    'match-installed-checkbox-6':            'chkMatchInstalled',
    'do-not-overlap-checkbox-6':             'chkDoNotOverlap',
    # ##firstboot checkbox for RHEL6
    'firstboot-manual-checkbox-6':           'chkautobind',
    'firstboot_activationkey-checkbox-6':    'chkIwilluseanActivationKey',

    ######## Label Element ########
    'import-cert-success-label-6':               'lblCertificateimportwassuccessful',
    'register-error-label-6':                    'lblUnabletoregisterthesystemInvalidusernameorpasswordTocreatealogin,pleasevisithttps//wwwredhatcom/wapps/ugc/registerhtmlPleasesee/var/log/rhsm/rhsmlogformoreinformation',
    'search-subscriptions-hint-label-6':         'lbl2applied',
    'error-user-label-6':                        'lblUserusertestisnotabletoregisterwithanyorgs',
    'warning-classic-already-label-6':           'lblWARNINGThissystemhasalreadybeenregisteredwithRedHatusingRHNClassicThetoolyouareusingisattemptingtore-registerusingRedHatSubscriptionManagementtechnologyRedHatrecommendsthatcustomersonlyregisteronceTolearnhowtounregisterfromeitherservicepleaseconsultthisKnowledgeBaseArticlehttps//accessredhatcom/kb/docs/DOC-45563',
    # firstboot label
    'firstboot-registeration-warning-label-6':   'lblYoursystemwasregisteredforupdatesduringinstallation',
    'firstboot_creat_user-label-6':              'lblYoumustcreatea\'username\'forregular(non-administrative)useofyoursystemTocreateasystem\'username\',pleaseprovidetheinformationrequestedbelow',
    'firstboot-skip-auto-label-6':               'lblYouhaveoptedtoskipauto-attach',
    'firstboot-classic-reviewsubscription-label-6':    'lblReviewSubscription',
    'firstboot-classic-finishupdate-label-6':          'lblFinishUpdatesSetup',
    # rhn_classic label
    'classic-software-update-label-6':           'lblSetUpSoftwareUpdates',
    'classic-choose-service-label-6':            'lblChooseService',
    'classic-redhat-account-label-6':            'lblRedHatAccount',
    'classic-OS-realeaseversion-label-6':        'lblOperatingSystemReleaseVersion',
    'classic-create-profile-label-6':            'lblCreateProfile',
    'classic-review-subscription-label-6':       'lblReviewSubscription',

    ######## Combobox Element ########
    'service-level-combobox':                    'cboslaselectioncombobox',
    'release-version-combobox':                  'cboreleaseselectioncombobox',

#     'service-level-notset-combobox-6':           'cboNotSet',
#     'service-level-premium-combobox-6':          'cboPremium',
#     'service-level-none-combobox-6':             'cboNone',
#     'release-version-combobox-6':                'cbo1',
#     'release-version-6server-combobox-6':        'cbo6Server',

    ######## Other Element ########
    'register-progressbar-6':                    'pbarregisterprogressbar',
    }

    os_serial = ""
    def __init__(self):
        if self.os_serial == "":
            self.os_serial = self.get_os_serials()

    def get_locator(self, name):
        if name + "-" + self.os_serial in self.element_locators.keys():
            return self.element_locators[name + "-" + self.os_serial]
        else:
            return self.element_locators[name]

    def get_os_serials(self):
        # close subscription-manager-gui
        cmd = "uname -r | awk -F \"el\" '{print substr($2,1,1)}'"
        (ret, output) = Command().run(cmd, comments=False)
        if ret == 0:
            return output.strip("\n").strip(" ")
            logger.info("It's successful to get system serials.")
        else:
            logger.info("It's failed to get system serials.")
