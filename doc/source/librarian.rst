Librarian
=========

This chapter is dedicated to librarians, people who manage the libreant node, decide how to structure the database, organize informations and supervise the catalogue.


Presets system
---------------

One of the things that make libreant powerful is that there are almost no assumptions and restrictions about informations you can catalog with it. You can use libreant to store digital book, organize physical book metadata, CDs, comics, organization reports, posters and so on.

Stored object informations are organized in a collection of key-values pairs::

    title:   Heart of Darkness
    author:  Joseph Conrad
    year:    1899
    country: United Kingdom

Normally, when users insert new objects in the database they can choose the number and the type of key-values pairs to save, without any restrictions. Language field is the only one information that is always required.

All this freedom could be difficult to administrate, so libreant provide the preset system as a useful tool to help librarians.


Preset
~~~~~~~
A preset is a set of rules and properties that denote a class of object.
For example, if you want to store physical book metadata in your libreant node and for every book you want to remember the date in which you bought that book, in this case you can create a preset for class ``bought-book`` that has always a property with id ``date``.


Quick steps creation
~~~~~~~~~~~~~~~~~~~~~
To create a new preset you need to create a new json file, populate it and configure libreant to use it.

Every preset is described by one json formatted text file. So in order to create a new preset you need to create a new text file with ``.json`` extension.
This is the simplest preset you can do::
    
    {
        "id": "bought-book",
        "properties": []
    }


Once you have created all your presets you can use the ``PRESET_PATHS`` configuration variable to make libreant use them. ``PRESET_PATHS`` accepts a list of paths ( strings ), you can pass paths to file or folders containing presets.

Start libreant and go to the add page, you should have a list menu from which you can choose one of your presets.
If some of your presets are not listed, you can take a look at log messages to investigate the problem.


Preset structure
~~~~~~~~~~~~~~~~~
The preset file has some general fields that describe the matadata of the preset (id, description, etc... ) and a list of properties describing informations that objects belonging to this preset must/should have.

Preset example::
    
    {
        "id": "bought-book",
        "allow_upload": false,
        "description": "bought physical book",
        "properties": [{ "id": "title",
                         "description": "title of the book",
                         "required": true  
                       },
                       { "id": "author",
                         "description": "author of the book",
                         "required": true
                       },
                       { "id": "date",
                         "description": "date in which book was bought",
                         "required": true
                       },
                       { "id": "genre",
                         "description": "genre of the book",
                         "required": true,
                         "type": "enum",
                         "values": ["novel", "scientific", "essay", "poetry"]
                       }]
    }

General fields:

===============  ========   ==========  =============   =========================================
Key              Type       Required    Default         Description
===============  ========   ==========  =============   =========================================
id               string     True                        id of the preset
description      string     False       ""              a brief description of the preset
allow_upload     boolean    False       True            permits upload of files during submission
properties       list       True                        list of properties
===============  ========   ==========  =============   =========================================

Property fields:

===============  ========   =================  =============   =======================================================
Key              Type       Required           Default         Description
===============  ========   =================  =============   =======================================================
id               string     True                               id of the property
description      string     False              ""              a brief description of the property
required         boolean    False              False           permits to leave this property empty during submission
type             string     False              "string"        the type of this property
values           list       `Enum type`_                       used if type is "enum"
===============  ========   =================  =============   =======================================================

String type
^^^^^^^^^^^^

String type properties will appear in the add page as a plain text field.

Enum type
^^^^^^^^^^

Enum type properties will appear in the add page as a list of values. Possible values must be placed in *values* field as list of strings. *values* field are required if the type of the same property is "enum". 
