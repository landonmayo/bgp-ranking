#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

"""
Start/stop a connector to each whois server we know. 
"""

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../bgp-ranking.conf")
root_dir = config.get('global','root')
sys.path.append(os.path.join(root_dir,config.get('global','lib')))
services_dir = os.path.join(root_dir,config.get('global','services'))

import signal
from whois_client.whois_fetcher import get_all_servers_urls
from helpers.initscript import *

def usage():
    print "start_whois_fetching.py (start|stop|forcestop)"
    exit (1)

if len(sys.argv) < 2:
    usage()

service = os.path.join(services_dir, "fetch_whois_entries")
whois_service_options = get_all_servers_urls()

if sys.argv[1] == "start":

    print "Starting fetching..."
    for option in whois_service_options:
        print option+" to start..."
        proc = service_start(servicename = service, param = option)
        writepid(processname = option, proc = proc)
        print pidof(processname=option)

elif sys.argv[1] == "stop":

    print "Stopping sorting..."
    for option in whois_service_options:
        pids = pidof(processname=option)
        if pids:
            print option+" to be stopped..."
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGKILL)
                except OSError, e:
                    print option+  " unsuccessfully stopped"
            print option
            rmpid(processname=option)

elif sys.argv[1] == "forcestop":
    
    print "(forced) Stopping sorting..."
    nppidof()

else:
    usage()