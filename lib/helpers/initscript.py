import os
import platform
import subprocess


import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../bgp-ranking.conf")
root_dir = config.get('global','root')
sys.path.append(os.path.join(root_dir,config.get('global','lib')))
pid_path = os.path.join(root_dir,config.get('global','pids'))

"""
Standard functions used by the init scripts
"""

def service_start_once(servicename = None, param = None, processname = None):
    pidpath = os.path.join(pid_path,processname+".pid")
    if not os.path.exists(pidpath):
        proc = service_start(servicename, param)
        writepid(processname, proc)
    else:
        print(param + ' already running on pid ' + str(pidof(processname)[0]))

def service_start(servicename = None, param = None):
    """
    Launch a Process
    """
    if servicename is not None :
        service = servicename+".py"
        if not param:
            proc =  subprocess.Popen(["python",service])
        else:
            proc =  subprocess.Popen(["python",service, param])
        return proc
    return False

def writepid (processname = None, proc = None):
    """
    Append the pid to the pids-list of this process
    """
    pidpath = os.path.join(pid_path,processname+".pid")

    if processname is not None and proc is not None:
        f = open (pidpath,"a")
        f.write(str(proc.pid)+'\n')
        f.close()
        return True
    else:
        return False

def rmpid (processname = None):
    """
    Delete the pids-file
    """
    pidpath = os.path.join(pid_path,processname+".pid")
    if os.path.exists(pidpath):
        os.unlink(pidpath)
        return True
    else:
        return False

def pidof(processname = None):
    """
    Get the pid of a process 
    """
    pidpath = os.path.join(pid_path,processname+".pid")
    if processname is not None and os.path.exists(pidpath):
        f = open (pidpath)
        pids = f.readlines()
        f.close()
        return pids
    else:
        return False

def nppidof(processname = None):
    """
    Force the kill of the process (not used)
    """

    if platform.system() is not "Windows":
        #os.system("ps ax | grep forban_ | grep python | cut -d\" \" -f1 | sed -e '$!N;N;N; s/\\n/,/g'")
        return True

def update_running_pids(old_procs):
    """
    Update the list of the running process
    """
    new_procs = []
    for proc in old_procs:
        if proc.poll():
            print(str(proc.pid) + ' is alive')
            new_procs.append(proc)
        else:
            try:
                os.kill (proc.pid, signal.SIGKILL)
            except:
                # the process is just already gone
                pass
    return new_procs

# FIXME : put it in the config
min_ips_by_process = 100
max_ips_by_process = 500
max_processes = 1

def init_counter(total_ips):
    ip_counter = {}
    ip_counter['total_ips'] = total_ips
    ip_counter['processes'] = max_processes
    ip_counter['min'] = 0
    ips_by_process = total_ips/max_processes
    if ips_by_process > max_ips_by_process:
        ips_by_process = max_ips_by_process
    elif ips_by_process < min_ips_by_process:
        ip_counter['processes'] = 0
        ips_by_process = min_ips_by_process
        while total_ips > 0:
            total_ips -= ips_by_process
            ip_counter['processes'] += 1
    ip_counter['max'] = ips_by_process
    ip_counter['interval'] = ips_by_process
    return ip_counter
