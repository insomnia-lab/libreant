#!/usr/bin/env bash
set -e

if [ -n "$1" ]; then
    act="$1/bin/activate"
    if [ ! -f "$act" ]; then
        echo "Virtualenv not found"
        exit 1
    fi
    source "$act"
fi

./run_es.sh -d
cd webant/
./run_web.sh
pid=$(cat elasticsearch/data/pid 2> /dev/null)
if [ -n "$pid" ]; then
	kill $pid
fi
