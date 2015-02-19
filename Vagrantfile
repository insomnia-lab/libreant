# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "precise32"
  config.vm.box_url = "http://files.vagrantup.com/precise32.box"

  config.vm.synced_folder ".", "/liberant"
end

$script = <<SCRIPT
wget -qO - https://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add -
echo "deb http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main" >> /etc/apt/sources.list
apt-get update && apt-get install -y python python-dev python-virtualenv openjdk-7-jre-headless elasticsearch
cd /liberant
virtualenv -p /usr/bin/python2 --no-site-packages ve-precise32
./ve-precise32/bin/python setup.py develop
SCRIPT

Vagrant.configure("2") do |config|
    config.vm.provision :shell, :inline => $script
end
