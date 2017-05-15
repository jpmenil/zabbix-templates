#!/bin/bash

# Ugly script inspired from
# https://github.com/a-schild/zabbix-ipsec.git
# to check ipsec tunnels

# ------------------------------------------
IPV4_REGEX="(([0-9][0-9]?|[0-1][0-9][0-9]|[2][0-4][0-9]|[2][5][0-5])\.){3}([0-9][0-9]?|[0-1][0-9][0-9]|[2][0-4][0-9]|[2][5][0-5])"
IPSECBIN="/usr/sbin/ipsec"
# Run the ipsec command via sudo
USE_SUDO=0
SUDOBIN="/usr/bin/sudo"
# ------------------------------------------

if [ $USE_SUDO -eq 1 ];
then
    IPSECCMD="$SUDOBIN -- $IPSECBIN"
else
    IPSECCMD=$IPSECBIN
fi

# Testing availability of $IPSECBIN, $FPINGBIN and $GATEWAYLIST

if [ $# -eq 0 ];
then
   echo UNKNOWN - missing Arguments. Run check_ipsec --help
   exit $STATE_UNKNOWN
fi

test -e $IPSECBIN
if [ $? -ne 0 ]; then
    echo CRITICAL - $IPSECBIN not exist
    exit $STATE_CRITICAL
else
    STRONG=`$IPSECBIN --version |grep strongSwan | wc -l`
fi

tunnel_up() {

    CONN="$1"
    $IPSECBIN up $CONN
    if [ $? -ne 0 ]; then
        # echo "Failed to start the tunnel, please investigate"
        return 1
    else
        # echo "Tunnel $CONN up successfully"
        return 0
    fi

}

tunnel_down() {

    CONN="$1"
    $IPSECBIN down $CONN
    if [ $? -ne 0 ]; then
        # echo "Failed to stop the tunnel, please investigate"
        return 1
    else
        # echo "Tunnel $CONN down successfully"
        return 0
    fi

}

test_tunnel() {

    CONN="$1"
    if [[ "$STRONG" -eq "1" ]]; then
        if [[ $(ipsec status | grep -e "$CONN") ]]; then
            if [[ $(ipsec status | grep -e "$CONN" | grep -e "ESTABLISHED") ]] || [[ $(ipsec status | grep -e "$CONN" | grep -e "IPsec SA established" | grep -e "newest") ]]; then
                #if [[  $(ipsec status | grep -e "$CONN" | grep -v "ESTABLISHED" | grep -E "$IPV4_REGEX") ]] || [[ $(ipsec status | grep -e "$CONN" | grep -v "IPsec SA established" | grep -v "newest" || grep -E "$IPV4_REGEX") ]]; then
		if [[  $(ipsec status | grep -e "$CONN" | grep -v "ESTABLISHED" | grep -E "$IPV4_REGEX") ]]; then
                    # echo " Tunnel $CONN look ok"
                    return 1
                else
                    # echo "Tunnel $CONN established without route"
                    # Down the tunnel and up it again
                    tunnel_down $CONN
                    # Do it two time, sometime there is Ghost in the machine
                    tunnel_down $CONN
                    # Finally, up the tunnel
                    tunnel_up $CONN
                    if [ $? -ne 0 ]; then
                        # Something goes wrong, please investigate
                        return 0
                    else
                        return 1
                    fi
                fi
            else
                # echo "Tunnel $CONN not ESTABLISHED"
                # Down the tunnel and up it again
                tunnel_down $CONN
                # Do it two time, sometime there is Ghost in the machine
                tunnel_down $CONN
                # Finally, up the tunnel
                tunnel_up $CONN
                if [ $? -ne 0 ]; then
                    # Something goes wrong, please investigate
                    return 0
                else
                    return 1
                fi
            fi
        else
            # echo "Can not find any tunnel up for $CONN, let start it"
            tunnel_up $CONN
            if [ $? -ne 0 ]; then
                # echo "Somethin really weird appened while trying to up the following tunnel $CONN"
                return 1
            else
                # echo "Tunnel $CONN up successfully"
                return 0
            fi
        fi
    fi

}

test_tunnel $1
echo $?
