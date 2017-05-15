#!/usr/bin/env python
# -*-coding:utf-8 -*

import itertools
import re
import sys

IPSEC_CONF = '/var/lib/strongswan/ipsec.conf.inc'
rtt_time_warn = 200
rtt_time_error = 300
#JSON_FILE = 'ipsec.conf'

def parseConf():
    reg_conn = re.compile('^conn\s((?!%default).*)')
    reg_left = re.compile('.*leftid=(.*).*')
    reg_right = re.compile('.*rightid=(.*).*')
    data = {}
    with open(IPSEC_CONF, 'r') as f:
        for key, group in itertools.groupby(f, lambda line: line.startswith('\n')):
            if not key:
                conn_info = list(group)
                conn_tmp = [m.group(1) for l in conn_info for m in [reg_conn.search(l)] if m]
                left_tmp = [m.group(1) for l in conn_info for m in [reg_left.search(l)] if m]
                right_tmp = [m.group(1) for l in conn_info for m in [reg_right.search(l)] if m]
                if conn_tmp and left_tmp and right_tmp:
                    data[conn_tmp[0]] = [left_tmp[0], right_tmp[0]]
        return data

def getTemplate():
    template = """
        {{ "{{#TUNNEL}}":"{0}","{{#TARGETIP}}":"{1}","{{#SOURCEIP}}":"{2}" }}"""

    return template

def getPayload():
    final_conf = """{{
    "data":[{0}
    ]
}}"""

    conf = ''
    data = parseConf().items()
    for key,value in data:
        tmp_conf = getTemplate().format(
            key,
            value[1],
            value[0],
            rtt_time_warn,
            rtt_time_error
        )
        if len(data) > 1:
            conf += '%s,' % (tmp_conf)
        else:
            conf = tmp_conf
    if conf[-1] == ',':
        conf=conf[:-1]
    return final_conf.format(conf)

"""
def writePayload():
    with open(JSON_FILE, 'w') as f:
        f.write(getPayload())
"""

if __name__ == "__main__":
    ret = getPayload()
    sys.exit(ret)
#    writePayload()
