#!/usr/bin/env bash
set -e

webrun=flaskdev
if [ -n "$1" ]; then
    webrun="$1/bin/$webrun"
    shift
    if [ ! -f "$webrun" ]; then
        echo "Virtualenv not found"
        exit 1
    fi
fi

./run_es.sh -d
PYTHONPATH=. $webrun webant $*
pid=$(cat elasticsearch/data/pid 2> /dev/null)
if [ -n "$pid" ]; then
	kill $pid
fi
