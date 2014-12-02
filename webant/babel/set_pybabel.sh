#!/bin/bash

# A POSIX variable
OPTIND=1    # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
while getopts "e:" opt; do
    case "$opt" in
    e)  env=$OPTARG
        ;;
    esac
done

shift $((OPTIND-1))

[ "$1" = "--" ] && shift

Bdir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

defaultEnv=$Bdir/../../ve
pybabel=pybabel

hash $pybabel 2>/dev/null
if [ $? -ne 0 ]; then
    pybabel=$defaultEnv/bin/pybabel
    if [ ! -f "$pybabel" ]; then
        if [ -n "$env" ]; then
            pybabel=$env/bin/pybabel
            if [ ! -f "$pybabel" ]; then
                echo "Pybable bin not found"
                exit 1
            fi
            echo "Pybable bin not found"
            exit 1
        fi
     fi
fi
