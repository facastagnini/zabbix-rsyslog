
TODO: THIS README NEEDS SOME LOVE

This is a fork for the creation of an RPM. Basically, run "make" in the directory to build the RPM.
Install it.

In Zabbix you will still need to import the template and attach it to each rsyslog host. That's about it.
[I may have forgotten a step; if so I'll add it later.]

zabbix-rsyslog
==============




Description
-----------

I needed to monitor one rsyslog server, with multiple clients forwarding logs.
This is how I got to monitor that with zabbix.

Zabbix will execute the discovery script, and create the appopiate items on each hosts. 

This tutorial assumes you have a zabbix server up and running.


Installation
------------

1) Import the [zabbix template](zbx_rsyslog_stats_template.xml) and add it to all the nodes running rsyslog.

2) With you favorite management tool, perform this actions on each server running rsyslog.

```bash
# install the script
cp rsyslog-impstats.py /etc/zabbix/include.d/
chmod 0644 /etc/zabbix/clientscripts/rsyslog-impstats.py
chown zabbix:zabbix /etc/zabbix/clientscripts/rsyslog-impstats.py

# configure zabbix to call the script
echo 'UserParameter=rsyslog.discovery[*],/etc/zabbix/clientscripts/rsyslog-impstats.py --discover $1' > /etc/zabbix/include.d/rsyslogdiscovery.conf
chmod 0644 /etc/zabbix/include.d/rsyslogdiscovery.conf
chown zabbix:zabbix /etc/zabbix/include.d/rsyslogdiscovery.conf

# configure rsyslog to send stats to the script
cat << EOF > /etc/rsyslog.d/10-impstats.conf
# Switch back to default ruleset
$RuleSet RSYSLOG_DefaultRuleset

# Input Module to Generate Periodic Statistics of Internal Counters
# http://www.rsyslog.com/doc/impstats.html
# http://www.rsyslog.com/impstats-analyzer/
module(load="impstats" interval="60" severity="7" format="json")

template (name="JustTheMSG" type="string" string="%msg%\n")
	
if $programname == "rsyslogd-pstats" then {
    action(name="action-impstats" type="omfile" file="/var/log/rsyslogd-impstats.log"
       # queue configuration
       queue.type="LinkedList"
       queue.checkpointinterval="0"
       queue.discardmark="90"
       queue.size="100"
       queue.timeoutenqueue="10"
       queue.dequeuebatchsize="50"
    )

    # monitoring template="JustTheMSG"
    action(name="action-omprog-impstats" type="omprog" binary="/etc/zabbix/clientscripts/rsyslog-impstats.py" template="JustTheMSG"
       # queue configuration
       queue.type="LinkedList"
       queue.checkpointinterval="0"
       queue.discardmark="900"
       queue.size="1000"
       queue.timeoutenqueue="10"
       queue.dequeuebatchsize="50"
    )

    stop
}
EOF
chmod 0644 /etc/rsyslog.d/10-impstats.conf
chown root:root /etc/rsyslog.d/10-impstats.conf

# configure logrotate
echo << EOF > /etc/logrotate.d/rsyslogd-impstats
/var/log/rsyslogd-impstats.log {
  missingok
  sharedscripts
  notifempty
  daily
  rotate 0
  size 10M
  postrotate
    invoke-rc.d rsyslog rotate > /dev/null
  endscript
}
EOF
chmod 0444 /etc/logrotate.d/rsyslogd-impstats
chown root:root /etc/logrotate.d/rsyslogd-impstats


# apply the changes
service zabbix restart
service rsyslog restart
```

3) wait until the zabbix discovery is executed and see how the fields appear and get populated


Troubleshooting
---------------

1) Make sure the log file '/var/log/rsyslogd-impstats.log' is formated in JSON.
2) Disable other rsyslog configuration that you may have, impstats wants to be loaded earlie to function properly.

Reference [impstats documentation](http://www.rsyslog.com/doc/v8-stable/configuration/modules/impstats.html)
```
Caveats/Known Bugs
This module MUST be loaded right at the top of rsyslog.conf, otherwise stats may not get turned on in all places.
```


Contributing
------------

Forks, patches and other feedback are welcome.
