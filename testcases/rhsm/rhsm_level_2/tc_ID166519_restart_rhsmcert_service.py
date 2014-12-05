from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID166519_restart_rhsmcert_service(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            #set healfrequency = 1
            self.sub_set_healfrequency(1)
            #1. Unsubscribe the subscription
            self.sub_unsubscribe()
            #2. refresh the local data
            cmd='subscription-manager refresh'
            (ret,output)=self.runcmd(cmd, "reflash")
            if ret == 0  and 'All local data refreshed' in output:    
                logger.info("It's successful to do refresh local data")
            else:
                raise FailException("Test Failed - Failed to do refresh.")
            #3. Restart the rhsmcertd service
            cmd='service rhsmcertd restart'
            self.runcmd(cmd, "restart rhsmcertd")
            #4. List the consumed
            cmd='subscription-manager refresh'
            (ret,output)=self.runcmd(,cmd,"refresh rhsmcertd")
            logger.info("Waiting 90 seconds for rhsmcertd service to take effect...")
            time.sleep(90)
            if self.sub_isconsumed(autosubprod):
                logger.info("It's successful to list consumed.")
            else:
                raise FailException("Test Failed - Failed to list consumed.")

    except Exception, e:
        logger.error(str(e))
        raise FailException("Test Failed - error happened when do restart rhsmcertd service :"+str(e))

    finally:
        sub_set_healfrequency(1440)
        cmd='service rhsmcertd restart'
        self.runcmd(cmd, "restart rhsmcertd")
        self.sub_unregister()
        logger.info("=========== End of Running Test Case: %s ==========="%__name__)

def sub_set_healfrequency(frtime):
    
    cmd = "subscription-manager config --rhsmcertd.healfrequency=%s" %frtime
    cmd510 = "subscription-manager config --rhsmcertd.autoattachinterval=%s" %frtime
    (ret, output) = self.runcmd(cmd, "set healfrequency")

    if ret == 0:
        logger.info("It successful to set healfrequency")
    else:
        (ret, output) = self.runcmd(cmd510, "set autoattachinterval")
        if ret == 0:
            logger.info("It successful to set autoattachinterval")
        else:
            logger.error("Test Failed - Failed to set healfrequency or autoattachinterval.")
