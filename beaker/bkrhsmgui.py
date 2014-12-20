import os, re
from utils import logger
from beaker.beakerbase import BeakerBase
from utils.tools.shell.command import Command
from utils.tools.shell.beakercmd import BeakerCMD
from utils.constants import RHSM_CONF, RHSM_JOB, PACKAGES, RHEL7_PACKAGES, GUI_PACKAGES

class BKRHSMGUI(BeakerBase):
    '''
    classdocs
    '''
    conf_file_name = RHSM_CONF

    def start(self, distro=None, sam_build=None, sam_server=None):
        if distro == None:
            distro = self.confs._confs["beakerdistro"]
        if sam_server == None:
            sam_server = self.confs._confs["samhostname"]
            sam_ip = self.confs._confs["samhostip"]
        else:
            sam_ip = sam_server

        beaker_command = BeakerCMD()

        job_xml = beaker_command.create_runtime_job(RHSM_JOB)
        beaker_command.set_beaker_distro_name(job_xml, distro)
        beaker_command.set_beaker_job_name(job_xml, "RHSM GUI testing on %s against %s" % (distro, sam_build))

        if beaker_command.get_rhel_version(distro) == 7:
            RHEL7_PACKAGES.extend(GUI_PACKAGES)
            beaker_command.set_packages(job_xml, RHEL7_PACKAGES)
        else:
            PACKAGES.extend(GUI_PACKAGES)
            beaker_command.set_packages(job_xml, PACKAGES)

        beaker_command.update_task(job_xml, "/distribution/entitlement-qa/Regression/rhsm", "/installation/entitlement-qa/Regression/rhsm-gui")
        beaker_command.update_job_param(job_xml, "/installation/entitlement-qa/Regression/rhsm-gui", "RUN_SERVER", "sam")
        beaker_command.update_job_param(job_xml, "/installation/entitlement-qa/Regression/rhsm-gui", "RUN_LEVEL", "rhsm_gui")
        beaker_command.update_job_param(job_xml, "/installation/entitlement-qa/Regression/rhsm-gui", "SAM_IP", sam_ip)
        beaker_command.update_job_param(job_xml, "/installation/entitlement-qa/Regression/rhsm-gui", "SAM_HOSTNAME", sam_server)

        job = beaker_command.job_submit(job_xml)

if __name__ == "__main__":
    BKRHSMGUI().start()
