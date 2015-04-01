#!/bin/bash
# vim: dict+=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /installation/entitlement-qa/Install/sam-latest-install
#   Description: Install the latest SAM to support Entitlement QA testing, including SAM intergration and virt-who testing
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

rlJournalStart
    rlPhaseStartSetup
#        if [ "$REBOOTCOUNT" -eq 0 ] ; then
            rlRun "setenforce 0" 0 "Set selinux"
            rlRun "sed -i -e 's/SELINUX=.*/SELINUX=permissive/g' /etc/sysconfig/selinux" 0 "Change selinux configure: permissive"
            rlRun "service iptables stop" 0 "Stop iptables service"
            rlRun "subscription-manager register --username=qa@redhat.com --password=uBLybd5JSmkRHebA --auto-attach" 0 "Auto subscribe"
            rlRun "cat > /etc/yum.repos.d/sam.repo <<EOF
[sam]
name=sam
baseurl=http://download.devel.redhat.com/devel/candidate-trees/SAM/latest-SAM-$VERSION-RHEL-6/compose/SAM/x86_64/os/
enabled=1
gpgcheck=0
EOF" 0 "Add SAM latest repo"
            rlRun "yum install -y katello-headpin-all" 0 "Install katello-headpin-all"
#            rhts-reboot
#        fi
#Failed to start katello service, will check later
#        rlRun "katello-configure --deployment=sam --user-pass=admin" 0 "Deploy SAM"
    rlPhaseEnd

    rlPhaseStartTest
        rlRun "wget http://10.66.100.116/projects/sam-virtwho/latest-manifest/sam_install_manifest.zip -P /root/" 0 "Wget manifest from data server"
#        rlRun "headpin -u admin -p admin provider import_manifest --org=ACME_Corporation --name='Red Hat' --file=/root/sam_install_manifest.zip" 0 "Import entitlement team related manifest"
#        rlLogInfo "$(rpm -q katello katello-cli candlepin katello-configure katello-cli-common katello-common subscription-manager python-rhsm)"
    rlPhaseEnd

rlJournalPrintText
rlJournalEnd
