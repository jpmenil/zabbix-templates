#!/usr/bin/python2.7

from netaddr import iter_iprange
import itertools
import json
import os
import pypureomapi
import re
import sys

KEYNAME = 'defomapi'
BASE64_ENCODED_KEY = '3XH5DswLleKLNJiy1tPHlw=='
dhcp_server_ip = '127.0.0.1'
port = 7911 # Port of the omapi service
OMAPI_OP_UPDATE = 3
DHCP_CONF = '/etc/dhcp/dhcpd.master' if os.path.isfile('/etc/dhcp/dhcpd.master') else '/etc/dhcp/dhcpd.conf'

def discoverRange():

    reg_range = re.compile('range\s(.*?);')
    reg_name = re.compile('#= (.*?) =#')
    ranges = []
    with open(DHCP_CONF, 'r') as f:
        for key, group in itertools.groupby(f, lambda line: line.startswith('\n')):
            if not key:
                subnet_info = list(group)
                name = [m.group(1) for l in subnet_info for m in [reg_name.search(l)] if m]
                range = [m.group(1) for l in subnet_info for m in [reg_range.search(l)] if m]
                if range:
                    ip_start = range[0].split(' ')[0]
                    ip_end = range[0].split(' ')[1]
                    ips = list(iter_iprange(ip_start, ip_end, step=1))
                    ranges.append({'{#NAME}': name[0], '{#RANGE}': '{0}-{1}'.format(ip_start, ip_end), '{#TOTAL}': len(ips)})

    ranges_dict = {}
    ranges_dict['data'] = ranges
    return json.dumps(ranges_dict)

def checkRange(ipsList):

    ip_start = ipsList.split('-')[0]
    ip_end = ipsList.split('-')[1]
    ips = list(iter_iprange(ip_start, ip_end, step=1))
    # man 8 dhcpd.conf
    leases_states = {
            1: 'free',
            2: 'active',
            3: 'expired',
            4: 'released',
            5: 'abandoned',
            6: 'reset',
            7: 'backup',
            8: 'reserved',
            9: 'bootp'
            }
    results = {
            'Total': len(ips),
            'free': 0,
            'active': 0,
            'expired': 0,
            'abandoned': 0,
            'reset': 0,
            'backup': 0,
            'reserved': 0,
            'bootp': 0,
            'released': 0
            }

    o = pypureomapi.Omapi(dhcp_server_ip, port, KEYNAME, BASE64_ENCODED_KEY)
    for ip in ips:
        msg = pypureomapi.OmapiMessage.open('lease')
        msg.obj.append(('ip-address', pypureomapi.pack_ip(str(ip))))
        response = o.query_server(msg)
        if response.opcode != OMAPI_OP_UPDATE:
            print 'ZBX_NOTSUPPORTED'
        # Need to dig for the key error thingy
        try:
            state = ord(response.obj[0][1][-1:])
            results[leases_states[state]] += 1
        except KeyError:
            print 'ZBX_NOTSUPPORTED'

    print(results['free'] + results['backup'])

if __name__ == "__main__":

    if len(sys.argv) < 2:
        sys.exit(discoverRange()) 
    else:
        sys.exit(checkRange(sys.argv[1]))
