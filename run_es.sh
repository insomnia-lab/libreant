#!/usr/bin/env bash
base=$(realpath $(dirname $0)/elasticsearch)
PID_FILE="$base/data/pid"
if [[ -f "$PID_FILE" ]]; then
    pid=$(cat "$PID_FILE")
    if [[ -d "/proc/$pid" ]]; then
        echo "Error: elasticsearch already running with pid $pid" >&2
        exit 1
    else
        rm "$PID_FILE"
    fi
fi

elasticsearch -p "$PID_FILE" "-Dcustom.prefix=$base/" \
	"-Des.config=$base/conf/elasticsearch.yml" $*

