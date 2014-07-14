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
