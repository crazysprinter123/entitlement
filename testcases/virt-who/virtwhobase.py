from utils import *
import time, random, pexpect
from utils.configs import Configs
from utils.tools.shell.command import Command
from utils.exception.failexception import FailException

class VIRTWHOBase(unittest.TestCase):
    # ========================================================
    #       0. Basic Functions
    # ========================================================
    commander = Command()