#!/bin/bash
# vim: dict+=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /distribution/entitlement-qa/Regression/rhsm
#   Description: rhsm testing
#   Author: gao shang <sgao@redhat.com>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2014 Red Hat, Inc.
#
#   This program is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 2 of
#   the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE.  See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see http://www.gnu.org/licenses/.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Include Beaker environment
. /usr/bin/rhts-environment.sh || exit 1
. /usr/share/beakerlib/beakerlib.sh || exit 1

PACKAGE="entitlement-qa"

#disable avc check
setenforce 0
export AVC_ERROR=+no_avc_check

rlJournalStart
    rlPhaseStartSetup
        rlRun "sed -i '/^BOOTPROTO/d' /etc/sysconfig/network-scripts/ifcfg-eth0"
        rlRun "echo "BRIDGE=switch" >> /etc/sysconfig/network-scripts/ifcfg-eth0"
        rlRun "cat > /etc/sysconfig/network-scripts/ifcfg-br0 <<EOF
DEVICE=switch
BOOTPROTO=dhcp
ONBOOT=yes
TYPE=Bridge
EOF"
        rlRun "service network restart"
        if [ `uname -r | awk -F "el" '{print substr($2,1,1)}'` -le 5 ]; then
            rpm -Uvh http://dl.fedoraproject.org/pub/epel/5/x86_64/epel-release-5-4.noarch.rpm
            yum -y install git
        fi
        rlRun "rm -rf ~/.ssh/known_hosts"
        rlRun "cat > /root/get-autotest-repo.sh <<EOF
#!/usr/bin/expect
spawn git clone git@qe-git.englab.nay.redhat.com:~/repo/hss-qe/entitlement/autotest
expect \"yes/no\"
send \"yes\r\"
expect \"password:\"
send \"redhat\r\"
expect \"Resolving deltas: 100%\"
sleep 30
expect eof
EOF"
        rlRun "chmod 777 /root/get-autotest-repo.sh"
        rlRun "cd /root/"
        rlRun "if [ ! -d /root/autotest ]; then /root/get-autotest-repo.sh; fi" 0 "Git clone autotest"
        rlRun "sleep 60"
        rlRun "cd /root/autotest"
    rlPhaseEnd

    rlPhaseStartTest

    rlPhaseEnd

    rlPhaseStartCleanup
    rlPhaseEnd
rlJournalPrintText
rlJournalEnd
