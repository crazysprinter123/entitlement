#!/bin/bash
# vim: dict+=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /installation/entitlement-qa/Regression/rhsm-gui
#   Description: rhsm gui testing
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
        if [ "$REBOOTCOUNT" -eq 0 ] ; then
            #configure for ldtp gui test
            gconftool-2 --set /desktop/gnome/interface/accessibility --type=boolean true
            gconftool-2 -s /apps/gnome-session/options/show_root_warning --type=boolean false
            gconftool-2 -s /apps/gnome-screensaver/idle_activation_enabled --type=boolean false
            gconftool-2 -s /apps/gnome-power-manager/ac_sleep_display --type=int 0
            if [ `uname -r | awk -F "el" '{print substr($2,1,1)}'` -le 5 ]; then
                rpm -Uvh http://dl.fedoraproject.org/pub/epel/5/x86_64/epel-release-5-4.noarch.rpm
                yum -y install git
            fi
            cd /root
            git clone https://github.com/bluesky-sgao/entitlement
            cd /root/entitlement
            if [ `uname -r | awk -F "el" '{print substr($2,1,1)}'` -le 5 ]; then
                tar -zxvf data/ldtp/ldtp.tar.gz; cd ldtp/; ./autogen.sh --prefix=/usr; make; make install
            else
                tar -zxvf data/ldtp/ldtp-3.0.0.tar.gz; cd ldtp2/; python setup.py build; python setup.py install
            fi
            mkdir -p /root/.config/autostart
            cat > /root/.config/autostart/gnome-terminal.desktop <<EOF
[Desktop Entry]
Type=Application
Exec=gnome-terminal -e ldtp
Hidden=false
X-GNOME-Autostart-enabled=true
Name=ldtpd
Comment=
EOF
            #for rhel 7, init 5 seems not work
            if [ `uname -r | awk -F "el" '{print substr($2,1,1)}'` -eq 7 ] ; then
                rhts-reboot
            else
                chkconfig vncserver on; init 3; sleep 10; init 5
            fi
        fi
        vncserver -SecurityTypes None

    rlPhaseEnd

    rlPhaseStartTest
        rlRun "echo start testing .............."
        rlRun "cd /root/entitlement"
        rlRun "export PYTHONPATH=/root/entitlement"
        cases_list=$(ls testcases/rhsm/rhsm_gui | grep "^tc_ID.*py$")
        for i in $cases_list; do
            python testcases/rhsm/rhsm_gui/$i
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
