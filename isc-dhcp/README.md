# on dhcp server
. install dependencies:
    - python-pypureomapi
    - python-netaddr
. mv userparameter_dhcp.conf /etc/zabbix/zabbix_agentd.d/
. mv zabbix_sudoers /etc/sudoers.d/zabbix
. mv check_dhcp_leases.py /usr/local/bin/

!! check_dhcp_leases.py script is furnished as best effort script ...

# import templates in zabbix
. add graphs
