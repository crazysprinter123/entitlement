from utils import *
from utils.configs import Configs
from utils.constants import RHSM_CONF
from utils.tools.shell.command import Command
from utils.exception.failexception import FailException

class RHSMConstants(object):
    sam_cons6 = {
            "username": "admin",
            "password": "admin",
            "baseurl": "https://samserv.redhat.com:443",
            "autosubprod": "Red Hat Enterprise Linux Server",
            "installedproductname": "Red Hat Enterprise Linux Server",
            "productid": "SYS0395",
            "pid": "69",
            "service_level": "PREMIUM",
            "pkgtoinstall": "zsh",
            "productrepo": "rhel-6-server-rpms",
            "betarepo": "rhel-6-server-beta-rpms",
            "servicelevel": "STANDARD",
            "releaselist": "6.1,6.2,6.3,6.4,6.5,6.6,6Server",
            }
    sam_cons7 = {
        "username": "admin",
        "password": "admin",
        "baseurl": "https://samserv.redhat.com:443",
        "autosubprod": "Red Hat Enterprise Linux Desktop",
        "installedproductname": "Red Hat Enterprise Linux Desktop",
        "productid": "SYS0395",
        "pid": "68",
        "service_level": "PREMIUM",
        "pkgtoinstall": "zsh",
        "productrepo": "rhel-6-desktop-rpms",
        "betarepo": "rhel-6-desktop-beta-rpms",
        "servicelevel": "STANDARD",
        "releaselist": "6.1,6.2,6.3,6.4,6Client",
        }
    stage_cons = {
            "username": "stage_test_12",
            "password": "redhat",
            "baseurl": "https://subscription.rhn.stage.redhat.com:443",
            "autosubprod": "Red Hat Enterprise Linux Server",
            "installedproductname": "Red Hat Enterprise Linux Server",
            "productid": "RH0103708",
            "pid": "69",
            "pkgtoinstall": "zsh",
            "productrepo": "rhel-6-server-rpms",
            "betarepo": "rhel-6-server-beta-rpms",
            "servicelevel": "PREMIUM",
            "releaselist": "6.1,6.2,6.3,6.4,6Server",
            }
    candlepin_cons = {
            "username": "qa@redhat.com",
            "password": "HWj8TE28Qi0eP2c",
            # please install a localcandlepin whose hostname is localcandlepin.redhat.com
            "baseurl": "https://localcandlepin.redhat.com:8443",
            }

    server = ""
    confs = None
    __instance = None
    samhostip = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(RHSMConstants, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if(self.__initialized): return
        self.__initialized = True
        self.confs = Configs(RHSM_CONF)
        self.server = self.confs._confs["server"]
        if self.server == "sam":
            self.configure_sam_host(self.confs._confs["samhostname"], self.confs._confs["samhostip"])
            self.samhostip = self.confs._confs["samhostip"]
        elif self.server == "stage":
            self.configure_stage_host(self.confs._confs["stage_name"])
        elif self.server == "candlepin":
            pass

    def configure_sam_host(self, samhostname, samhostip):
        ''' configure the host machine for sam '''
        if samhostname != None and samhostip != None:
            # add sam hostip and hostname in /etc/hosts
            cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (samhostname, samhostip, samhostname)
            ret, output = Command().run(cmd)
            if ret == 0:
                logger.info("Succeeded to configure /etc/hosts")
            else:
                raise FailException("Failed to configure /etc/hosts")
            # config hostname, prefix, port,   and repo_ca_crt by installing candlepin-cert
            cmd = "rpm -qa | grep candlepin-cert-consumer"
            ret, output = Command().run(cmd)
            if ret == 0:
                logger.info("candlepin-cert-consumer-%s-1.0-1.noarch has already exist, remove it first." % samhostname)
                cmd = "rpm -e candlepin-cert-consumer-%s-1.0-1.noarch" % samhostname
                ret, output = Command().run(cmd)
                if ret == 0:
                     logger.info("Succeeded to uninstall candlepin-cert-consumer-%s-1.0-1.noarch." % samhostname)
                else:
                    raise FailException("Failed to uninstall candlepin-cert-consumer-%s-1.0-1.noarch." % samhostname)
            cmd = "rpm -ivh http://%s/pub/candlepin-cert-consumer-%s-1.0-1.noarch.rpm" % (samhostip, samhostname)
            ret, output = Command().run(cmd)
            if ret == 0:
                logger.info("Succeeded to install candlepin cert and configure the system with sam configuration as %s." % samhostip)
            else:
                raise FailException("Failed to install candlepin cert and configure the system with sam configuration as %s." % samhostip)

    def configure_stage_host(self, stage_name):
        ''' configure the host machine for stage '''
        # configure /etc/rhsm/rhsm.conf to stage candlepin
        cmd = "sed -i -e 's/hostname = subscription.rhn.redhat.com/hostname = %s/g' /etc/rhsm/rhsm.conf" % stage_name
        ret, output = Command().run(cmd)
        if ret == 0:
            logger.info("Succeeded to configure rhsm.conf for stage")
        else:
            raise FailException("Failed to configure rhsm.conf for stage")

    def get_constant(self, name):
        if self.server == "sam":
            if self.get_os_serials() == "6":
                return self.sam_cons6[name]
            elif self.get_os_serials() == "7":
                return self.sam_cons7[name]
        elif self.server == "stage":
            return self.stage_cons[name]
        elif self.server == "candlepin":
            return self.candlepin_cons[name]

    def get_os_serials(self):
        cmd = "uname -r | awk -F \"el\" '{print substr($2,1,1)}'"
        (ret, output) = Command().run(cmd, comments=False)
        if ret == 0:
            return output.strip("\n").strip(" ")
            logger.info("It's successful to get system serials.")
        else:
            logger.info("It's failed to get system serials.")