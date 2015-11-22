import os.path
import logging
import json

logger = logging.getLogger(__name__)


class PresetManager(object):
    '''PresetManager deals with presets loading, validating, storing

    you can use it like this::

        pm = PresetManager(["/path/to/presets/folder", "/another/path"])

    '''

    MAX_DEPTH = 5

    def __init__(self, paths, strict=False):
        """load, validate, and store presets under ```self.presets```

        :param paths:  list of paths to preset file
                       or folder containing presets.
        :param strict: if strict is False
                       all exceptions and errors
                       will be converted to log messages.
        """

        self.presets = {}
        self.strict = strict

        # normalize paramter type string -> array
        if isinstance(paths, basestring):
            paths = [paths]

        self._load_paths(paths)

        if len(self.presets) > 0:
            logger.debug("successfully loaded {} presets".format(len(self.presets)))

    def _load_paths(self, paths, depth=0):
        '''
        Goes recursevly through the given list of paths
        in order to find and pass all preset files to ```_load_preset()```
        '''

        if depth > self.MAX_DEPTH:
            return

        for path in paths:
            try:
                # avoid empty string
                if not path:
                    continue

                # cleanUp path
                if depth == 0:
                    path = os.path.expanduser(path)  # replace ~
                    path = os.path.expandvars(path)  # replace vars
                    path = os.path.normpath(path)  # replace /../ , "" will be converted to "."

                if not os.path.exists(path):
                    raise PresetException("does not exists or is a broken link or not enough permissions to read")
                elif os.path.isdir(path):
                    try:
                        for child in os.listdir(path):
                            self._load_paths([os.path.join(path, child)], depth + 1)
                    except OSError as e:
                        raise PresetException("IOError: " + e.strerror)
                elif os.path.isfile(path):
                    if path.endswith(".json"):
                        self._load_preset(path)
                else:
                    raise PresetException("not regular file")
            except PresetException as e:
                e.message = "Failed to load preset: \"{}\" [ {} ]".format(path, e.message)
                if self.strict:
                    raise
                logger.error(str(e))

    def _load_preset(self, path):
        ''' load, validate and store a single preset file'''

        try:
            with open(path, 'r') as f:
                presetBody = json.load(f)
        except IOError as e:
            raise PresetException("IOError: " + e.strerror)
        except ValueError as e:
            raise PresetException("JSON decoding error: " + str(e))
        except Exception as e:
            raise PresetException(str(e))

        try:
            preset = Preset(presetBody)
        except PresetException as e:
            e.message = "Bad format: " + e.message
            raise

        if(preset.id in self.presets):
            raise PresetException("Duplicate preset id: " + preset.id)
        else:
            self.presets[preset.id] = preset


class Schema(object):
    '''
    Schema is the parent of all the classes that needs to verify
    a specific object structure.

    all child class in order to use schema validation must:
     - describe the desired object schema using `self.fields`
     - save input object in `self.body`

    `self.fields` must be a dict,
    where keys match the relative `self.body` keys
    and values describe how relative self.body valuse must be.

    Example::

        self.fields = { 'description': {
                            'type': basestring,
                            'required': False,
                            'default': ""
                        },
                        'allow_upload': {
                            'type': bool,
                            'required': False,
                            'default': True
                        }
                      }

    '''

    fields = {}

    def __init__(self):
        self._verify_fields()

    def _verify_fields(self):
        for fieldId, fieldProps in self.fields.items():
            if fieldId not in self.body:
                # control if field is required
                # if required is a function, call it, otherwise use it as a boolean
                reqFunc = isinstance(fieldProps['required'], str)
                if (reqFunc and getattr(self, fieldProps['required'])()) or ((not reqFunc) and fieldProps['required']):
                    raise PresetMissingFieldException("missing field '{}'".format(fieldId))

                # if the default value is provided use it to set attribute
                if 'default' in fieldProps:
                    setattr(self, fieldId, fieldProps['default'])
            else:
                # control field type
                if not isinstance(self.body[fieldId], fieldProps['type']):
                    raise PresetFieldTypeException("field '{}' must be of type {}".format(fieldId, fieldProps['type'].__name__))
                # make additional check on field if necessary
                if 'check' in fieldProps:
                    getattr(self, fieldProps['check'])()
                setattr(self, fieldId, self.body[fieldId])


