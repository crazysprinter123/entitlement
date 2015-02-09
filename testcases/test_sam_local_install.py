from utils import *
from utils.installation.samlocalinstall import SAMLocalInstall
from utils.installation.samslaveinstall import SAMSlaveInstall

class Test_SAM_Local_Install(unittest.TestCase):


    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        SAMSlaveInstall().start()

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
