'''
Collection of tests to verify presets validation
'''

from nose.tools import eq_, raises
from presets.presetManager import Preset
from presets.presetManager import PresetMissingFieldException
from presets.presetManager import PresetFieldTypeException
from presets.presetManager import PresetException

def test_validate_empty():
    ''' preset without empty must validate empty data'''
    preset = {
        "id": "id_test",
        "properties": []
    }
    data = {}
    p = Preset(preset)
    p.validate(data)

# string type tests

def test_validate_string_not_required_missing():
    ''' if string property is not required we can skip it'''
    preset = {
        "id": "id_test",
        "properties": [ { "id": "prop_test_string",
                          "required": False,
                          "type" : "string" } ]
    }
    data = {}
    p = Preset(preset)
    p.validate(data)

def test_validate_string_not_required():
    ''' if string property are not required we can insert it anyway'''
    preset = {
        "id": "id_test",
        "properties": [ { "id": "prop_test_string",
                          "required": False,
                          "type" : "string" } ]
    }
    data = { "prop_test_string" : "any_text_I_want" }
    p = Preset(preset)
    p.validate(data)

@raises(PresetMissingFieldException)
def test_validate_string_required_missing():
    ''' if property of type string is required
        and we do not provide it, exception must be raised.
    '''
    preset = {
        "id": "id_test",
        "properties": [ { "id": "prop_test_string",
                          "required": True,
                          "type" : "string" } ]
    }
    data = {}
    p = Preset(preset)
    p.validate(data)

# enum type tests

def test_validate_enum_not_required_missing():
    ''' if enum property is not required we can skip it'''
    preset = {
        "id": "id_test",
        "properties": [ { "id": "prop_test_enum",
                          "required": False,
                          "type" : "enum",
                          "values": ['alfa','beta','gamma'] } ]
    }
    data = {}
    p = Preset(preset)
    p.validate(data)

def test_validate_enum_not_required():
    ''' if enum property is not required we can insert it anyway'''
    preset = {
        "id": "id_test",
        "properties": [ { "id": "prop_test_enum",
                          "required": False,
                          "type" : "enum",
                          "values": ['alfa','beta','gamma'] } ]
    }
    data = { "prop_test_enum": "alfa" }
    p = Preset(preset)
    p.validate(data)

@raises(PresetMissingFieldException)
def test_validate_enum_required_missing():
    ''' if property of type enum is required
        and we do not provide it, exception must be raised.
    '''
    preset = {
        "id": "id_test",
        "properties": [ { "id": "prop_test_enum",
                          "required": True,
                          "type" : "enum",
                          "values": ['alfa','beta','gamma'] } ]
    }
    data = {}
    p = Preset(preset)
    p.validate(data)

@raises(PresetException)
def test_validate_enum_not_required_wrong():
    ''' if property of type enum is not required
        and we provide a wrong value, exception must be raised
    '''
    preset = {
        "id": "id_test",
        "properties": [ { "id": "prop_test_enum",
                          "required": False,
                          "type" : "enum",
                          "values": ['alfa','beta','gamma'] } ]
    }
    data = {"prop_test_enum": "alfas"}
    p = Preset(preset)
    p.validate(data)

@raises(PresetException)
def test_validate_enum_required_wrong():
    ''' if property of type enum is required
        and we provide a wrong value, exception must be raised
    '''
    preset = {
        "id": "id_test",
        "properties": [ { "id": "prop_test_enum",
                          "required": True,
                          "type" : "enum",
                          "values": ['alfa','beta','gamma'] } ]
    }
    data = {"prop_test_enum": "alsdkasld"}
    p = Preset(preset)
    p.validate(data)
