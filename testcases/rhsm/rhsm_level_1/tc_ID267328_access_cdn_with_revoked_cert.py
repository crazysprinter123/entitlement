from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID267328_access_cdn_with_revoked_cert(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            autosubprod = RHSMConstants().get_constant("autosubprod")
            pkgtoinstall = RHSMConstants().get_constant("pkgtoinstall")
            #register to and auto-attach
            self.register_and_autosubscribe(username, password, autosubprod)
            # unregister
            self.sub_unregister()
            #install a pkg
            cmd = "yum install -y %s" % (pkgtoinstall)
            (ret, output) = self.runcmd(cmd, "install selected package %s" % pkgtoinstall)
            if ret == 1 and "No package %s available."%pkgtoinstall in output:
                logger.info("It's successful to verify that system cannot access CDN contents through thumbslug with revoked cert")
            else:
                raise FailException("Test Failed - failed to verify that system cannot access CDN contents through thumbslug with revoked cert")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

    def register_and_autosubscribe(self, username, password, autosubprod):
        cmd = "subscription-manager register --username=%s --password=%s --auto-attach"%(username, password)
        (ret, output) = self.runcmd(cmd, "register_and_autosubscribe")
        if (ret == 0) and ("The system has been registered with ID:" in output) and (autosubprod in output) and ("Subscribed" in output):
            logger.info("It's successful to register and auto-attach")
        else:
            raise FailException("Test Failed - failed to register or auto-attach.")

if __name__ == "__main__":
    unittest.main()