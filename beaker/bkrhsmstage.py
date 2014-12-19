import os, re
from utils import logger
from beaker.beakerbase import BeakerBase
from utils.tools.shell.command import Command
from utils.tools.shell.beakercmd import BeakerCMD
from utils.constants import RHSM_CONF, RHSM_JOB, RHEL7_PACKAGES, PACKAGES

class BKRHSMSTAGE(BeakerBase):
    '''
    classdocs
    '''
    conf_file_name = RHSM_CONF

    def start(self, distro=None, run_level="rhsm_level_1"):
        if distro == None:
            distro = self.confs._confs["beakerdistro"]

        beaker_command = BeakerCMD()

        job_xml = beaker_command.create_runtime_job(RHSM_JOB)
        beaker_command.set_beaker_distro_name(job_xml, distro)
        beaker_command.set_beaker_job_name(job_xml, "RHSM testing(%s) on %s against Stage Candlepin" % (run_level, distro))

        if beaker_command.get_rhel_version(distro) == 7:
            beaker_command.set_packages(job_xml, RHEL7_PACKAGES)
        else:
            beaker_command.set_packages(job_xml, PACKAGES)
        beaker_command.update_job_param(job_xml, "/distribution/entitlement-qa/Regression/rhsm", "RUN_SERVER", "stage")
        beaker_command.update_job_param(job_xml, "/distribution/entitlement-qa/Regression/rhsm", "RUN_LEVEL", run_level)
        job = beaker_command.job_submit(job_xml)

class BKRHSMSTAGELEVEL1(BKRHSMSTAGE):
    def start(self, distro=None):
        BKRHSMSTAGE().start(distro, run_level="rhsm_level_1")

class BKRHSMSTAGELEVEL2(BKRHSMSTAGE):
    def start(self, distro=None):
        BKRHSMSTAGE().start(distro, run_level="rhsm_level_2")

if __name__ == "__main__":
    BKRHSMSTAGE().start()
