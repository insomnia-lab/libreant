import os.path
import logging
import json


class PresetManager(object):
    SKIPPING_PATH_MSG = "skipping preset path: \"{}\" ( {} )"
    MAX_DEPTH = 2

    def __init__(self, paths):

        self.logger = logging.getLogger(__name__)
        self.presets = {}

        # normalize paramter type string -> array
        if isinstance(paths, basestring):
            paths = [paths]

        self._loadPaths(paths)

    def _loadPaths(self, paths, depth=0):
        if depth > self.MAX_DEPTH:
            return

        for i in range(len(paths)):
            path = paths[i]

            # avoid empty string
            if not path:
                continue

            # cleanUp path
            if depth == 0:
                path = os.path.expanduser(path)  # replace ~
                path = os.path.expandvars(path)  # replace vars
                path = os.path.normpath(path)  # replace /../ and so on
                path = os.path.realpath(path)  # resolve links

            if not os.path.exists(path):
                self._warn(path, "file does not exists")
            elif os.path.isdir(path):
                try:
                    for child in os.listdir(path):
                        self._loadPaths([os.path.join(path, child)], depth+1)
                except OSError, e:
                    self._warn(path, "IOError: "+e.strerror)
                    continue
            elif os.path.isfile(path):
                self._loadPreset(path)
            else:
                self._warn(path, "not regular file")

    def _loadPreset(self, path):
        try:
            with open(path, 'r') as f:
                skeleton = json.load(f)
        except IOError, e:
            self._warn(path, "IOError: "+e.strerror)
            return
        except ValueError, e:
            self._warn(path, "JSON decoding error: "+str(e))
            return
        except Exception, e:
            self._warn(path, e.strerror)
            return

        try:
            preset = Preset(path, skeleton)
        except SkeletonException, e:
            self._warn(path, "Skeleton bad format: "+str(e))
            return

        if(preset.id in self.presets):
            self._warn(path, "Duplicate skeleton id: "+preset.id)
        else:
            self.presets[preset.id] = preset

    def _warn(self, path, details):
        self.logger.error(self.SKIPPING_PATH_MSG.format(path, details))


class Preset(object):

    def __init__(self, path, skeleton):
        self.path = path
        self.skeleton = skeleton
        self.required = []
        self.description = ""
        self.allowUpload = True

        requiredFields = ['id', 'properties']
        fieldsType = {
            'id': basestring,
            'description': basestring,
            'allowUpload': bool,
            'properties': dict
        }

        for reqField in requiredFields:
            if reqField not in skeleton:
                raise SkeletonException("missing '{}' field".format(reqField))

        for field, reqType in fieldsType.items():
            if field in skeleton and not isinstance(skeleton[field], reqType):
                raise SkeletonException("'{}' field must be of type {}".format(field, reqType.__name__))

        props = skeleton['properties']
        for key in props:
            if ('description' in props[key]) and not isinstance(props[key]['description'], basestring):
                raise SkeletonException("'{}' field of '{}' property must be a {}".format("description", key, "string"))
            if 'required' in props[key]:
                if not isinstance(props[key]['required'], bool):
                    raise SkeletonException("'{}' field of '{}' property must be a {}".format("required", key, "bool"))
                else:
                    self.required.append(key)

        self.id = skeleton['id']
        self.properties = props

        if 'description' in skeleton:
            self.description = skeleton['description']
        if 'allowUpload' in skeleton:
            self.allowUpload = skeleton['allowUpload']


class SkeletonException(Exception):
    pass
