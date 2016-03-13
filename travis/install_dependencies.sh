#! /bin/bash

if [[ $VERSION_ES == "2.x" ]]; then
    sudo apt-get autoremove --purge elasticsearch
    wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
    echo "deb http://packages.elastic.co/elasticsearch/2.x/debian stable main" | sudo tee -a /etc/apt/sources.list.d/elk.list
    sudo apt-get update && sudo apt-get install elasticsearch -y
    sudo service elasticsearch start
    sed -i "s/\('elasticsearch\)\(.*\)\('\)/\1 >2\3/g" setup.py
    pip install --upgrade elasticsearch>=2.0
fi
