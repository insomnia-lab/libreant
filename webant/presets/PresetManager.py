import os.path
import warnings
import json


class PresetManager(object):
    SKIPPING_PATH_MSG = "PresetManager: skipping preset path: \"{}\" ({})"
    MAX_DEPTH = 2

    def __init__(self, paths):
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

            #avoid empty string
            if not path:
                continue

            # cleanUp path
            if depth == 0:
                path = os.path.expanduser(path) # replace ~
                path = os.path.expandvars(path) # replace vars
                path = os.path.normpath(path) # replace /../ and so on
                path = os.path.realpath(path) # resolve links

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
        warnings.warn(self.SKIPPING_PATH_MSG.format(path, details), RuntimeWarning)


class Preset(object):

    def __init__(self, path, skeleton):
        self.path = path
        self.skeleton = skeleton
        self.required = []
        self.description = ""
        self.allowUpload = True

        # ID
        if 'id' not in skeleton:
            raise SkeletonException("missing 'id' field")
        if not isinstance(skeleton['id'], basestring):
            raise SkeletonException("'id' field must be a string")
        self.id = skeleton['id']

        # DESCRIPTION
        if 'description' in skeleton:
            if isinstance(skeleton['description'], basestring):
                self.description = skeleton['description']
            else:
                raise SkeletonException("'description' field must be a string")

        # ALLOW UPLAOD
        if 'allowUpload' in skeleton:
            if isinstance(skeleton['allowUpload'], bool):
                self.allowUpload = skeleton['allowUpload']
            else:
                raise SkeletonException("'allowUpload' field must be a boolean")

        # PROPERTIES
        if 'properties' not in skeleton:
            raise SkeletonException("missing 'properties' field")
        props = skeleton['properties']
        if not isinstance(props, dict):
            raise SkeletonException("'properties' field must be a json object")
        if not len(props) > 0:
            raise SkeletonException("'properties' field could not be empty")

        for key in props:
            if ('description' in props[key]) and not isinstance(props[key]['description'], basestring):
                raise SkeletonException("'{}' field of '{}' property must be a {}".format("description", key, "string"))
            if 'required' in props[key]:
                if not isinstance(props[key]['required'], bool):
                    raise SkeletonException("'{}' field of '{}' property must be a {}".format("required", key, "bool"))
                else:
                    self.required.append(key)

        self.properties = props


class SkeletonException(Exception):
    pass