class Preset(Schema):
    '''A preset is a set of rules and properties denoting a class of object

       Example:
          A preset could be used to describe which properties an object
          that describe a book must have. (title, authors, etc)
    '''

    '''`fields` is used by Schema class to validate `body`.
        you can follow this structure to add new fields.
        if you need to implement more complex logic,
        you can use function name of this class both in `check` and `required`,
        those functions must return a boolean and
        can access `self.body` to calculate the result.
    '''
    fields = {
        'id': {
            'type': basestring,
            'required': True,
            'check': 'check_id'
        },
        'properties': {
            'type': list,
            'required': True
        },
        'description': {
            'type': basestring,
            'required': False,
            'default': ""
        },
        'allow_upload': {
            'type': bool,
            'required': False,
            'default': True
        }
    }

    def __init__(self, body):
        self.body = body
        super(Preset, self).__init__()

        self.properties = list()

        for propBody in body['properties']:
            try:
                prop = Property(propBody)
            except PresetException as e:
                e.message = "in property '{}', {}".format(propBody['id'], e.message)
                raise
            # check if a property with the same ID have already added
            for p in self.properties:
                if p.id == prop.id:
                    raise PresetException("Duplicate property id: '{}'".format(prop.id))
            self.properties.append(prop)

    def check_id(self):
        if not len(self.body['id']) > 0:
            raise PresetException("field 'id' could not be empty")

    def validate(self, data):
        '''
        Checks if `data` respects this preset specification

        It will check that every required property is present and
        for every property type it will make some specific control.
        '''
        for prop in self.properties:
            if prop.id in data:
                if prop.type == 'string':
                    if not isinstance(data[prop.id], basestring):
                        raise PresetFieldTypeException("property '{}' must be of type string".format(prop.id))
                elif prop.type == 'enum':
                    if not isinstance(data[prop.id], basestring):
                        raise PresetFieldTypeException("property '{}' must be of type string".format(prop.id))
                    if data[prop.id] not in prop.values:
                        raise PresetException("property '{}' can be one of {}".format(prop.id, prop.values))
            else:
                if prop.required:
                    raise PresetMissingFieldException("missing required property: '{}'".format(prop.id))


class Property(Schema):
    '''A propety describe the format of a peculiarity of a preset'''

    '''these are all the supported Property types'''
    types = ['string', 'enum']

    '''`fields` is used as in Preset class'''
    fields = {
        'id': {
            'type': basestring,
            'required': True,
            'check': 'check_id'
        },
        'description': {
            'type': basestring,
            'required': False,
            'default': ""
        },
        'required': {
            'type': bool,
            'required': False,
            'default': False
        },
        'type': {
            'type': basestring,
            'required': False,
            'default': "string",
            'check': 'check_type'
        },
        'values': {
            'type': list,
            'required': 'required_values',
            'check': 'check_values'
        }
    }

    def __init__(self, body):
        self.body = body
        super(Property, self).__init__()

    def check_type(self):
        if self.body['type'] not in self.types:
            raise PresetException("field 'type' has not valid value")

    def required_values(self):
        return 'type' in self.body and self.body['type'] == 'enum'

    def check_values(self):
        for e in self.body['values']:
            if not isinstance(e, basestring):
                raise PresetFieldTypeException("field 'values' must be a list of strings ")

    def check_id(self):
        if not len(self.body['id']) > 0:
            raise PresetException("field 'id' could not be empty")


class PresetException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class PresetMissingFieldException(PresetException):
    pass


class PresetFieldTypeException(PresetException):
    pass
