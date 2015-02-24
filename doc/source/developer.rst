How to develop
=================

This chapter is dedicated to developers, and will guide you through code
organization, design choices, etc.  This is not a tutorial to python, nor to
git. It will provide pointers and explanation, but will not teach you how to
program.

Ingredients
------------

libreant is coded in python2.7. Its main components are an elasticsearch_ db, a
Fsdb_ and a web interface based on Flask_.

Details about libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Elasticsearch is a big beast. It has a lot of features and it can be scaring. We can suggest this `elasticsearch guide`_.
The python library for elasticsearch, elasticsearch-py_, is quite simple to
use, and has a nice documentation.

Fsdb_ is a quite simple "file database": the main idea behind it is that it is a content-addressable storage. The address is simply the sha1sum of the content.

Flask_ is a "web microframework for python". It's not a big and complete solution like django, so you'll probably get familiar with it quite soon.

.. _dev-installation:

Installation
-------------

We will assume that you are familiar with virtualenvs. If you are not, please
get familiar!

Inside a clean virtualenv, run

.. code-block:: bash

    python setup.py develop

You are now ready to develop. And you'll find two tools inside your ``$PATH``:
``webant`` and ``libreant-manage``. The first is a webserver that will run the
web interface of libreant, while the second is a command-line tool to do basic
operations with libreant: exporting/importing items, searching, etc.

Code design
------------------

This section is devoted to get a better understanding on why the code is like
it is, the principles that guides us, and things like that.

Design choices
~~~~~~~~~~~~~~~~

few assumptions about data
    We try to be very generic about the items that libreant will store. We do
    not adhere to any standard about book catalogation, nor metadata
    organization, nor nothing like that. We leave the libraries free to set
    metadata how they prefer.  There is only one mandatory field in items,
    which is ``language``. The reason it is this way, is that it's important to
    know the language of the metadata in order for full-text search to work
    properly. There are also two somewhat-special fields: ``title`` and
    ``actors``; they are not required, but are sometimes used in the code
    (being too much agnostic is soo difficult!)
no big framework
    we try to avoid huge frameworks like django or similar stuff. This is both
    a precise need, and a matter of taste. First of all, libreant uses many
    different storage resources (elasticsearch, fsdb, and this list will
    probably grow), so most frameworks will not fit our case.  But it's also
    because we want to avoid that the code is "locked" in a framework and
    therefore difficult to fork.

File organization
~~~~~~~~~~~~~~~~~~

``setup.py`` is the file that defines how libreant is installed, how are
packages built, etc.
The most common reason you could care about it, is if you need to add some
dependency to libreant.


libreantdb
##########

``libreantdb/`` is a package containing an abstraction over elasticsearch.
Again: this is elasticsearch-only, and completely unaware of any other storage,
or the logic of libreant itself.

webant
########

``webant/`` is a package; you could think that it only contains web-specific logic,
but this is not the case. Instead, all that is not in ``libreantdb`` is in
``webant``, which is surely a bit counterintuitive.

The web application (defined in ``webant.py``) "contains" a Blueprint_ called
``agherant``. Agherant is the part of libreant that cares about "aggregating"
multiple nodes in one single search engine. We believe that agherant is an
important component, and if we really want to make libreant a distributed
network, it should be very reusable. That's why agherant is a blueprint: it
should be reusable easily.

``manage.py`` is what will be installed as ``libreant-manage``: a simple
command-line manager for lot of libreant operations. ``libreant-manage`` is
meant to be a tool for developers (reproduce scenarios easily) and sysadmins
(batch operations, debug), surely not for librarians! This program is actually
based on flask-script_, so you may wonder why we use flask for something that
is not web related at all; the point is that we use flask as an application
framework more than a web framework.

``templates/`` is... well, it contains templates. They are written with jinja_
templating language. The `render_template` function 

documentation
##############

Documentation is kept on ``doc/source/`` and is comprised of ``.rst`` files. The
syntax used is restructuredText_. Don't forget to update documentation when you
change something!

API
~~~~

You can read :doc:`api/modules`

Coding style
~~~~~~~~~~~~~

PEP8_ must be used in all the code.

Docstrings are used for autogenerating api documentation, so please don't
forget to provide clear, detailed explanation of what the module/class/function
does, how to use it, when is it useful, etc.
If you want to be really nice, consider using `restructured-text directives`_
to improve the structure of the documentation: they're fun to use.

We care a lot about documentation, so please don't leave documentation
out-of-date. If you change the parameters that a function is accepting, please
document it. If you are making changes to the end user's experience, please
fix the user manual.

Never put "binary" files in the source. With 'binary', we also mean "any files
that could be obtained programmatically, instead of being included". This is,
for example, the case of ``.mo``.

Unit tests are very important: if your function is testable, you should test
it. Yes, even if its behaviour might seem obvious. Unit tests are important
both as a way of avoding regressions and as a way to document how something
behaves.
If the code you are writing is not easy to test, you should think of making it
more easy to test. Running unit tests is easy: ``python setup.py test`` is
enough. This command will run all the tests, and print a coverage summary. Ensure that the module you are writing has high coverage, and investigate what has not been covered.

Contributing
------------

Like ``libreant``? You can help!

We have a bugtracker_, and you are welcome to pick tasks from there :) We use
it also for discussions. Our most typical way of proposing patches is to open a
pull request on github; if, for whatever reason, you are not comfortable with
that, you can just contact us by email and send a patch, or give a link to your
git repository.

.. _elasticsearch: https://www.elasticsearch.org/
.. _elasticsearch guide: https://www.elasticsearch.org/guide/en/elasticsearch/guide/current/index.html
.. _Fsdb: https://github.com/ael-code/pyFsdb/
.. _Flask: http://flask.pocoo.org/
.. _elasticsearch-py: https://elasticsearch-py.readthedocs.org/
.. _fsdb code: https://github.com/ael-code/pyFsdb/blob/master/fsdb/Fsdb.py
.. _Blueprint: http://flask.pocoo.org/docs/0.10/blueprints/
.. _jinja: http://jinja.pocoo.org/
.. _flask-script: https://flask-script.readthedocs.org/en/latest/
.. _bugtracker: https://github.com/insomnia-lab/libreant/issues
.. _PEP8: https://www.python.org/dev/peps/pep-0008/
.. _restructured-text directives: http://sphinx-doc.org/domains.html#signatures
.. _restructuredText: http://sphinx-doc.org/rest.html
