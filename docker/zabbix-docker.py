#!/usr/bin/env python

import docker
import sys

def numberOfContainers(containerList):

    return len(containerList)

def numberOfRunningContainer(containerList):

    number = 0
    for container in containerList:
        state = container['State']
        if state == 'running':
            number += 1

    return number

def nameOfContainer(containerList):

    names = []
    for container in containerList:
        name = container['Names'][0]
        if name[0].startswith('/'):
            name = name.split('/')[1]
        names.append({'{#NAME}': name})

    con_dict = {}
    con_dict['data'] = names

    return json.dumps(con_dict)

def stateOfContainer(client, container):

    # Need to check if container with name provided exist for real
    try:
        return client.containers(filters={'name': container})[0]['State']
    except:
        print 'Container with this name is not running'
        sys.exit(0)

if __name__ == "__main__":

    if len(sys.argv) > 1:
        client = docker.Client(base_url='unix://var/run/docker.sock')
        if sys.argv[1] == 'list':
            import json
            containerList = client.containers()
            sys.exit(nameOfContainer(containerList))
        else:
            client = docker.Client(base_url='unix://var/run/docker.sock')
            sys.exit(stateOfContainer(client, sys.argv[1]))
    else:
        print 'Please run script with list or container name'
        sys.exit(0)
