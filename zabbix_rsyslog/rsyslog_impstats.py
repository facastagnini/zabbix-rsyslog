#!/usr/bin/python -u
# -*- coding: utf-8 -*-
# File managed by puppet

import os
import re
import json
import sys
import argparse

log = "/var/log/rsyslogd-impstats.log"
pid_file = '/var/run/rsyslog-impstats.pid'

def tail(f, n):
	stdin,stdout = os.popen2("tail -n "+n+" "+f+" | awk -F': ' '{print $2}'")
	stdin.close()
	lines = stdout.readlines(); stdout.close()
	return lines


def print_discovery_json(tag, values):
	tmp = []
	for value in values:
		tmp.append({tag: value})
	
	# python to json
	zabbix_str = dict(data=tmp)
	json_str = json.dumps(zabbix_str)
	print json_str


def run_discovery(filter):
	names = []
	for line in tail(log,"30"):
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
	return re.sub('[\[\]\(\)\*: ]', '_', name)


def process_impstats_json():
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
		for key in json_object:
			cmd = 'zabbix_sender -c /etc/zabbix/zabbix_agentd.conf --key rsyslog["%s",%s] --value %s' % (name,key, json_object[key])
			retvalue = os.system(cmd)
			if debug:
				fd.write("command: %s\n" % (cmd))
				fd.write("exit status: %s\n\n" % (retvalue))
				fd.flush()
	if debug:
		fd.close()
        

def main():
	global debug 
	debug = False
	
	parser = argparse.ArgumentParser(usage='%(prog)s [--discover queue|action]')
	parser = argparse.ArgumentParser(description='Helper script to link syslog stats and zabbix.')
	parser.add_argument("--discover", action="store", help="Discover the rsyslog items in this system")
	
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
