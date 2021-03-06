#!/bin/sh

# Define functions.
function fixperms {
	chown -R $UID:$GID /data /opt/mudtrix
}

cd /opt/mudtrix

if [ ! -f /data/config.yaml ]; then
	cp example-config.yaml /data/config.yaml
	echo "Didn't find a config file."
	echo "Copied default config file to /data/config.yaml"
	echo "Modify that config file to your liking."
	echo "Start the container again after that to generate the registration file."
	fixperms
	exit
fi

# Replace database path in config.
sed -i "s#sqlite:///mudtrix.db#sqlite:////data/mudtrix.db#" /data/config.yaml

# Check that database is in the right state
alembic -x config=/data/config.yaml upgrade head

if [ ! -f /data/registration.yaml ]; then
	python3 -m mudtrix -g -c /data/config.yaml -r /data/registration.yaml
	echo "Didn't find a registration file."
	echo "Generated one for you."
	echo "Copy that over to synapses app service directory."
	fixperms
	exit
fi

fixperms
exec su-exec $UID:$GID python3 -m mudtrix -c /data/config.yaml
