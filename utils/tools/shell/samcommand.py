'''
commands run on sam server
'''
import os
from utils import logger
from utils.tools.shell.command import Command

# manifest_name = "sam_install_manifest.zip"
# sam_manifest = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, "data/manifest/%s" % manifest_name))

class SAMCommand(Command):

    def install_sam(self, compose):
        self.__stop_iptables()
        self.__set_selinux()
        self.__set_hosts_file()
        self.__set_hostname()
        self.__auto_subscribe()
        self.__add_sam_repo(compose)
        self.__install_katello()
        self.__deploy_sam()
        self.__import_manifest()

    def __stop_iptables(self):
        cmd = "service iptables stop"
        self.run(cmd)

    def __set_selinux(self):
        cmd = "setenforce 0"
        self.run(cmd)
        cmd = "sed -i -e 's/SELINUX=.*/SELINUX=%s/g' /etc/sysconfig/selinux" % ("permissive")
        self.run(cmd)

    def __set_hosts_file(self):
        cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (self.remote_ip, self.remote_ip, "samserv.redhat.com")
        self.run(cmd)

    def __set_hostname(self):
        cmd = "hostname samserv.redhat.com"
        self.run(cmd)
        cmd = "sed -i '/HOSTNAME=/d' /etc/sysconfig/network; echo 'HOSTNAME=%s' >> /etc/sysconfig/network" % ("samserv.redhat.com")
        self.run(cmd)

    def __auto_subscribe(self):
        cmd = "subscription-manager register --username=qa@redhat.com --password=AC7YeKvJ7j8ZPu8 --auto-attach"
        self.run(cmd)

    def __add_sam_repo(self, sam_compose):
        cmd = ('cat <<EOF > /etc/yum.repos.d/sam.repo\n'
            '[sam]\n'
            'name=sam\n'
            'baseurl=http://download.lab.bos.redhat.com/devel/candidate-trees/SAM/%s/compose/SAM/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            'EOF' % sam_compose
            )
        self.run(cmd)

    def __install_katello(self):
        cmd = "yum install -y katello-headpin-all"
        # cmd = "yum install -y git"
        self.run(cmd, timeout=7200)

    def __deploy_sam(self):
        cmd = "katello-configure --deployment=sam --user-pass=admin"
        self.run(cmd, timeout=1800)

    def __import_manifest(self):
        # only support remote run
        self.__upload_manifest()
        cmd = "headpin -u admin -p admin provider import_manifest --org=ACME_Corporation --name='Red Hat' --file=/root/sam_install_manifest.zip"
        self.run(cmd)

    def __upload_manifest(self):
        # self.remote_put(sam_manifest, "/root/%s" % manifest_name)
        cmd = "wget http://10.66.100.116/projects/sam-virtwho/latest-manifest/sam_install_manifest.zip -P /root/"
        self.run(cmd)

if __name__ == "__main__":
    sam_command = SAMCommand("10.66.128.31", "root", "redhat")
    sam_command.import_manifest()
#     sam_command.add_sam_repo("SAM-1.4.0-RHEL-6-20140512.0")

