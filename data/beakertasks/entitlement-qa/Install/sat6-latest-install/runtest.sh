#!/bin/bash
# vim: dict+=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /installation/entitlement-qa/Install/sat6-latest-install
#   Description: install latest satellite 6
#   Author: gao shang <sgao@redhat.com>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2015 Red Hat, Inc.
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
        rlRun "setenforce 0" 0 "Set selinux"
        rlRun "sed -i -e 's/SELINUX=.*/SELINUX=permissive/g' /etc/sysconfig/selinux" 0 "Change selinux configure: permissive"
        rlRun "service iptables stop" 0 "Stop iptables service"
        rlRun "subscription-manager register --username=qa@redhat.com --password=uBLybd5JSmkRHebA --auto-attach" 0 "Auto subscribe"
        rlRun "subscription-manager repos --disable "*""
        rlRun "subscription-manager repos --enable rhel-7-server-rpms --enable rhel-server-rhscl-7-rpms"
        rlRun "cat > /etc/yum.repos.d/sat6.repo <<EOF
[sat6]
name=sat6
baseurl=http://satellite6.lab.eng.rdu2.redhat.com/devel/candidate-trees/Satellite/latest-stable-Satellite-6.1-RHEL-7/compose/Satellite/x86_64/os/
enabled=1
gpgcheck=0

[sat6-capsule]
name=Satellite 6 Capsule Packages
baseurl=http://satellite6.lab.eng.rdu2.redhat.com/devel/candidate-trees/Satellite/latest-stable-Satellite-6.1-RHEL-7/compose/Capsule/x86_64/os/
enabled=1
gpgcheck=0

[sat6-rhcommon]
name=Satellite 6 RH Common Packages
baseurl=http://satellite6.lab.eng.rdu2.redhat.com/devel/candidate-trees/Satellite/latest-stable-Satellite-6.1-RHEL-7/compose/sattools/x86_64/os/
enabled=1
gpgcheck=0

EOF" 0 "Add satellite 6 latest repo"
        rlRun "yum install -y katello"
        rlRun "katello-installer --foreman-admin-password=admin"
        rlRun "sed -i \"s/^enabled=.*/enabled=1/\" /etc/yum.repos.d/*beaker*"
rlJournalPrintText
rlJournalEnd
