#!/usr/bin/env bash
set -e

webrun=webant
if [ -n "$1" ]; then
    webrun="$1/bin/$webrun"
    shift
    if [ ! -f "$webrun" ]; then
        echo "Virtualenv not found"
        exit 1
    fi
fi

./run_es.sh start -d

cleanup() {
	./run_es.sh stop
}
trap cleanup EXIT

PYTHONPATH=. $webrun $*
