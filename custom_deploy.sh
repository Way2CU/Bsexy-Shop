#!/bin/bash
cd deploy
PID_FILE=/tmp/ansible.pid

if [ -f "hosts.txt" ]; then
	ansible-playbook -i 185.151.197.11, --ask-pass ./custom_deploy.yml

	echo $! > $PID_FILE
	wait $!
	rm -f $PID_FILE
	exit $?

else
	echo 'Missing "hosts" file.'
fi
