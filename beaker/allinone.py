from beaker.bksaminstall import BKSAMInstall
from utils.installation.vwkscreate import VWKSCreate
from beaker.bkvirtwhokvm import BKvirtwhoKVM
from beaker.bkvirtwhoesx import BKvirtwhoESX
from beaker.bkvirtwhoxenfv import BKvirtwhoXENFV
from beaker.bkvirtwhoxenpv import BKvirtwhoXENPV

class AllInOne():

    def start(self):
        new_rhel, build = VWKSCreate().start()
        new_sam, sam_build, sam_server = BKSAMInstall().start()
        if new_rhel == 0 or new_sam == 0:
            # if no sam new build, install the latest one
            if new_sam == -1:
                new_sam, sam_build, sam_server = BKSAMInstall().start(sam_build)
            BKvirtwhoKVM().start(build, sam_build, sam_server)
            BKvirtwhoESX().start(build, sam_build, sam_server)
            BKvirtwhoXENFV().start(build, sam_build, sam_server)
            BKvirtwhoXENPV().start(build, sam_build, sam_server)

if __name__ == "__main__":
    AllInOne().start()
