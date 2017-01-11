#!/usr/bin/python -u
# -*- coding: utf-8 -*-

"""
Send rsyslog impstats output to zabbix
"""

import os
import re
import json
import sys
import argparse
import subprocess

def tail(f, n):
    """
    FIXME
    """
    process = subprocess.Popen(
        ("tail -n "+n+" "+f+" | awk -F': ' '{print $2}'"),
        shell=True, bufsize=0, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdin, stdout = (process.stdin, process.stdout)
    stdin.close()
    lines = stdout.readlines()
    stdout.close()
    return lines


def print_discovery_json(tag, values):
    """
    FIXME
    """
    tmp = []
    for value in values:
        tmp.append({tag: value})

    # python to json
    zabbix_str = dict(data=tmp)
    json_str = json.dumps(zabbix_str)
    print json_str


def run_discovery(filter):
    """
    FIXME
    """
    names = []
    for line in tail(log, "500"):
        json_object = json.loads(line)
        try:
            if json_object[filter] is not None:
                names.append(clean_name(json_object['name']))
        except:
            continue
    names = list(set(names))
    #print names
    print_discovery_json("{#ITEMNAME}", names)


def clean_name(name):
    """
    FIXME
    """
    return re.sub(r'[\[\]\(\)\*: ]', '_', name)


def process_impstats_json():
    """
    FIXME
    """
    if debug:
        fd = open('/tmp/testrsyslogomoutput.txt', 'a')
        fd.write("Opened logfile\n")
        fd.flush()

    while True:
        line = sys.stdin.readline()
        if not line:
            # exit if rsyslog dies
            break
        if debug:
            fd.write("Received: %s" % (line))
            fd.flush()
        json_object = json.loads(line)

        # send to zabbix
        name = clean_name(json_object['name'])
        del json_object['name']

        items_to_send = []
        for key in json_object:
            items_to_send.append('- rsyslog[{0},{1}] {2}'
                                 .format(name, key, json_object[key]))
        cmd = "echo '{0}' | zabbix_sender -i - " + \
            "-c /etc/zabbix/zabbix_agentd.conf".format('\n'.join(items_to_send))
        retvalue = os.system(cmd)
        if debug:
            fd.write("command: %s\n" % (cmd))
            fd.write("exit status: %s\n\n" % (retvalue))
            fd.flush()
    if debug:
        fd.close()


def main():
    """
    FIXME
    """
    global debug
    debug = False

    global log
    log = "/var/log/rsyslogd-impstats.log"

    # global pid_file
    # pid_file = '/var/run/rsyslog-impstats.pid'

    parser = argparse.ArgumentParser(usage='%(prog)s [--discover queue|action]')
    parser = argparse.ArgumentParser(
        description='Helper script to link syslog stats and zabbix.')
    parser.add_argument("--discover", action="store",
                        help="Discover the rsyslog items in this system")

    args = parser.parse_args()

    if args.discover == "queue":
        run_discovery("enqueued")
    elif args.discover == "action":
        run_discovery("processed")
    elif args.discover == "dynafile":
        run_discovery("evicted")
    else:
        # if there is no discovery, start parsing the syslog input.
        process_impstats_json()

    sys.exit(0)



if __name__ == "__main__":
    main()
