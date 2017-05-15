# on dhcp server
* install dependencies:
    * python-pypureomapi
    * python-netaddr
* mv userparameter_dhcp.conf /etc/zabbix/zabbix_agentd.d/
* mv zabbix_sudoers /etc/sudoers.d/zabbix
* mv check_dhcp_leases.py /usr/local/bin/

# import templates in zabbix
* add graphs


As far as i know, there is no native way implemented by ISC dhcp to request free lease.

Two choices, parse the dhcpd.leases file, or do it via omapi.

The script is using omapi and is far from perfect.
