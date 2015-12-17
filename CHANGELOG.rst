===================
Libreant changelog
===================

0.3
+++

Major changes:
--------------
- Implemented a role-based access control layer.
  This means that libreant now support the common ``login`` procedure.
  This functionality isn't documented yet, anyway you can use the brand new ``libreant-users`` command to manage users, groups and capabilities,
  and enable this feature at runtime with the ``--users-db`` parameter.
  The default user is (user: admin, password: admin)

Web interface:
--------------
- Added possibility to delete a volume through a button on the single-volume-view page.
- New user menu (only in users-mode)
- New login/logut pages.
- Improoved error messages/pages

Deployment:
-----------
- Removed elasticsearch strong dependecy.
  Now libreant can be started with elasticsearch still not ready or not running.
- Bugfix: make libreant command exits with code 1 on exception.
- Fixed ``elasticsearch-py`` version dependency. Now the version must be ``>=1`` and ``<2``.
- Reloader is used only in debug mode (``--debug``).
- More uniform logs.

Documentation:
--------------
- The suggested version for elasticsearch installation has been updated: ``1.4`` -> ``1.7``
- A lot of packages have been inserted in the official docs.
