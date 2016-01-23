#!/usr/bin/python

import sys
import time
import subprocess
import argparse

from influxdb import InfluxDBClient
from enum import Enum

INTERVAL = 30

class IDX:
    desc, IFACE, rxpcks, txpcks, rxkBs,\
    txkBs, rxcmps, txcmps, rxmcsts, util = range(0, 10)

env = {
    'measurement' : 'env',
    'fields' : {
        'temp'  : None,
        'humid' : None
    }
}

aggregate = {
    'measurement' : 'aggregate',
    'fields' : {
        'in'  : None,
        'out' : None
    }
}


def read_traffic(client, interface):
    cmd = ['sar', '-n', 'DEV', '1', '1']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out, err = p.communicate()

    out = filter(lambda s: 'Average' in s, out.splitlines())
    out = filter(lambda s: interface in s, out)
    out = out[0].split()

    aggregate['fields']['out'] = float(out[IDX.txkBs])*1024
    aggregate['fields']['in'] = float(out[IDX.rxkBs])*1024

    commited = client.write_points([aggregate])


def commit_env(client, temp, humid):
    env['fields']['temp'] = float(temp)
    env['fields']['humid'] = float(humid)

    print temp, humid
    commited = client.write_points([env])


def read_env(client, executable):

    time.sleep(INTERVAL)
    cmd = [executable]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    out, err = p.communicate()
    timestamp, temp, humid = out.split()
    
    commit_env(client, temp, humid)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help = 'InfluxDB host.')
    parser.add_argument('username', help = 'InfluxDB username.')
    parser.add_argument('password', help = 'InfluxDB password.')
    parser.add_argument('command', nargs = '*', help = 'Command to execute.')
    args = parser.parse_args()

    host = args.host
    username = args.username
    password = args.password
    command = args.command

    if command[0] == 'traffic':
        dbname = 'traffic'
        interface = command[1]
    elif command[0] == 'env':
        dbname = 'env'
        executable = command[1]
    elif command[0] == 'write':
        dbname = 'env'
        temp = command[1]
        humid = command[2]
    else:
        print 'Unknown command. Exiting...'
        sys.exit(1)

    client = InfluxDBClient(host, 8086, 
                                username, password, dbname)

    if len(filter(lambda dic: dic['name'] == dbname, 
                              client.get_list_database())) == 0:
        client.create_database(dbname)

    if command[0] == 'traffic':
        while(True):
            read_traffic(client, interface) 
    elif command[0] == 'env':
        while(True):
            read_env(client, executable) 
    elif command[0] == 'write':
        commit_env(client, temp, humid)


if __name__ == "__main__":
    main()

