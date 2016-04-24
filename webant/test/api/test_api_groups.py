from webant.test.api import WebantTestApiCase, ApiClientError
from nose.tools import eq_
from flask.json import loads, dumps


class TestApiGroups(WebantTestApiCase):

    def test_get_group_not_exist(self):
        r = self.wtc.get(self.GRP_URI + 'a1s2d')
        eq_(r.status_code, 404)
        r = self.wtc.get(self.GRP_URI + '10233')
        eq_(r.status_code, 404)

    def test_add_group(self):
        self.add_group({'name':'groupName'})

    def test_add_group_wrong_content_type(self):
        r = self.wtc.post(self.GRP_URI,
                          data=dumps({'name':'groupStoName'}))
        eq_(r.status_code, 415)
        r = self.wtc.post(self.GRP_URI,
                          data="asdasd",
                          content_type="application/json")
        eq_(r.status_code, 400)

    def test_add_group_no_name(self):
        with self.assertRaises(ApiClientError) as ace:
            self.add_group({'altro':'altroValue'})
            eq_(ace.res.status_code, 400)

    def test_add_group_same_name(self):
        self.add_group({'name':'groupName'})
        with self.assertRaises(ApiClientError) as ace:
            self.add_group({'name':'groupName'})
            eq_(ace.res.status_code, 409)

    def test_get_group(self):
        gid = self.add_group({'name':'groupName'})
        rg = self.wtc.get(self.GRP_URI + str(gid))
        eq_(rg.status_code, 200)

    def test_get_grups(self):
        rg = self.wtc.get(self.GRP_URI)
        eq_(rg.status_code, 200)
        eq_(len((loads(rg.data))['data']), 2) # the 2 default groups

    def test_delete_group(self):
        gid = self.add_group({'name':'groupName'})
        r = self.wtc.delete(self.GRP_URI + str(gid))
        eq_(r.status_code, 200)

    def test_delete_grop_not_exists(self):
        r = self.wtc.delete(self.GRP_URI + str(56))
        eq_(r.status_code, 404)

    def test_update_group(self):
        gid = self.add_group({'name':'groupName'})
        r = self.wtc.patch(self.GRP_URI + str(gid),
                           data=dumps({'name':'otherGroupName'}),
                           content_type="application/json")
        eq_(r.status_code, 200)
        r = self.wtc.get(self.GRP_URI + str(gid))
        eq_(loads(r.data)['data']['name'], 'otherGroupName')

    def test_update_group_wrong_content_type(self):
        gid = self.add_group({'name':'groupName'})
        r = self.wtc.patch(self.GRP_URI + str(gid),
                           data=dumps({'name':'groupStoName'}))
        eq_(r.status_code, 415)
        r = self.wtc.patch(self.GRP_URI + str(gid),
                           data="asdasd",
                           content_type="application/json")
        eq_(r.status_code, 400)

    def test_update_group_not_exist(self):
        self.add_group({'name':'groupName'})
        r = self.wtc.patch(self.GRP_URI + str(50),
                           content_type="application/json",
                           data=dumps({'name':'seStaAFaTardi'}))
        eq_(r.status_code, 404)

    def test_add_user_to_group(self):
        gid = self.add_group({'name':'groupName'})
        uid = self.add_user({'name':'userName', 'password':'pwd'})
        r = self.wtc.put(self.GRP_URI + str(gid) + '/users/' + str(uid))
        eq_(r.status_code, 200)

    def test_add_user_to_group_not_exist(self):
        uid = self.add_user({'name':'userName', 'password':'pwd'})
        gid = self.add_group({'name':'groupName'})
        r = self.wtc.put(self.GRP_URI + str(123) + '/users/' + str(uid))
        eq_(r.status_code, 404)
        r = self.wtc.put(self.GRP_URI + str(gid) + '/users/' + str(123))
        eq_(r.status_code, 404)

    def test_get_users_in_group(self):
        gid = self.add_group({'name':'groupName'})
        uid = self.add_user({'name':'userName', 'password':'pwd'})
        r = self.wtc.put(self.GRP_URI + str(gid) + '/users/' + str(uid))
        r = self.wtc.get(self.GRP_URI + str(gid) + '/users/')
        eq_(r.status_code, 200)
        eq_(loads(r.data)['data'][0]['id'], uid)

    def test_get_users_from_group_not_exist(self):
        r = self.wtc.get(self.GRP_URI + str(1233) + '/users/')
        eq_(r.status_code, 404)

    def test_get_groups_from_user(self):
        gid = self.add_group({'name':'groupName'})
        uid = self.add_user({'name':'userName', 'password':'pwd'})
        r = self.wtc.put(self.GRP_URI + str(gid) + '/users/' + str(uid))
        r = self.wtc.get(self.USR_URI + str(uid) + '/groups/')
        eq_(r.status_code, 200)
        eq_(loads(r.data)['data'][0]['id'], gid)

    def test_get_groups_from_user_not_exist(self):
        r = self.wtc.get(self.USR_URI + str(1233) + '/groups/')
        eq_(r.status_code, 404)

    def test_remove_user_from_group(self):
        gid = self.add_group({'name':'groupName'})
        uid = self.add_user({'name':'userName', 'password':'pwd'})
        r = self.wtc.put(self.GRP_URI + str(gid) + '/users/' + str(uid))
        r = self.wtc.delete(self.GRP_URI + str(gid) + '/users/' + str(uid))
        eq_(r.status_code, 200)

    def test_remove_user_from_group_not_exist(self):
        gid = self.add_group({'name':'groupName'})
        uid = self.add_user({'name':'userName', 'password':'pwd'})
        r = self.wtc.put(self.GRP_URI + str(gid) + '/users/' + str(uid))
        r = self.wtc.delete(self.GRP_URI + str(gid) + '/users/' + str(3214))
        eq_(r.status_code, 404)
        r = self.wtc.delete(self.GRP_URI + str(3123) + '/users/' + str(uid))
        eq_(r.status_code, 404)
