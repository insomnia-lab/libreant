===================
Libreant changelog
===================

0.5
+++
- Added supoort to Elasticsearch 2.x versions. (PR #281)

- Changed default capability for anonymous (non logged) user: now she can read all volumes
  in the collection.

  Tip: if you have an existing and already initialized user database, it won't be changed, i.e.
  if you upgrade from a previous version of libreant and you have existing users, the anonymous
  user won't get the read capability.
  In the case you want to add this capability to the already existing anonymous user you can use the
  following command::

    libreant-users --users-db <users-db-url> group cap-add anonymous "volumes/*" R

CLI:
----
- Added new command `libreant-db import` to import volumes all at once. (PR #291)

Web Interface:
--------------
- While adding a new book if it is available the language will be autocompleted
  using the one suggested by the client's browser. ( based on `Accept-Language` http field).
  Thanks @leonaard (PR #288)

API:
----
- Added endpoints to retrieve collections
    - `/api/v1/groups/`
    - `/api/v1/users/`
    - `/api/v1/capabilities/`

Dependencies:
-------------
- Fsdb: added support till version `1.2.1` (PR #277)
- Gevent: added support for the new version `1.1.1` (PR #298)
- Flask: added support till version `0.11.1` (PR #299)

Bugfixes:
---------
- #255 Libreant starts also if it fails to read the conf file:
    fixed by PR #260.
    If some error is encountered while reading the configuration file the stack trace
    will be printed if the debug mode is active otherwise a colored one-line message
    with the cause of the error will be printed.
    Moreover the path of the configuration file will be printed if available.

- #283 Read configuration file error:
    If the configuration is a valid JSON formatted file but it's not a
    dictionary an exception is raised.
    (PR #286)

- Tests for Webant were leaving leftover files around ( commit 1c050a8 )

- In single-user-mode all the users related REST api enpoints are disabled (PR #278)

- CLI: don't print 'Error' string twice (PR #279)

- #287 missing authentication/authorization layer for REST api.
    For the moment the only supported authentication method is the cookie based one ( login through the web UI )


0.4
+++

Web Interface:
--------------
- The page to modify metadata of volumes has been added. If you have
  enough permission you should see a button with a pencil on the single-volume-view page.
- Added support for paginated results in search page.

CLI:
----
- added new command ``libreant-db insert-volume`` to insert a volume along with its attachments.
- added new command ``libreant-db attach`` to attach new files to an already existing volume.

Logs:
-----
- changed default log level to INFO.
- all startup messages are now printed using loggers.
- using recent versions of gevent (>= 1.1b1) it is now possible to
  have a completely uniform log format.

Warning:
--------
- Due to breaking changes introduced in new version of Elasticsearch (deprecation of ``_timestamp`` field),
  it is not possible to use libreant with version of Elasticsearch major or equal to ``2.0``.
  Probably in the next release we'll provide support for these versions.


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
