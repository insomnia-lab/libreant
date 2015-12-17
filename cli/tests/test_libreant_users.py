import os.path

from click.testing import CliRunner

from cli.libreant_users import libreant_users


def get_runner():
    runner = CliRunner()
    runner.isolation(env={})
    return runner


def test_usersdb_mandatory():
    result = get_runner().invoke(libreant_users, ['user', 'list'])
    assert result.exit_code != 0
    assert '--users-db' in result.output


def test_usersdb_works():
    runner = get_runner()
    with runner.isolated_filesystem():
        assert not os.path.exists('u.db')
        base = ['--users-db', 'sqlite:///u.db', 'user']
        result = runner.invoke(libreant_users, base +['list'])
        assert os.path.exists('u.db')
        assert result.exit_code == 0
