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
echo -n "elastisearch is starting..."
if $(which netstat &> /dev/null); then
    while netstat -tpln 2> /dev/null|grep -Fq :9200; do
        sleep 1
    done
    sleep 1 #an extra second; what could be wrong?
else
    sleep 8  # ok, very dirty
fi
echo "  OK"
cd webant/
./run_web.sh
