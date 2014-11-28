#!/bin/bash

Bdir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

source $Bdir/set_pybabel.sh

set -e
$pybabel compile -d $Bdir/../translations -f
