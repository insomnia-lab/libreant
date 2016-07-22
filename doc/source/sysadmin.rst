Sysadmin
=========

.. _sys-Installation:

Installation
-------------

System dependencies
^^^^^^^^^^^^^^^^^^^^

Debian wheezy / Debian jessie / Ubuntu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. highlight:: bash

Download and install the Public Signing Key for elasticsearch repo::

    wget -qO - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | sudo apt-key add -

Add elasticsearch repos in /etc/apt/sources.list.d/elasticsearch.list::

    echo "deb http://packages.elasticsearch.org/elasticsearch/2.x/debian stable main" | sudo tee /etc/apt/sources.list.d/elasticsearch.list

Install requirements::
    
    sudo apt-get update && sudo apt-get install python2.7 gcc python2.7-dev python-virtualenv openjdk-7-jre-headless elasticsearch

.. note::
    
    if you have problem installing elasticsearch try to follow the `official installation guide`_

.. _official installation guide: http://www.elastic.co/guide/en/elasticsearch/reference/current/setup-repositories.html

Arch
~~~~~

Install all necessary packages::

    sudo pacman -Sy python2 python2-virtualenv elasticsearch

Python dependencies
^^^^^^^^^^^^^^^^^^^^

Create a virtual env::

    virtualenv -p /usr/bin/python2 ve

Install libreant and all python dependencies::
    
    ./ve/bin/pip install libreant

Upgrading
----------

Generally speaking, to upgrade libreant you just need to::

    ./ve/bin/pip install -U libreant

And restart your instance (see the :ref:`sys-execution` section).

Some versions, however, could need additional actions. We will list them all in
this section.

From 0.4 to 0.5
^^^^^^^^^^^^^^^

libreant now supports elasticsearch2. If you were already using libreant0.4, you were using libreant 1.x.
You *can* continue using it if you want. The standard upgrade procedure is enough to have everything working.
However, we suggest you to upgrade to elasticsearch2 sooner or later.


Step 1: stop libreant
~~~~~~~~~~~~~~~~~~~~~~

For more info, see :ref:`sys-execution`; something like ``pkill libreant`` should do

Step 2: upgrade elasticsearch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Just apply the steps in :ref:`sys-installation` section as if it was a brand new installation.

If you are using archlinux, you must remove the ``IgnorePkg elasticsearch`` line in ``/etc/pacman.conf`` *before* trying to upgrade.

Step 3: upgrade DB contents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Libreant ships a tool that will take care of the upgrade. You can run it with
``./ve/bin/libreant-db upgrade``.

This tool will give you information on the current DB status and ask you for
confirmation before proceding to real changes. Which means that you can run it
without worries, you're still in time for answering "no" if you change your mind.

The upgrade tool will ask you about converting entries to the new format, and upgrading the index mapping (in elasticsearch jargon, this is somewhat similar to what a ``TABLE SCHEMA`` is in SQL)

.. _sys-execution:

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

