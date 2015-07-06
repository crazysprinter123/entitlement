##############################################################################
## Test Description
##############################################################################
"""
The object list for test 190920 is buggy and therefore, in order to run the test
python needs to be restarted.  This code handles that.
"""
##############################################################################
from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException
import ldtp

def main():
    print ldtp.getobjectlist("frmSubscriptionManager") 
    if not(RHSMGuiBase.check_object_exist('main-window','nosubscriptions-in-filter-label')):
        raise FailException("Can't find the no-subscriptions text!")


if __name__ == "__main__":
    main()