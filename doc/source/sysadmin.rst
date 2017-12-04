Sysadmin
=========

.. _sys-Installation:

Installation
-------------

Libreant is written in Python and uses Elasticsearch as the underlying search engine.
In the follwoing sections there are the step-by-step guides to install Libreant on different linux-based operating system:

* :ref:`Debian, Ubuntu and all the debian based distributions<sys-install-debian>`
* :ref:`Arch Linux<sys-install-arch>`

.. _sys-install-debian:

Debian & Ubuntu
^^^^^^^^^^^^^^^

System dependencies
"""""""""""""""""""

Install Elasticsearch
~~~~~~~~~~~~~~~~~~~~~

The recommended way of installing Elasticsearch on debian-based distro is through the official APT repository.

.. note::

    If you have any problem installing elasticsearch try to follow the `official deb installation guide`_

.. _official deb installation guide: https://www.elastic.co/guide/en/elasticsearch/reference/6.0/deb.html

.. highlight:: bash

In order to follow the Elasticsearch installation steps we needs to install some common packages::

    sudo apt-get update && sudo apt-get install apt-transport-https wget gnupg ca-certificates

Download and install the Public Signing Key for elasticsearch repo::

    wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -


Add elasticsearch repository::

    echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-6.x.list

And finally you can install the Elasticsearch package with::

    sudo apt-get update && sudo apt-get install openjdk-8-jre-headless procps elasticsearch

.. note::
    
    The procps provides the ``ps`` command that is required by the elasticsearch startup script 

Install Python
~~~~~~~~~~~~~~

Libreant is going to be installed into a python virtual environment, thus we need to install it::

    sudo apt-get update && sudo apt-get install python2.7 virtualenv python-wheel


Install libreant
""""""""""""""""
Create a virtual env::

    virtualenv -p /usr/bin/python2 ve

Install libreant and all python dependencies::

    ./ve/bin/pip install libreant

.. _sys-install-arch:

Arch
^^^^

Install all necessary packages::

    sudo pacman -Sy python2 python2-setuptools python2-virtualenv grep procps elasticsearch

.. note::
    
    The procps and grep packages are required by the elasticsearch startup script 

Create a virtual env::

    virtualenv2 -p /usr/bin/python2 ve

Install libreant and all python dependencies::

    ./ve/bin/pip install libreant


.. _sys-execution:

Execution
---------

Start elasticsearch service::

    sudo service elasticsearch start

.. note::

    If you want to automatically start elasticsearch during bootup::

        sudo systemctl enable elasticsearch


To execute libreant::

    ./ve/bin/libreant


Upgrading
---------

Generally speaking, to upgrade libreant you just need to::

    ./ve/bin/pip install -U libreant

And restart your instance (see the :ref:`sys-execution` section).

Some versions, however, could need additional actions. We will list them all in
this section.

Upgrade to version 0.5
^^^^^^^^^^^^^^^^^^^^^^

libreant now supports elasticsearch 2. If you were already using libreant 0.4, you were using elasticsearch 1.x.
You *can* continue using it if you want. The standard upgrade procedure is enough to have everything working.
However, we suggest you to upgrade to elasticsearch2 sooner or later.


Step 1: stop libreant
"""""""""""""""""""""

For more info, see :ref:`sys-execution`; something like ``pkill libreant`` should do

Step 2: upgrade elasticsearch
"""""""""""""""""""""""""""""

Just apply the steps in :ref:`sys-installation` section as if it was a brand new installation.

.. note::

    If you are using archlinux, you've probably made pacman ignore elasticsearch package updates.
    In order to install the new elasticsearch version you must remove the ``IgnorePkg elasticsearch`` line in ``/etc/pacman.conf``
    *before* trying to upgrade.

Step 3: upgrade DB contents
"""""""""""""""""""""""""""

Libreant ships a tool that will take care of the upgrade. You can run it with
``./ve/bin/libreant-db upgrade``.

This tool will give you information on the current DB status and ask you for
confirmation before proceding to real changes. Which means that you can run it
without worries, you're still in time for answering "no" if you change your mind.

The upgrade tool will ask you about converting entries to the new format, and upgrading the index mapping (in elasticsearch jargon, this is somewhat similar to what a ``TABLE SCHEMA`` is in SQL)
