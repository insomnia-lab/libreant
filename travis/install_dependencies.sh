#! /bin/bash

if [[ $VERSION_ES == "2.x" ]]; then
    sed -i "s/\('elasticsearch\)\(.*\)\('\)/\1 >=2.0.0, <3.0.0\3/" setup.py
    pip install .
fi

echo -e "travis_fold:start:ESinfo\r"
dpkg-query -W -f='DEB ${Package} ${Version}\n' elasticsearch
pip freeze|grep elasticsearch
echo -e "travis_fold:end:ESinfo\r"
