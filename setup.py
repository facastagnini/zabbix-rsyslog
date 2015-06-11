from setuptools import setup
from sys import path

path.insert(0, '.')

NAME = "zabbix_rsyslog"

if __name__ == "__main__":

    setup(
        name = NAME,
        version = "1.0.0",
        author = "facastagnini",
        author_email = "",
        url = "https://github.com/facastagnini/zabbix-rsyslog",
        license = 'APL 2.0',
        packages = [NAME],
        package_dir = {NAME: NAME},
        data_files = [ ('/etc/rsyslog.d', ['10-impstats.conf']),
                       ('/etc/zabbix_agentd.d', ['rsyslogdiscovery.conf']),
                       ('/etc/logrotate.d', ['rsyslogd-impstats']) ],
        description = "Send rsyslog impstats output to zabbix",

        entry_points={
            'console_scripts': [ 'rsyslog-impstats.py = zabbix_rsyslog.rsyslog_impstats:main' ],
        }
    )

