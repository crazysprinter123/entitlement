'''
Run command in remote machine with paramiko
'''
import sys
import pexpect
from utils import logger

try:
    import paramiko
except ImportError:
    print "Please install paramiko."
    sys.exit(-1)

class RemoteSH(object):
    """
    Run shell in remote machine via paramiko
    """
    @classmethod
    def remote_run(self, cmd, remote_ip, username, password, timeout=None):
        """
        Executes SSH command on remote machine.
        """

        logger.info(">>> %s" % cmd)
        stdout = self.run_paramiko(cmd, remote_ip, username, password, timeout=timeout)
#         regex = re.compile(r'\x1b\[\d\d?m')
#         if stdout:
#             stdout = stdout.decode('utf-8')
#             stdout = u"".join(stdout).split("\n")
#             output = [
#                 regex.sub('', line) for line in stdout if not line.startswith("[")
#                 ]
#         else:
#             output = []

#         if output:
#             logger.debug("<<<\n%s" % '\n'.join(output[:-1]))
        logger.info("<<<\n%s" % stdout)
        return stdout

    @classmethod
    def remote_get(self, remote_ip, username, password, from_path, to_path):
        scp = paramiko.Transport((remote_ip, 22))
        scp.connect(username, password)
        sftp = paramiko.SFTPClient.from_transport(scp)
        # Copy a remote file from the SFTP server to the local host
        sftp.get(from_path, to_path)
        scp.close()

    @classmethod
    def remote_put(self, remote_ip, username, password, from_path, to_path):
        scp = paramiko.Transport((remote_ip, 22))
        scp.connect(username, password)
        sftp = paramiko.SFTPClient.from_transport(scp)
        # Copy a local file to the SFTP server
        sftp.put(from_path, to_path)
        scp.close()

    @classmethod
    def run_paramiko(self, cmd, remote_ip, username, password, timeout=None):
        # paramiko.util.log_to_file('/tmp/test')
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(remote_ip, 22, username, password)
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        # logger.info(stdout.read())
        ssh.close()
        return stdout.read()

    @classmethod
    def run_pexpect(self, cmd, remote_ip, username, password):
            """ Remote exec function via pexpect """
            user_hostname = "%s@%s" % (username, remote_ip)
            child = pexpect.spawn("/usr/bin/ssh", [user_hostname, cmd], timeout=60, maxread=2000, logfile=None)
            while True:
                    index = child.expect(['(yes\/no)', 'password:', pexpect.EOF, pexpect.TIMEOUT])
                    if index == 0:
                            child.sendline("yes")
                    elif index == 1:
                            child.sendline(password)
                    elif index == 2:
                            child.close()
                            return child.exitstatus, child.before
                    elif index == 3:
                            child.close()

if __name__ == "__main__":
#     exit_code, result = RemoteSH.run_pexpect("ifconfig", "10.66.129.77", "root", "gaoshang")
#     print exit_code, result
#     RemoteSH.run_paramiko("ifconfig", "10.66.129.77", "root", "gaoshang")
#     RemoteSH.remote_run("ifconfig", "10.66.129.77", "root", "gaoshang")
    pass