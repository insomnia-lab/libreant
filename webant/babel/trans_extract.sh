#!/bin/bash

Bdir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

source $Bdir/set_pybabel.sh

set -e
$pybabel extract -F $Bdir/babel.cfg -k lazy_gettext -o $Bdir/messages.pot $Bdir/../

