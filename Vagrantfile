# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "precise32"
  config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-i386-vagrant-disk1.box"
  config.vm.box_download_checksum = "e720cb6ed0a9a46f1e5ada73243f8622f623d297de3035a5f745bcfb14ec8f68"
  config.vm.box_download_checksum_type = "sha256"

  config.vm.synced_folder ".", "/libreant"
  config.vm.network "forwarded_port", guest: 5000, host: 5000

end

$script = <<SCRIPT
wget -qO - https://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add -
echo "deb http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main" >> /etc/apt/sources.list
apt-get update && apt-get install -y python python-dev python-virtualenv openjdk-7-jre-headless elasticsearch
update-rc.d elasticsearch defaults
service elasticsearch start
cd /libreant
virtualenv -p /usr/bin/python2 --no-site-packages /ve
/ve/bin/python setup.py develop
SCRIPT

Vagrant.configure("2") do |config|
    config.vm.provision :shell, :inline => $script
end
