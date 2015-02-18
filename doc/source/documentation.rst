How to write documentation
===========================

We care a lot about documentation. So this chapter is both about technical
reference and guidelines.

Markup language
----------------

Documentation is written using restructuredText_; it's a very rich markup
language, so learning it all may be difficult. You can start reading a
`quick guide`_; you can then pass to a slightly `longest guide`_.

As with all the code, you can learn much just reading pre-existing one. So go
to next section and you'll know where it is placed.

Documentation directory
------------------------

Documentation is placed in ``doc/source/`` in libreant repository. Yes, it's
just a bunch of ``.rst`` files. The main one is ``index.rst``, and hist main
part is the ``toctree`` directive; the list below it specifies the order in
which to include all the other pages.

.. note::
        If you are trying to add a new page to the documentation, remember to
        add its filename to the ``toctree`` in ``index.rst``

To build html documentation from it, you should first of all ``pip install
Sphinx`` inside your virtualenv. Then you can run ``python setup.py
build_sphinx``. This command will create documentation inside
``build/sphinx/html/``. So run ``firefox build/sphinx/html/index.html`` and you
can read it.

.. seealso:: :ref:`dev-installation`

Documenting code
-------------------

If you are a developer, you know that well-documented code is very important:
it makes newcomers more comfortable hacking your project, it helps clarifying
what's the goal of the code you are writing and how other parts of the project
should use it. Keep in mind that libreant must be easily hackable, and the code
should be kept reusable at all levels as much as possible.

Since 99% of libreant code is Python, we'll focus on it, and especially on
python docstrings.

If you are writing a new module, or anyway creating a new file, the "module
docstring" (that is, the docstring just at the start of the file) should
explain what this module is useful for, which kind of objects will it contain,
and clarify any possible caveat.

The same principle applies to classes and, to a lesser degree, to methods. If a
class docstring is complete enough, it can be the case that function docstring
is redundant. Even in that case, you should at least be very careful in giving
meaningful names to function parameters: they help a lot, and come for free!

.. _restructuredText: http://sphinx-doc.org/rest.html
.. _quick guide: http://docutils.sourceforge.net/docs/user/rst/quickstart.html
.. _longest guide: http://docutils.sourceforge.net/docs/user/rst/quickref.html
