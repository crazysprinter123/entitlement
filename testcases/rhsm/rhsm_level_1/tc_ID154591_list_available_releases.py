from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID154591_list_available_releases(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        #register to server
        username=RHSMConstants().get_constant("username")
        password=RHSMConstants().get_constant("password")
        self.sub_register(username,password)

        try:
            #auto subscribe to a pool
            autosubprod=RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)#get env variables
             #list available releases
		guestname=params.get("guest_name")
		currentversion=eu().sub_getcurrentversion(session,guestname)
		cmd="subscription-manager release --list"
		(ret,output)=eu().runcmd(session,cmd,"list available releases")
		

	        if ret == 0 and currentversion in output:      
           		logging.info("It's successful to list available releases.")	
                else:
        	        raise error.TestFail("Test Failed - Failed to list available releases.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do list available releases:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
