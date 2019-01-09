#!/bin/bash
apt-get update;
echo "nslcd   nslcd/ldap-base string  dc=company,dc=com" | debconf-set-selections;
echo "nslcd   nslcd/ldap-uris string  ldap://auth.transformanalytics.company.com" | debconf-set-selections;
echo "libnss-ldapd    libnss-ldapd/nsswitch   multiselect     group, passwd, shadow" | debconf-set-selections;
echo "libnss-ldapd:amd64      libnss-ldapd/nsswitch   multiselect     group, passwd, shadow" | debconf-set-selections;
apt-get -y install libpam-ldapd pcregrep ntp;
echo "pam_authz_search (&(objectClass=posixAccount)(uid=\$username)(|(host=$(/sbin/ifconfig eth0 | grep -P -o '(?<=inet)[^0-9]+[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | grep -P -o '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+'))))" | tee -a /etc/nslcd.conf;
sed -i -e 's/PasswordAuthentication\ no/PasswordAuthentication\ yes/' /etc/ssh/sshd_config;
echo -e "Name: Create home directory during login\nDefault: yes\nPriority: 900\nSession-Type: Additional\nSession:\n        required        pam_mkhomedir.so umask=0022 skel=/etc/skel\n" > /usr/share/pam-configs/mkhomedir;
service nslcd restart && service ssh restart;
DEBIAN_FRONTEND=noninteractive pam-auth-update;
wget https://amazon-ssm-us-west-2.s3.amazonaws.com/latest/debian_amd64/amazon-ssm-agent.deb -O /tmp/amazon-ssm-agent.deb;
dpkg -i /tmp/amazon-ssm-agent.deb;
echo -e "#! /bin/sh\n### BEGIN INIT INFO\n# Provides:          amazon-ssm-agent\n# Required-Start:    \$remote_fs \$syslog\n# Required-Stop:     \$remote_fs \$syslog\n# Default-Start:     2 3 4 5\n# Default-Stop:      0 1 6\n# Short-Description: Example initscript\n# Description:       This file should be used to construct scripts to be\n#                    placed in /etc/init.d.\n### END INIT INFO\n# Author: First last <First.last@company.com>\n\n# Do NOT \"set -e\"\n\n# PATH should only include /usr/* if it runs after the mountnfs.sh script\nPATH=/sbin:/usr/sbin:/bin:/usr/bin\nDESC=\"Amazon SSM Agent\"\nNAME=amazon-ssm-agent\nDAEMON=/usr/bin/\$NAME\nDAEMON_ARGS=\"\"\nPIDFILE=/var/run/\$NAME.pid\nSCRIPTNAME=/etc/init.d/\$NAME\n\n# Exit if the package is not installed\n[ -x \"\$DAEMON\" ] || exit 0\n\n# Read configuration variable file if it is present\n[ -r /etc/default/\$NAME ] && . /etc/default/\$NAME\n\n# Load the VERBOSE setting and other rcS variables\n. /lib/init/vars.sh\n\n# Define LSB log_* functions.\n# Depend on lsb-base (>= 3.2-14) to ensure that this file is present\n# and status_of_proc is working.\n. /lib/lsb/init-functions\n\n#\n# Function that starts the daemon/service\n#\ndo_start()\n{\n\t# Return\n\t#   0 if daemon has been started\n\t#   1 if daemon was already running\n\t#   2 if daemon could not be started\n\tstart-stop-daemon --start --quiet -b --pidfile \$PIDFILE --exec \$DAEMON --test > /dev/null \\CHANGEME\n\t\t|| return 1\n\tstart-stop-daemon --start --quiet -b --pidfile \$PIDFILE --exec \$DAEMON -- \\ \n\t\t\$DAEMON_ARGS \\CHANGEME\n\t\t|| return 2\n\t# Add code here, if necessary, that waits for the process to be ready\n\t# to handle requests from services started subsequently which depend\n\t# on this one.  As a last resort, sleep for some time.\n}\n\n#\n# Function that stops the daemon/service\n#\ndo_stop()\n{\n\t# Return\n\t#   0 if daemon has been stopped\n\t#   1 if daemon was already stopped\n\t#   2 if daemon could not be stopped\n\t#   other if a failure occurred\n\tstart-stop-daemon --stop --quiet --retry=TERM/30/KILL/5 --pidfile \$PIDFILE --exec \$DAEMON\n\tRETVAL=\"\$?\"\n\t[ \"\$RETVAL\" = 2 ] && return 2\n\t# Wait for children to finish too if this is a daemon that forks\n\t# and if the daemon is only ever run from this initscript.\n\t# If the above conditions are not satisfied then add some other code\n\t# that waits for the process to drop all resources that could be\n\t# needed by services started subsequently.  A last resort is to\n\t# sleep for some time.\n\tstart-stop-daemon --stop --quiet --oknodo --retry=0/30/KILL/5 --exec \$DAEMON\n\t[ \"\$?\" = 2 ] && return 2\n\t# Many daemons don't delete their pidfiles when they exit.\n\trm -f \$PIDFILE\n\treturn \"\$RETVAL\"\n}\n\n#\n# Function that sends a SIGHUP to the daemon/service\n#\ndo_reload() {\n\t#\n\t# If the daemon can reload its configuration without\n\t# restarting (for example, when it is sent a SIGHUP),\n\t# then implement that here.\n\t#\n\tstart-stop-daemon --stop --signal 1 --quiet --pidfile \$PIDFILE --exec \$DAEMON\n\treturn 0\n}\n\ncase \"\$1\" in\n  start)\n\t[ \"\$VERBOSE\" != no ] && log_daemon_msg \"Starting \$DESC\" \"\$NAME\"\n\tdo_start\n\tcase \"\$?\" in\n\t\t0|1) [ \"\$VERBOSE\" != no ] && log_end_msg 0 ;;\n\t\t2) [ \"\$VERBOSE\" != no ] && log_end_msg 1 ;;\n\tesac\n\t;;\n  stop)\n\t[ \"\$VERBOSE\" != no ] && log_daemon_msg \"Stopping \$DESC\" \"\$NAME\"\n\tdo_stop\n\tcase \"\$?\" in\n\t\t0|1) [ \"\$VERBOSE\" != no ] && log_end_msg 0 ;;\n\t\t2) [ \"\$VERBOSE\" != no ] && log_end_msg 1 ;;\n\tesac\n\t;;\n  status)\n\tstatus_of_proc \"\$DAEMON\" \"\$NAME\" && exit 0 || exit \$?\n\t;;\n  #reload|force-reload)\n\t#\n\t# If do_reload() is not implemented then leave this commented out\n\t# and leave 'force-reload' as an alias for 'restart'.\n\t#\n\t#log_daemon_msg \"Reloading \$DESC\" \"\$NAME\"\n\t#do_reload\n\t#log_end_msg \$?\n\t#;;\n  restart|force-reload)\n\t#\n\t# If the \"reload\" option is implemented then remove the\n\t# 'force-reload' alias\n\t#\n\tlog_daemon_msg \"Restarting \$DESC\" \"\$NAME\"\n\tdo_stop\n\tcase \"\$?\" in\n\t  0|1)\n\t\tdo_start\n\t\tcase \"\$?\" in\n\t\t\t0) log_end_msg 0 ;;\n\t\t\t1) log_end_msg 1 ;; # Old process is still running\n\t\t\t*) log_end_msg 1 ;; # Failed to start\n\t\tesac\n\t\t;;\n\t  *)\n\t\t# Failed to stop\n\t\tlog_end_msg 1\n\t\t;;\n\tesac\n\t;;\n  *)\n\t#echo \"Usage: \$SCRIPTNAME {start|stop|restart|reload|force-reload}\" >&2\n\techo \"Usage: \$SCRIPTNAME {start|stop|status|restart|force-reload}\" >&2\n\texit 3\n\t;;\nesac\n\n:\n" | sed 's/\CHANGEME//g' > /etc/init.d/amazon-ssm-agent
chmod a+x /etc/init.d/amazon-ssm-agent;
service amazon-ssm-agent start;
update-rc.d amazon-ssm-agent defaults;