from beaker.bkrhsm import BKRHSMLEVEL1, BKRHSMLEVEL2
from beaker.bkrhsmstage import BKRHSMSTAGELEVEL1, BKRHSMSTAGELEVEL2
from beaker.bkrhsmgui import BKRHSMGUI
from beaker.bksaminstall import BKSAMInstall
from utils.installation.vwkscreate import VWKSCreate
from beaker.bkvirtwhokvm import BKvirtwhoKVM
from beaker.bkvirtwhoesx import BKvirtwhoESX
from beaker.bkvirtwhoxenfv import BKvirtwhoXENFV
from beaker.bkvirtwhoxenpv import BKvirtwhoXENPV
from utils import *
from utils.constants import RUNTIME_PATH

class AllInOne():

    def start(self):
        new_rhel, build = VWKSCreate().start()
        new_sam, sam_build, sam_server = BKSAMInstall().start()
        if new_rhel == 0 or new_sam == 0:
            # run stage testing only new rhel comes
            if new_rhel == 0:
                BKRHSMSTAGELEVEL1().start(build)
            # if no sam new build, install the latest one
            if new_sam == -1:
                new_sam, sam_build, sam_server = BKSAMInstall().start(sam_build)
            BKRHSMLEVEL1().start(build, sam_build, sam_server)
            BKRHSMLEVEL2().start(build, sam_build, sam_server)
            BKRHSMGUI().start(build, sam_build, sam_server)
            BKvirtwhoKVM().start(build, sam_build, sam_server)
            BKvirtwhoESX().start(build, sam_build, sam_server)
            BKvirtwhoXENFV().start(build, sam_build, sam_server)
            BKvirtwhoXENPV().start(build, sam_build, sam_server)
            self.set_mail_trigger("true")
        else:
            self.set_mail_trigger("false")

    def set_mail_trigger(self, triggered):
        if not os.path.exists(RUNTIME_PATH):
            os.makedirs(RUNTIME_PATH)
        trigger_file_name = "mail_trigger"
        trigger_file = os.path.join(RUNTIME_PATH, trigger_file_name)
        fileHandler = os.open(trigger_file, os.O_RDWR | os.O_TRUNC | os.O_CREAT)
        try:
            os.write(fileHandler, triggered)
        finally:
            os.close(fileHandler)

if __name__ == "__main__":
    AllInOne().start()
#     AllInOne().set_mail_trigger("true")
