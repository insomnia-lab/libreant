from webant.test.api import WebantTestApiCase, ApiClientError
from nose.tools import eq_
from flask.json import dumps, loads


class TestApiUsers(WebantTestApiCase):

    def test_add_user(self):
        self.add_user({'name':'testName', 'password': 'testPassword'})

    def test_add_user_wrong_content_type(self):
        r = self.wtc.post(self.USR_URI,
                          data=dumps({'name':'testName', 'password': 'testPassword'}))
        eq_(r.status_code, 415)
        r = self.wtc.post(self.USR_URI,
                          data="asdasd",
                          content_type="application/json")
        eq_(r.status_code, 400)

    def test_get_user_not_exist(self):
        r = self.wtc.get(self.API_PREFIX + '/users/12')
        eq_(r.status_code, 404)

    def test_get_user(self):
        userData = {'name':'testName', 'password': 'testPassword'}
        uid = self.add_user(userData)
        rg = self.wtc.get(self.API_PREFIX + '/users/' + str(uid))
        eq_(rg.status_code, 200)

    def test_get_users(self):
        rg = self.wtc.get(self.USR_URI)
        eq_(rg.status_code, 200)
        eq_(len((loads(rg.data))['data']), 2) # the 2 default user

    def test_add_user_no_name(self):
        with self.assertRaises(ApiClientError) as ace:
            self.add_user({'password':'testPassword'})
        eq_(ace.exception.res.status_code, 400)

    def test_add_user_no_pass(self):
        with self.assertRaises(ApiClientError) as ace:
            self.add_user({'name':'testName'})
        eq_(ace.exception.res.status_code, 400)

    def test_add_user_same_name(self):
        user_data = {'name':'testName', 'password': 'testPassword'}
        self.add_user(user_data)
        with self.assertRaises(ApiClientError) as ace:
            self.add_user(user_data)
        eq_(ace.exception.res.status_code, 409)

    def test_delete_user(self):
        userData = {'name':'testName', 'password': 'testPassword'}
        uid = self.add_user(userData)
        r = self.wtc.delete(self.API_PREFIX + '/users/' + str(uid))
        eq_(r.status_code, 200)

    def test_delete_user_not_exists(self):
        r = self.wtc.delete(self.API_PREFIX + '/users/' + str(56))
        eq_(r.status_code, 404)

    def test_update_user(self):
        userData = {'name':'testName', 'password': 'testPassword'}
        uid = self.add_user(userData)
        userData = {'name':'testName2', 'password': 'testPassword2'}
        r = self.wtc.patch(self.API_PREFIX + '/users/' + str(uid),
                         data=dumps(userData),
                         content_type="application/json")
        eq_(r.status_code, 200)

    def test_update_user_wrong_content_type(self):
        userData = {'name':'testName', 'password': 'testPassword'}
        uid = self.add_user(userData)
        userData = {'name':'testName2', 'password': 'testPassword2'}
        r = self.wtc.patch(self.API_PREFIX + '/users/' + str(uid),
                         data=dumps(userData))
        eq_(r.status_code, 415)
        r = self.wtc.patch(self.API_PREFIX + '/users/' + str(uid),
                         data="asdasd",
                         content_type="application/json")
        eq_(r.status_code, 400)

    def test_update_user_not_exist(self):
        userData = {'name':'testName', 'password': 'testPassword'}
        self.add_user(userData)
        userData = {'name':'testName2', 'password': 'testPassword2'}
        r = self.wtc.patch(self.API_PREFIX + '/users/' + str(50),
                           content_type="application/json",
                           data=dumps(userData))
        eq_(r.status_code, 404)
