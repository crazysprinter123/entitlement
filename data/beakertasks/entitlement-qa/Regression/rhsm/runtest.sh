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
        bk_ip=$(hostname -I | awk {'print $1'})
        network_dev=$(ip route | grep $bk_ip | awk {'print $3'})
        rlRun "sed -i '/^BOOTPROTO/d' /etc/sysconfig/network-scripts/ifcfg-$network_dev"
        rlRun "echo "BRIDGE=switch" >> /etc/sysconfig/network-scripts/ifcfg-$network_dev"
        rlRun "cat > /etc/sysconfig/network-scripts/ifcfg-br0 <<EOF
DEVICE=switch
BOOTPROTO=dhcp
ONBOOT=yes
TYPE=Bridge
EOF"
        rlRun "service network restart"
        rlRun "vncserver -SecurityTypes None"
        rlRun "service network restart"
        if [ `uname -r | awk -F "el" '{print substr($2,1,1)}'` -le 5 ]; then
            rpm -Uvh http://dl.fedoraproject.org/pub/epel/5/x86_64/epel-release-5-4.noarch.rpm
            yum -y install git
        fi
        cd /root
        git clone https://github.com/bluesky-sgao/entitlement
        cd /root/entitlement
    rlPhaseEnd

    rlPhaseStartTest
        rlRun "echo start testing .............."
        rlRun "cd /root/entitlement"
        rlRun "export PYTHONPATH=/root/entitlement"
        cases_list=$(ls testcases/rhsm/$RUN_LEVEL/ | grep "^tc_ID.*py$")
        for i in $cases_list; do
            python testcases/rhsm/$RUN_LEVEL/$i
            if [ $? -eq 0 ]; then
                rhts-report-result $i PASS runtime/result/default/runtime.log
            else
                rhts-report-result $i FAIL runtime/result/default/runtime.log
            fi
        done
    rlPhaseEnd

    rlPhaseStartCleanup
    rlPhaseEnd
rlJournalPrintText
rlJournalEnd
