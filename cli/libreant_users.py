import click
import logging
import json

import users.api
import users

from conf import config_utils
from conf.defaults import get_def_conf, get_help
from utils.loggers import initLoggers

json_dumps = json.dumps
usersDB = None
conf = dict()


def pretty_json_dumps(*args, **kargs):
    kargs['indent'] = 3
    return json.dumps(*args, **kargs)


def die(msg, exit_code=1):
        click.secho('ERROR: ' + msg, err=True, fg='red')
        exit(exit_code)


@click.group(name="libreant-users", help="manage libreant users")
@click.version_option()
@click.option('-s', '--settings', type=click.Path(exists=True, readable=True), help='file from wich load settings')
@click.option('-d', '--debug', is_flag=True, help=get_help('DEBUG'))
@click.option('--users-db', type=click.Path(), metavar="<url>", help=get_help('USERS_DATABASE') )
@click.option('-p', '--pretty', is_flag=True, help="format the output on multiple lines")
def libreant_users(debug, settings, users_db, pretty):
    initLoggers(logNames=['config_utils'])
    global conf
    conf = config_utils.load_configs('LIBREANT_', defaults=get_def_conf(), path=settings)
    cliConf = {}
    if debug:
        cliConf['DEBUG'] = True
    if users_db:
        cliConf['USERS_DATABASE'] = users_db
    conf.update(cliConf)
    if conf['USERS_DATABASE'] is None:
        die('--users-db not set')
    if pretty:
        global json_dumps
        json_dumps = pretty_json_dumps
    initLoggers(logging.DEBUG if conf.get('DEBUG', False) else logging.WARNING)

    global usersDB
    try:
        usersDB = users.init_db(conf['USERS_DATABASE'],
                                   pwd_salt_size=conf['PWD_SALT_SIZE'],
                                   pwd_rounds=conf['PWD_ROUNDS'])
        users.populate_with_defaults()
    except Exception as e:
        if conf['DEBUG']:
            raise
        else:
            die(str(e))


class ExistingUserType(click.ParamType):
    name = 'existinguser'

    def convert(self, value, param, ctx):
        try:
            return users.api.get_user(name=value)
        except users.api.NotFoundException:
            self.fail('Cannot find user "%s"' % value)


class ExistingGroupType(click.ParamType):
    name = 'existinggroup'

    def convert(self, value, param, ctx):
        try:
            return users.api.get_group(name=value)
        except users.api.NotFoundException:
            self.fail('Cannot find group "%s"' % value)


@libreant_users.group(name='user')
def user_subcmd():
    pass


@user_subcmd.command(name='create', help='Create new user')
@click.argument('username')
def user_add(username):
    try:
        users.api.get_user(name=username)
    except users.api.NotFoundException:
        pass
    else:
        click.secho('User already present', err=True)
        exit(1)
    password = click.prompt('Password', hide_input=True,
                            confirmation_prompt=True)
    user = users.api.add_user(username, password)
    click.echo(json_dumps(user.to_dict()))


@user_subcmd.command(name='list', help='List all the users')
@click.option('--password', is_flag=True, help='Show also password (in hashed form)')
def user_list(password):
    if password:
        all_users = [{'name': user.name, 'id': user.id, 'pwd_hash': user.pwd_hash} for user in users.User.select()]
    else:
        all_users = [{'name': user.name, 'id': user.id} for user in users.User.select()]
    click.echo(json_dumps(all_users))


@user_subcmd.command(name='show', help='Show user infos')
@click.argument('user', metavar='USERNAME', type=ExistingUserType())
def user_show(user):
    data = user.to_dict()
    data['groups'] = [group.to_dict() for group in user.groups]
    click.echo(json_dumps(data))


@user_subcmd.command(name='passwd', help='change the password for a user')
@click.argument('user', metavar='USERNAME', type=ExistingUserType())
def user_set_password(user):
    password = click.prompt('Password', hide_input=True,
                            confirmation_prompt=True)
    users.api.update_user(user.id, {'password': password})


@user_subcmd.command(name='check-password',
                        help='check if a password is correct')
@click.argument('user', metavar='USERNAME', type=ExistingUserType())
def user_check_password(user):
    password = click.prompt('Password', hide_input=True,
                            confirmation_prompt=False)
    if user.verify_password(password):
        click.secho('Password correct', fg='green')
    else:
        click.secho('Incorrect password', fg='red', err=True)


