Sysadmin
=========

Installation
-------------

System dependencies
^^^^^^^^^^^^^^^^^^^^
.. note::
        In this moment we do *not* support elasticsearch v2.
        There are plans to do it shortly!

Debian wheezy / Debian jessie / Ubuntu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. highlight:: bash

Download and install the Public Signing Key for elasticsearch repo::

    wget -qO - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | sudo apt-key add -

Add elasticsearch repos in /etc/apt/sources.list.d/elasticsearch.list::

    echo "deb http://packages.elasticsearch.org/elasticsearch/1.7/debian stable main" | sudo tee /etc/apt/sources.list.d/elasticsearch.list

Install requirements::
    
    sudo apt-get update && sudo apt-get install python2.7 gcc python2.7-dev python-virtualenv openjdk-7-jre-headless elasticsearch

.. note::
    
    if you have problem installing elasticsearch try to follow the `official installation guide`_

.. _official installation guide: http://www.elastic.co/guide/en/elasticsearch/reference/current/setup-repositories.html

Arch
~~~~~

Install all necessary packages::

    sudo pacman -Sy python2 python2-virtualenv 

And take care to install elasticsearch<2.x::

    wget https://archive.archlinux.org/packages/e/elasticsearch/elasticsearch-1.7.3-1-x86_64.pkg.tar.xz
    wget https://archive.archlinux.org/packages/e/elasticsearch/elasticsearch-1.7.3-1-x86_64.pkg.tar.xz.sig
    sudo pacman-key --verify elasticsearch-1.7.3-1-x86_64.pkg.tar.xz elasticsearch-1.7.3-1-x86_64.pkg.tar.xz.sig
    sudo pacman -U elasticsearch-1.7.3.1-x86_64.pkg.tar.xz
    echo "IgnorePkg elasticsearch" | sudo tee -a /etc/pacman.conf

Python dependencies
^^^^^^^^^^^^^^^^^^^^

Create a virtual env::

    virtualenv -p /usr/bin/python2 ve

Install libreant and all python dependencies::
    
    ./ve/bin/pip install libreant

Execution
----------

Start elsticsearch
^^^^^^^^^^^^^^^^^^^

Debian wheezy / Ubuntu
~~~~~~~~~~~~~~~~~~~~~~

Start elasticsearch service::

    sudo service elasticsearch start

.. note::

    If you want to automatically start elasticsearch during bootup::
        
        sudo update-rc.d elasticsearch defaults 95 10

Arch / Debian jessie
~~~~~~~~~~~~~~~~~~~~

Start elasticsearch service::
    
    sudo systemctl start elasticsearch

.. note::

    If you want to automatically start elasticsearch during bootup::
        
        sudo systemctl enable elasticsearch


Start libreant
^^^^^^^^^^^^^^
To execute libreant::

    ./ve/bin/libreant

