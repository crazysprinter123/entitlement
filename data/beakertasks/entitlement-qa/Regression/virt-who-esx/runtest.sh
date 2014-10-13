#!/bin/bash
# vim: dict+=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /distribution/etitlement-qa/Regression/virt-who-esx
#   Description: Run virt-who esx testing
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

PACKAGE="etitlement-qa"

PACKAGE="entitlement-qa"

# decide if we're running standalone or in a Beaker instance
if test -z $JOBID ; then
        echo "Variable JOBID not set, assuming standalone"
        SERVERS="server-vm.example.com"
else
        echo "Variable JOBID set, we're running inside Beaker"
fi

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
        rlRun "if [ `uname -r | awk -F "el" '{print substr($2,1,1)}'` -eq 5 ]; then rpm -Uvh http://dl.fedoraproject.org/pub/epel/5/x86_64/epel-release-5-4.noarch.rpm; yum -y install git vgabios gnutls-utils selinux-policy selinux-policy-targeted selinux-policy-devel python-virtinst virt-manager virt-viewer; fi"
    rlPhaseEnd

    rlPhaseStartTest
        rlRun "rm -rf ~/.ssh/known_hosts"
        rlRun "cat > /root/get-libvirt-repo.sh <<EOF
#!/usr/bin/expect
spawn git clone git@qe-git.englab.nay.redhat.com:~/repo/hss-qe/entitlement/libvirt-test-API
expect \"yes/no\"
send \"yes\r\"
expect \"password:\"
send \"redhat\r\"
expect \"Resolving deltas: 100%\"
sleep 30
expect eof
EOF"
        rlRun "chmod 777 /root/get-libvirt-repo.sh"
        rlRun "cd /root/"
        rlRun "if [ ! -d /root/libvirt-test-API ]; then /root/get-libvirt-repo.sh; fi" 0 "Git clone libvirt-test-API"
        rlRun "sleep 60"
        rlRun "cd /root/libvirt-test-API"
        rlRun "echo \"Servers: $SERVERS\""
        cases_params_list=$(python libvirt-test-beaker-api.py --handleguest=$HANDLEGUEST --samhostname=$SAMHOSTNAME --confile=$CONFILE --copyimages=$COPYIMAGES --samhostip=$SAMHOSTIP --vcentermachine_ip=$VCENTERMACHINE_IP --vcentermachine_username=$VCENTERMACHINE_USERNAME --vcentermachine_password=$VCENTERMACHINE_PASSWORD --beaker=yes 2>&1 >/dev/null)
        for i in $cases_params_list; do
            python libvirt-test-beaker-api.py $i
            if [ $? -eq 0 ]; then
                rhts-report-result $i PASS result/default/$i
            else
                rhts-report-result $i FAIL result/default/$i
            fi
        done
    rlPhaseEnd
rlJournalPrintText
rlJournalEnd
