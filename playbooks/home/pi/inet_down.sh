#!/bin/bash

TMP_FILE=/tmp/inet_down

no_inet_action() {
	counter=$1
	echo "No internet $counter"

	/usr/sbin/ifconfig wwan0
	sudo /usr/bin/qmi-network /dev/cdc-wdm0 status
	lsusb

	if ((counter < 2)); then
		echo "Recycle net"
		sudo ifdown wwan0
		sudo ifup wwan0
	else
		echo "Reboot"
		echo 0 > $TMP_FILE
    	sudo shutdown -r +1 'No internet.'
    fi
}

date

if ping -c5 google.com; then
    echo 0 > $TMP_FILE
else
	[ ! -f "$TMP_FILE" ] && echo 0 > $TMP_FILE
	counter=$((`cat $TMP_FILE` + 1))
	echo $counter > $TMP_FILE
    no_inet_action $counter
fi