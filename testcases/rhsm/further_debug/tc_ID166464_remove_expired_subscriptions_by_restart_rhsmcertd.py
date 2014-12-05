from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException
import datetime
import time

class tc_ID166464_remove_expired_subscriptions_by_restart_rhsmcertd(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # register to server
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            # auto-attach
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # Check the subscription status
            sub_status = self.get_subscription_status()
            if sub_status == "True":
                logger.info("It's successful to check the subscription status is not expired")
            else:
                raise FailException("Test Failed - Failed to check the subscription status is not expired.")
            # set the system times later than 12 years.
            cmd = "date -d '+12 years'"
            specified_time = self.get_specified_time(cmd)
            cmd = "date -s '%s'" % (specified_time)
            self.set_system_time(cmd)

            # restart rhsmcertd service
            cmd = 'service rhsmcertd restart'
            self.runcmd(cmd, "restart rhsmcertd service")
#            logger.info('sleep 120 second for waiting rhsmcertd service...') 
#            time.sleep(120)

            # Check the subscription status
            sub_status = self.get_subscription_status()
            if sub_status == "False":
                logger.info("It's successful to check the subscription status is expired")
            else:
                raise FailException("Test Failed - Failed to check the subscription status is expired.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            cmd = "hwclock --hctosys"
            self.set_system_time(cmd)
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

    def get_specified_time(self, cmd):
        (ret, output) = self.runcmd(cmd, "get_specified_time")
        if ret == 0:
            logger.info("It's successful to get_specified_time")
            specified_time = output.strip()
            return specified_time
        else:
            raise FailException("Test Failed - Failed to get_specified_time.")

    def set_system_time(self, cmd):
        (ret, output) = self.runcmd(cmd, "set client time with specified time")
        if ret == 0:
            logger.info("It's successful to set/recover client time with specified time")
        else:
            raise FailException("Test Failed - Failed to set/recover client time with specified time.")

    def get_subscription_status(self):
        cmd = "subscription-manager list --consumed | grep Active"
        (ret, output) = self.runcmd(cmd, "get subscription status")
        if ret == 0:
            if "False" in output:
                logger.info("It's successful to get subscription status: the subscription is expired")
                return "False"
            elif "True" in output:
                logger.info("It's successful to get subscription status: the subscription is not expired")
                return "True"
            else:
                logger.info("nonsense status ")
                return "None"
        else:
            raise FailException("Test Failed - Failed to get subscription status.")

if __name__ == "__main__":
    unittest.main()
