#!/usr/bin/python2

import datetime, time
import json
import requests
import sys

# When importing token into the /tmp/aruba file
# remove the last three 000


## need to handle error message:
# API rate limit exceeded etc ...

site_uri = 'https://app1-apigw.central.arubanetworks.com'
authorization_base_url = site_uri + '/oauth2/token/authorize/central'
token_url = site_uri + '/oauth2/token'

client_id = ''
client_secret = ''

authfile = '/tmp/aruba'

def print_json(data):
    print json.dumps({'data':data},sort_keys=True,indent=7,separators=(',',':'))

def getAuthToken( url, now, client_id, client_secret, refresh_token):
    response = session.post(url)
    newtokendict = response.json()
    if 'error_description' in newtokendict:
        return 'ZBX_NOTSUPPORTED'
    newtokendict['created_at'] = now
    authtoken = newtokendict['access_token']
    refresh_token = newtokendict['refresh_token']
    newjsontoken = json.JSONEncoder().encode(newtokendict)
    f = open(authfile,'w')
    f.write(newjsontoken)
    f.close()
    return authtoken

def getToken():
    with open(authfile, 'a+') as f:
        filetoken = f.read()
        try:
            dicttoken = json.loads(filetoken)
            authtoken = dicttoken['access_token']
            refresh_token = dicttoken['refresh_token']
            dtobj = dicttoken['created_at']
            expires = dtobj + dicttoken["expires_in"]
            url = token_url + '?client_id={0}&grant_type=refresh_token&refresh_token={1}&client_secret={2}'.format(client_id, refresh_token, client_secret)
            now = int(time.mktime(datetime.datetime.now().timetuple()))
            if expires < now:
                #print "expired"
                authtoken = getAuthToken(url, now, client_id, client_secret, refresh_token)
                return authtoken
            else:
                #print "not expired", now
                return authtoken
        except ValueError:
            #print "Invalid JSON. Retrieving new token"
            authtoken = getAuthToken(url, now, client_id, client_secret, refresh_token)
            return authtoken

def getApStatus(token):

    down_aps = []
    url = site_uri + '/monitoring/v1/aps?access_token={0}'.format(token)
    r = session.get(url)
    aps = r.json()[u'aps']
    for ap in aps:
        if ap[u'status'] == 'Down':
            down_aps.append(str(ap[u'name']))
            print 'Ap {0} status {1} from {2}'.format(ap[u'name'], ap[u'status'], ap[u'group_name'])
    return down_aps

def discoverAps(token):

    aps = []
    url = site_uri + '/monitoring/v1/aps?access_token={0}'.format(token)
    r = session.get(url)
    # Check for {"message":"API rate limit exceeded"}
    if 'message' in r.content:
        print 'ZBX_NOTSUPPORTED'
    elif 'error_description' in r.content:
        print 'ZBX_NOTSUPPORTED'
    else:
        apsList = r.json()[u'aps']
        for ap in apsList:
            aps.append({'{#NAME}': ap[u'name'], '{#IP}': ap[u'ip_address'], '{#SERIAL}': ap[u'serial'], '{#GROUP}': ap[u'group_name']})
        print_json(aps)

def discoverGroups(token):

    groups = []
    url = site_uri + '/monitoring/v1/aps?access_token={0}'.format(token)
    r = session.get(url)
    # Check for {"message":"API rate limit exceeded"}
    if 'message' in r.content:
        print 'ZBX_NOTSUPPORTED'
    elif 'error_description' in r.content:
        print 'ZBX_NOTSUPPORTED'
    else:
        apsList = r.json()[u'aps']
        for i in set(ap[u'group_name'] for ap in apsList):
            groups.append({'{#GROUP}': i})
        print_json(groups)

def getSwarmStatus(token):

    down_swarms = []
    url = site_uri + '/monitoring/v1/swarms?access_token={0}'.format(token)
    r = session.get(url)
    swarms = r.json()[u'swarms']
    for swarm in swarms:
        if swarm[u'status'] == 'Down':
            down_swarms.append(str(swarm[u'group_name']))
            print swarm[u'group_name'], swarm[u'status']
    return down_swarms
    print swarms

def getTotalClients(token):

    url = site_uri + '/monitoring/v1/clients/count?access_token={0}'.format(token)
    r = session.get(url)
    clients = r.json()[u'samples'][-1][u'client_count']
    print clients
    return clients

def getClients(token, group = None, ssid = None):

    if group is None:
        url = site_uri + '/monitoring/v1/clients/count?access_token={0}'.format(token)
    elif ssid is None:
        url = site_uri + '/monitoring/v1/clients/count?group={0}&access_token={1}'.format(group, token)
    else:
        url = url = site_uri + '/monitoring/v1/clients/count?group={0}&network={1}&access_token={2}'.format(group, ssid, token)
    r = session.get(url)
    # Check for {"message":"API rate limit exceeded"}
    if 'message' in r.content:
        print 'ZBX_NOTSUPPORTED'
    elif 'error_description' in r.content:
        print 'ZBX_NOTSUPPORTED'
    else:
        clients = r.json()[u'samples'][-1][u'client_count']
        print clients

if __name__ == "__main__":
    session = requests.Session()
    if sys.argv[1] == 'discoverAps':
        token = getToken()
        sys.exit(discoverAps(token))
    elif sys.argv[1] == 'discoverGroups':
        token = getToken()
        sys.exit(discoverGroups(token))
    elif sys.argv[1] == 'clients':
        token = getToken()
        if len(sys.argv) == 4:
            sys.exit(getClients(token, sys.argv[2], sys.argv[3]))
        elif len(sys.argv) == 3:
            sys.exit(getClients(token, sys.argv[2]))
        else:
            sys.exit(getClients(token))
    else:
        print 'ZBX_NOTSUPPORTED'
