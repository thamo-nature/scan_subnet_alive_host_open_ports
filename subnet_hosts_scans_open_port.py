#! /usr/bin/python3
import os
import sys
import socket
import numpy as np
import multiprocessing
import subprocess
from datetime import datetime
import pyfiglet


def pinger(job_q, results_q):
    """
    Do Ping
    :param job_q:
    :param results_q:
    :return:
    """
    DEVNULL = open(os.devnull, 'w')
    while True:

        ip = job_q.get()

        if ip is None:
            break

        try:
            subprocess.check_call(['ping', '-c1', ip],
                                  stdout=DEVNULL)
            results_q.put(ip)
        except:
            pass


def get_my_ip():
    """
    Find my IP address
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def map_network(pool_size=255):
    """
    Maps the network
    :param pool_size: amount of parallel ping processes
    :return: list of valid ip addresses
    """
    
    ip_list = list()
    
    # get my IP and compose a base like 192.168.1.xxx
    ip_parts = get_my_ip().split('.')
    base_ip = ip_parts[0] + '.' + ip_parts[1] + '.' + ip_parts[2] + '.'
    
    # prepare the jobs queue
    jobs = multiprocessing.Queue()
    results = multiprocessing.Queue()
    
    pool = [multiprocessing.Process(target=pinger, args=(jobs, results)) for i in range(pool_size)]
    
    for p in pool:
        p.start()
    
    # cue hte ping processes
    for i in range(1, 255):
        jobs.put(base_ip + '{0}'.format(i))
    
    for p in pool:
        jobs.put(None)
    
    for p in pool:
        p.join()
    
    # collect he results
    while not results.empty():
        ip = results.get()
        ip_list.append(ip)

    return ip_list


if __name__ == '__main__':

    ascii_banner = pyfiglet.figlet_format("Accept who u r")
    print(ascii_banner)
    print('Mapping Network... ' + str(datetime.now()))    
    
    lst = map_network()
    print(lst)
for new_host in lst:
    print("Scanning for open ports in " + str(new_host))    
    target = socket.gethostbyname(new_host)
    print("Target Name : " + target)     
           
    try:
        
        # will scan ports between 1 to 65,535
        for port in range(1,65535):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket.setdefaulttimeout(1)
            
            # returns an error indicator
            result = s.connect_ex((target,port))
            if result ==0:
                print("Port {} is open".format(port))
                
            s.close()        
                    
    except KeyboardInterrupt:
            print("\n Exiting Program !!!!")
            sys.exit()
    except socket.gaierror:
            print("\n Hostname Could Not Be Resolved !!!!")
            sys.exit()
    except socket.error:
            print("\ Server not responding !!!!")
            sys.exit()                
            
            
                

