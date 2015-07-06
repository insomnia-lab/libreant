'''
Collection of tests to verify preset paths loading
'''

from nose.tools import raises, eq_
from tempfile import NamedTemporaryFile, mkdtemp
from shutil import rmtree
from presets.presetManager import PresetException
import json
from presets.presetManager import PresetManager


minimalBody = { "id": "id_test",
                "properties": [] }
tmpDir = None


def setUpModule():
    global tmpDir
    tmpDir = mkdtemp(prefix='libreant_presets_tests')


def tearDownModule():
    rmtree(tmpDir)


def json_tmp_file():
    return NamedTemporaryFile(delete=False, dir=tmpDir, suffix=".json")


def test_sigle_file():
    ''' test single file loding'''
    file = json_tmp_file()
    file.write(json.dumps(minimalBody))
    file.close()
    p = PresetManager(file.name, strict=True)
    assert minimalBody['id'] in p.presets


def test_multiple_file():
    '''test multiple file loading'''
    files = list()
    presetBodies = list()
    num = 5
    for i in range(0, num):
        files.append(json_tmp_file())
        presetBodies.append(minimalBody.copy())
        presetBodies[i]['id'] = "id_" + str(i)
        files[i].write(json.dumps(presetBodies[i]))
        files[i].close()
    p = PresetManager(map(lambda x: x.name, files), strict=True)
    for i in range(0, num):
        assert presetBodies[i]['id'] in p.presets


@raises(PresetException)
def test_duplicate_id():
    f1 = json_tmp_file()
    f1.write(json.dumps(minimalBody))
    f1.close()
    f2 = json_tmp_file()
    f2.write(json.dumps(minimalBody))
    f2.close()
    PresetManager([f1.name,f2.name], strict=True)


def test_empty_path():
    ''' passing empty path must not break anything '''
    p = PresetManager([""])
    eq_(len(p.presets), 0)


@raises(PresetException)
def test_not_existent():
    ''' if preset file do not exists we expect an exception '''
    PresetManager("notexistent", strict=True)


def test_folders():
    ''' test preset files distributed in multiple folders '''
    folders = list()
    presetBodies = list()
    num = 5
    for i in range(num):
        folders.append(mkdtemp(dir=tmpDir))
        presetBodies.append(minimalBody.copy())
        presetBodies[i]['id'] = "id_" + str(i)
        file = NamedTemporaryFile(delete=False, dir=folders[i], suffix=".json")
        file.write(json.dumps(presetBodies[i]))
        file.close()

    p = PresetManager(folders, strict=True)
    for i in range(num):
        assert presetBodies[i]['id'] in p.presets
        rmtree(folders[i], ignore_errors=True)


@raises(PresetException)
def test_wrong_json_format():
    ''' if preset has a bad json format we expect an exception'''
    f = json_tmp_file()
    f.write("{{{{}")
    f.close()
    PresetManager(f.name, strict=True)
