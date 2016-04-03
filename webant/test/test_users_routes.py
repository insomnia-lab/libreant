from . import WebantTestCase, WebantUsersTestCase


class TestSingleUserMode(WebantTestCase):
    '''those tests express the behavior when no USERS_DATABASE is supplied'''

    def test_no_login(self):
        self.assertEqual(self.wtc.get('/login').status_code, 404)

    def test_no_logout(self):
        self.assertEqual(self.wtc.get('/logout').status_code, 404)

    def test_no_users(self):
        res = self.wtc.get('/api/v1/users/1')
        self.assertEqual(res.status_code, 404)

    def test_no_groups(self):
        res = self.wtc.get('/api/v1/groups/1')
        self.assertEqual(res.status_code, 404)


class TestUsersMode(WebantUsersTestCase):

    def test_login_pages(self):
        self.assertEqual(self.wtc.get('/login').status_code, 200)
        res = self.wtc.get('/logout')
        self.assertEqual(res.status_code, 400)
        assert 'not logged' in res.data