@user_subcmd.command(name='delete', help='Delete a user')
@click.argument('user', metavar='USERNAME', type=ExistingUserType())
def user_del(user):
    users.api.delete_user(user.id)


@libreant_users.group(name='group')
def group_subcmd():
    pass


@group_subcmd.command(name='delete', help='Delete a group')
@click.argument('group', metavar='GROUPNAME', type=ExistingGroupType())
def group_del(group):
    users.api.delete_group(group.id)


@group_subcmd.command(name='create', help='Create a group')
@click.argument('groupname')
def group_add(groupname):
    try:
        users.api.get_group(name=groupname)
    except users.api.NotFoundException:
        pass
    else:
        die('Group already present')
    group = users.api.add_group(groupname)
    click.echo(json_dumps(group.to_dict()))


@group_subcmd.command(name='list', help='List groups')
def list_groups():
    click.echo(json_dumps([g.to_dict() for g in users.Group.select()]))


@group_subcmd.command(name='show', help='Show group properties and members')
@click.argument('group', metavar='GROUPNAME', type=ExistingGroupType())
def show_group(group):
    groupdict = group.to_dict()
    groupdict['users'] = [user.to_dict() for user in users.api.get_users_in_group(group.id)]
    click.echo(json_dumps(groupdict))


@group_subcmd.command(name='user-remove', help='Remove a user from a group')
@click.argument('user', metavar='USERNAME', type=ExistingUserType())
@click.argument('group', metavar='GROUPNAME', type=ExistingGroupType())
def remove_from_group(user, group):
    users.api.remove_user_from_group(user.id, group.id)
    userdata = user.to_dict()
    userdata['groups'] = [ug.to_dict() for ug in
                          users.api.get_groups_of_user(user.id)]
    click.echo(json_dumps(userdata))


@group_subcmd.command(name='user-add', help='Add a user to a group')
@click.argument('user', metavar='USERNAME', type=ExistingUserType())
@click.argument('group', metavar='GROUPNAME', type=ExistingGroupType())
def add_to_group(user, group):
    users.api.add_user_to_group(user.id, group.id)
    userdata = user.to_dict()
    userdata['groups'] = [ug.to_dict() for ug in users.api.get_groups_of_user(user.id)]
    click.echo(json_dumps(userdata))


@libreant_users.group(name='capability')
def caps_subcmd():
    pass


@group_subcmd.command(name='cap-list', help='List capabilities owned by group')
@click.argument('group', metavar='GROUPNAME', type=ExistingGroupType())
def list_capabilities(group):
    click.echo(json_dumps([c.to_dict() for c in group.capabilities]))


class ActionParamType(click.ParamType):
    name='action'

    def convert(self, value, param, ctx):
        possibleactions = {v[0]: v for v in users.Action.ACTIONS}
        value = '' if value == '0' else value
        try:
            value = [possibleactions[x] for x in value]
        except KeyError as exc:
            self.fail('"%s is not a valid literal; '
                        'valid values are %s (which stand for %s)' % (
                            exc.args[0],
                            ', '.join(possibleactions.keys()),
                            ', '.join(possibleactions.values())
                        ))
        return users.Action.from_list(value)


@group_subcmd.command(name='cap-add',
                      short_help='Add a new capability to a group',
                      help='Add a new capability to a group\n\n'
                      'An action is expressed as a subset of the string "CRUD"\n'
                      'Examples of valid values are R,CR,CRUD,CD,etc.')
@click.argument('group', metavar='GROUPNAME', type=ExistingGroupType())
@click.argument('domain')
@click.argument('action', type=ActionParamType())
def capability_add(group, domain, action):
    cap = users.api.add_capability(domain, action)
    users.api.add_capability_to_group(cap.id, group.id)

    groupdata = group.to_dict()
    groupdata['capabilities'] = [c.to_dict() for c in group.capabilities]
    click.echo(json_dumps(groupdata))


@caps_subcmd.command(name='delete')
@click.argument('capID')
def capability_del(capid):
    users.api.delete_capability(capid)


@caps_subcmd.command(name='list', help='List every capability')
def capability_list():
    allcaps = users.Capability.select()
    click.echo(json_dumps([c.to_dict() for c in allcaps]))
