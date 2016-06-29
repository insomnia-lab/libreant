from webant.test.api import WebantTestApiCase, ApiClientError
import users
from nose.tools import eq_


class TestApiAuthLayer(WebantTestApiCase):

    def test_add_user_as_anon(self):
        ''' Calling an api without capability should return an 401 Unauthorized response'''
        with self.assertRaises(ApiClientError) as ace:
            self.add_user({'name':'testName', 'password': 'testPassword'})
        eq_(ace.exception.res.status_code, 403)

    def test_add_user_with_capability(self):
        usrName = 'testUsr'
        usrPwd = 'testPwd'
        usrID = users.api.add_user(usrName, usrPwd)
        capID = users.api.add_capability('/users/*', users.Action.CREATE)
        groupID = users.api.add_group('TestGroup')

        users.api.add_user_to_group(usrID, groupID)
        users.api.add_capability_to_group(capID, groupID)

        logRes = self.login(usrName, usrPwd)
        eq_(logRes.status_code, 200)
        self.add_user({'name':'testName', 'password': 'testPassword'})
