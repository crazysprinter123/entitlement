import os, re
from utils import logger
from beaker.beakerbase import BeakerBase
from utils.tools.shell.command import Command
from utils.tools.shell.beakercmd import BeakerCMD
from utils.constants import RHSM_GUI_CONF, RHSM_GUI_JOB

class BKRHSMInstall(BeakerBase):
    '''
    classdocs
    '''
    conf_file_name = RHSM_GUI_CONF

    def start(self, distro=None, sam_build=None, sam_server=None):
        if distro == None:
            distro = self.confs._confs["beakerdistro"]
        if sam_server == None:
            sam_server = self.confs._confs["samhostname"]
            sam_ip = self.confs._confs["samhostip"]
        else:
            sam_ip = sam_server

        beaker_command = BeakerCMD()

        job_xml = beaker_command.create_runtime_job(RHSM_GUI_JOB)
        beaker_command.set_beaker_distro_name(job_xml, distro)
        beaker_command.set_beaker_job_name(job_xml, "RHSM GUI test on %s against %s" % (distro, sam_build))

#         if beaker_command.get_rhel_version(distro) == 5:
#             RHEL5_PACKAGES.append("@kvm")
#             beaker_command.set_packages(job_xml, RHEL5_PACKAGES)
#             beaker_command.set_beaker_distro_variant(job_xml, "")
#         else:
#             beaker_command.set_packages(job_xml, PACKAGES)

        job = beaker_command.job_submit(job_xml)
        rhsm_server = beaker_command.check_job_finished(job)
        # begin running gui automation ...
        cmd = "vncviewer %s:1" % rhsm_server
        Command.run(cmd)
        bk_commander = Command(rhsm_server, "root", "xxoo2014")
        cmd = "cd /root/entitlement; export PYTHONPATH=$PYTHONPATH:$/root/entitlement; python testcases/test_rhsm_gui.py"
        bk_commander.run(cmd)
#         os.environ["LDTP_SERVER_ADDR"] = rhsm_server
#         from testcases import test_rhsm_gui

if __name__ == "__main__":
    BKRHSMInstall().start()
