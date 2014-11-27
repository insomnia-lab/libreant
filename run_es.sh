#!/usr/bin/env bash

usage() {
	echo "$0 start [elasticsearch arguments]"
	echo "$0 stop"
}

base=$(readlink -f $(dirname $0)/elasticsearch)
PID_FILE="$base/data/pid"

PATH=/usr/share/elasticsearch/bin:$PATH
pid=
if [[ -f "$PID_FILE" ]]; then
	pid=$(cat "$PID_FILE")
	if [[ ! -d "/proc/$pid" ]]; then
		pid=
	else
		rm "$PID_FILE"
	fi
fi
if [[ $# -lt 1 ]]; then
	usage >&2
	exit 2
fi
if [[ $1 = start ]]; then
	shift 1
	if [[ -n "$pid" ]]; then
		echo "Error: elasticsearch already running with pid $pid" >&2
		exit 1
	fi
	elasticsearch -p "$PID_FILE" "-Dcustom.prefix=$base/" \
		"-Des.config=$base/conf/elasticsearch.yml" $*
elif [[ $1 = stop ]]; then
	if [[ -z "$pid" ]]; then
		echo "Not running"
		exit 0
	fi
	kill "$pid"
else
	echo "Bad subcommand" >&2
	usage >&2
	exit 2
fi


