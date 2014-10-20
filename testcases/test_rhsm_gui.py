from utils import *
from testcases.rhsmgui import *

class Test_RHSM_GUI(unittest.TestCase):
 
    def setUp(self):
        pass
 
    def tearDown(self):
        pass
 
    def testAll(self):
        return self.regressionTest()
 
    def regressionTest(self):
        path = os.path.abspath(os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "testcases/rhsmgui/")))
        files = os.listdir(path)
        files.sort()
        case = re.compile("^tc_ID.*py$", re.IGNORECASE)
        files = filter(case.search, files)
        filenameToModuleName = lambda f: os.path.splitext(f)[0]
        moduleNames = map(filenameToModuleName, files)
        sys.path.append(path)
        modules = map(__import__, moduleNames)
        load = unittest.defaultTestLoader.loadTestsFromModule
        return unittest.TestSuite(map(load, modules))
#         sys.path.append(path)
#         for testcase in moduleNames:
#             obj = __import__(testcase)
#             self.assertEqual(getattr(getattr(obj, testcase)(), "run")(), 0, "run test case")

def get_all_cases():
    path = os.path.abspath(os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "testcases/rhsmgui/")))
    files = os.listdir(path)
    files.sort()
    case = re.compile("^tc_ID.*py$", re.IGNORECASE)
    files = filter(case.search, files)
    print files
    return files

def suite():
    suite = unittest.TestSuite()
    path = os.path.abspath(os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "testcases/rhsmgui/")))
    files = os.listdir(path)
    files.sort()
    case = re.compile("^tc_ID.*py$", re.IGNORECASE)
    files = filter(case.search, files)
    filenameToModuleName = lambda f: os.path.splitext(f)[0]
    moduleNames = map(filenameToModuleName, files)
    sys.path.append(path)
    modules = map(__import__, moduleNames)
    load = unittest.defaultTestLoader.loadTestsFromModule
    return unittest.TestSuite(map(load, modules))

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
#     get_all_cases()
