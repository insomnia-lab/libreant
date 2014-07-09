#!/usr/bin/env bash
base=$(realpath $(dirname $0)/elasticsearch)
elasticsearch "-Dcustom.prefix=$base/" \
	"-Des.config=$base/conf/elasticsearch.yml" $*

