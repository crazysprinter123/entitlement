from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID267323_access_candlepin_crl_when_system_expired_revoked(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # register to and auto-attach
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.register_and_autosubscribe(username, password, autosubprod)
            # get variables form ent_env
            repoid = RHSMConstants().get_constant("productrepo")
            pid = RHSMConstants().get_constant("pid")
            pkgtoinstall = RHSMConstants().get_constant("pkgtoinstall")
            # check repo exist
            if self.is_enabled_repo(repoid):
                # check package to be installed exist
                self.check_givenpkg_avail(repoid, pkgtoinstall)
                # install test-pkg
                self.install_givenpkg(pkgtoinstall)
            else:
                raise FailException("Test Failed - The product repoid is not exist.")
            # check the cert file exist.
            certfile = pid + ".pem"
            self.check_cert_file(certfile)
            # check productid cert
            self.sub_checkproductcert(pid)
            # uninstall test-pkg
            self.uninstall_givenpkg(pkgtoinstall)
            ####                    install the same package when system expired         ###
            # make the system expired
            self.set_system_date()
            # install test-pkg again
            self.install_givenpkg(pkgtoinstall)
            # restore the system time
            self.restore_system_time()
            ####                    install the same package when system expired         ###
            # unsubscribe all subscriptions
            self.sub_unsubscribe()
            # install test-pkg again
            self.install_givenpkg(pkgtoinstall)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_system_time()
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

    def register_and_autosubscribe(self, username, password, autosubprod):
        cmd = "subscription-manager register --username=%s --password=%s --auto-attach" % (username, password)
        (ret, output) = self.runcmd(cmd, "register_and_autosubscribe")
        if (ret == 0) and ("The system has been registered with ID:" in output) and (autosubprod in output) and ("Subscribed" in output):
            logger.info("It's successful to register and auto-attach")
        else:
            raise FailException("Test Failed - failed to register or auto-attach.")

    def is_enabled_repo(self, repoid):
        cmd = "yum repolist"
        (ret, output) = self.runcmd(cmd, "list enabled repos")
        if ret == 0 and "repolist:(\s+)0" in output:
            raise FailException("Test Failed - There is not enabled repo to list.")
        else:
            logger.info("It's successful to list enabled repos.")
        if repoid in output:
            return True
        else:
            return False

    def check_givenpkg_avail(self, repoid, testpkg):
        cmd = "repoquery -a --repoid=%s | grep %s" % (repoid, testpkg)
        (ret, output) = self.runcmd(cmd, "check package available")
        if ret == 0 and testpkg in output:
            logger.info("The package %s exists." % (testpkg))
        else : 
            raise FailException("Test Failed - The package %s does not exist." % (testpkg))

    def install_givenpkg(self, testpkg):
        cmd = "yum install -y %s" % (testpkg)
        (ret, output) = self.runcmd(cmd, "install selected package %s" % testpkg)
        if ret == 0 and "Complete!" in output and "Error" not in output:
            logger.info("The package %s is installed successfully." % (testpkg))
        elif ret == 1:
            if("The subscription for following product(s) has expired" in output):
                logger.info("It's successful to verify that system should not be able to access CDN bits through thumbslug  proxy when the system is expired.")
            else:
                logger.info("It's successful to verify that system should not be able to access CDN bits through thumbslug  proxy when the system is not attach subscriptions")
        else:
            raise FailException("Test Failed - The package %s is failed to install." % (testpkg))

    def uninstall_givenpkg(self, testpkg):
        cmd = "rpm -qa | grep %s" % (testpkg)
        (ret, output) = self.runcmd(cmd, "check package %s" % testpkg)
        if ret == 1:
            logger.info("There is no need to remove package")
        else:
            cmd = "yum remove -y %s" % (testpkg)
            (ret, output) = self.runcmd(cmd, "remove select package %s" % testpkg)
            if ret == 0 and "Complete!" in output and "Removed" in output:
                logger.info("The package %s is uninstalled successfully." % (testpkg))
            elif ret == 0 and "No package %s available" % testpkg in output:
                logger.info("The package %s is not installed at all" % (testpkg))
            else:
                raise FailException("Test Failed - The package %s is failed to uninstall." % (testpkg))
	
    def check_cert_file(self, certfile):
        cmd = "ls -l /etc/pki/product/%s" % certfile
        (ret, output) = self.runcmd(cmd, "check the product cert file exists")
        if ret == 0 :
            logger.info("It's successful to check product cert file exists.")            
        else:
            raise FailException("Test Failed - it's failed to check product cert file exists.")

    def set_system_date(self):
        cmd = "date -s 20200101"
        (ret, output) = self.runcmd(cmd, "set_system_date")
        if (ret == 0):
            logger.info("It's successful to set the system date to be expired")
        else:
            raise FailException("Test Failed - failed to set the system date to be expired.")

    def restore_system_time(self):
        cmd = "hwclock --hctosys"
        (ret, output) = self.runcmd(cmd, "restore system time")
        if ret == 0:
            logger.info("It's successful to restore the system time")
        else:
            raise FailException("Test Failed - Failed to restore system time.")

if __name__ == "__main__":
    unittest.main()
