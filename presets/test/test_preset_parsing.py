'''
Collection of tests to verify presets parsing correctness
'''

from nose.tools import eq_, raises
from presets.presetManager import Preset
from presets.presetManager import PresetMissingFieldException
from presets.presetManager import PresetFieldTypeException
from presets.presetManager import PresetException

def test_creation():
    preset = {
        "id": "id_test",
        "properties": []
    }
    p = Preset(preset)
    eq_(p.id, preset['id'])


@raises(PresetMissingFieldException)
def test_field_id_missing():
    ''' id is not optional'''
    preset = {
        "properties": []
    }
    p = Preset(preset)


@raises(PresetException)
def test_field_id_empty():
    ''' id is not optional'''
    preset = {
        "id": "",
        "properties": []
    }
    p = Preset(preset)


@raises(PresetFieldTypeException)
def test_field_id_type():
    ''' id must be a string '''
    preset = {
        "id": {},
        "properties": []
    }
    p = Preset(preset)


def test_field_allowUpload():
    ''' properties must be dict'''
    preset = {
        "id": "id_test",
        "properties": [],
        "allow_upload": True
    }
    p = Preset(preset)
    eq_(p.allow_upload, preset['allow_upload'])

    preset['allow_upload'] = False
    p = Preset(preset)
    eq_(p.allow_upload, preset['allow_upload'])


def test_field_allowUpload_default():
    preset = {
        "id": "id_test",
        "properties": []
    }
    p = Preset(preset)
    eq_(p.allow_upload, True)


@raises(PresetFieldTypeException)
def test_field_allowUpload_type():
    ''' allow_upload must be bool'''
    preset = {
        "id": "id_test",
        "properties": [],
        "allow_upload": "test"
    }
    p = Preset(preset)


@raises(PresetMissingFieldException)
def test_field_properties_missing():
    ''' properties is not optional'''
    preset = {
        "id": "id_test"
    }
    p = Preset(preset)


@raises(PresetFieldTypeException)
def test_field_properties_type():
    ''' properties must be dict'''
    preset = {
        "id": "id_test",
        "properties": "asd"
    }
    p = Preset(preset)


def test_properties_empty():
    preset = {
        "id": "id_test",
        "properties": []
    }
    p = Preset(preset)
    eq_(len(p.properties), 0)


@raises(PresetException)
def test_id_empty():
    preset = {
        "id": "",
        "properties": []
    }
    p = Preset(preset)


@raises(PresetException)
def test_properties_id_empty():
    preset = {
        "id": "id_test",
        "properties": [{"id": ""}]
    }
    p = Preset(preset)


@raises(PresetException)
def test_properties_duplicate_id():
    preset = {
        "id": "id_test",
        "properties": [ {"id": "1_p"},
                        {"id": "1_p"} ]
    }
    p = Preset(preset)


def test_properties_num():
    preset = {
        "id": "id_test",
        "properties": [ {"id": "1_p"},
                        {"id": "2_p"},
                        {"id": "3_p"}
                      ]
    }
    p = Preset(preset)
    eq_(len(p.properties),3)
    for i,prop in enumerate(preset['properties']):
        eq_(prop['id'], p.properties[i].id)


def test_properties_all():
    preset = {
        "id": "id_test",
        "properties": [ { "id": "prop_test",
                          "description": "description test",
                          "required": True,
                          "type" : "string" } ]
    }
    p = Preset(preset)
    eq_(len(p.properties),1)
    eq_(p.properties[0].id, preset['properties'][0]['id'])
    eq_(p.properties[0].description, preset['properties'][0]['description'])
    eq_(p.properties[0].required, preset['properties'][0]['required'])
    eq_(p.properties[0].type, preset['properties'][0]['type'])


def test_properties_defaults():
    preset = {
        "id" : "id_test",
        "properties": [ {"id": "prop_test"} ]
    }
    p = Preset(preset)
    eq_(len(p.properties),1)
    eq_(p.properties[0].id, preset['properties'][0]['id'])
    eq_(p.properties[0].required, False)
    eq_(p.properties[0].type, "string")


@raises(PresetException)
def test_properties_type():
    ''' test type value not valid '''   
    preset = {
        "id" : "id_test",
        "properties": [{ "id": "prop_test",
                         "type" : "### non_esiste ###" }]
    }
    p = Preset(preset)


@raises(PresetMissingFieldException)
def test_properties_type_enum_missing_values():
    preset = {
        "id": "id_test",
        "properties": [{ "id": "prop_test",
                         "type" : "enum"
                        }]
    }
    p = Preset(preset)


@raises(PresetFieldTypeException)
def test_properties_type_enum_values_type():
    preset = {
        "id": "id_test",
        "properties": [{ "id": "prop_test",
                         "type" : "enum",
                         "values": "errorrrre"
                        }]
    }
    p = Preset(preset)


def test_properties_type_enum_values():
    preset = {
        "id": "id_test",
        "properties": [{ "id": "prop_test",
                         "type": "enum",
                         "values": ['uno','due','dieci']
                        }]
    }
    p = Preset(preset)
    eq_(len(p.properties),1)
    eq_(p.properties[0].id, preset['properties'][0]['id'])
    eq_(p.properties[0].type, preset['properties'][0]['type'])
    eq_(p.properties[0].values, preset['properties'][0]['values'])
