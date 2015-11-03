from webant.test.api import WebantTestApiCase, ApiClientError
from nose.tools import eq_
from flask.json import loads, dumps


class TestApiCapabilities(WebantTestApiCase):

    def test_get_capability_not_exist(self):
        r = self.wtc.get(self.CAP_URI + 'a1s2d')
        eq_(r.status_code, 404)
        r = self.wtc.get(self.CAP_URI + '10233')
        eq_(r.status_code, 404)

    def test_add_capability(self):
        self.add_capability({'domain':'/res1/id1/res2/*', 'actions':['READ','UPDATE']})

    def test_add_capability_wrong_content_type(self):
        r = self.wtc.post(self.CAP_URI,
                          data=dumps({'domain':'/res1/id1/res2/*', 'actions':['READ','UPDATE']}))
        eq_(r.status_code, 415)
        r = self.wtc.post(self.CAP_URI,
                          data="asdasd",
                          content_type="application/json")
        eq_(r.status_code, 400)

    def test_add_capability_no_actions(self):
        with self.assertRaises(ApiClientError) as ace:
            self.add_capability({'domain':'/res1/id1/res2/*'})
            eq_(ace.res.status_code, 400)

    def test_add_capability_no_domain(self):
        with self.assertRaises(ApiClientError) as ace:
            self.add_capability({'actions':['UPDATE', 'DELETE']})
            eq_(ace.res.status_code, 400)

    def test_add_capability_same_name(self):
        capData = {'domain':'/res1/id1/res2/*', 'actions':['READ','UPDATE']}
        self.add_capability(capData)
        self.add_capability(capData)

    def test_get_capability(self):
        capData = {'domain':'res1/id1/res2/*', 'actions':['READ','UPDATE']}
        capID = self.add_capability(capData)
        rg = self.wtc.get(self.CAP_URI + str(capID))
        eq_(rg.status_code, 200)
        capDataRet = loads(rg.data)['data']
        eq_(capDataRet['domain'], capData['domain'])
        eq_(capDataRet['actions'], capData['actions'])

    def test_delete_capability(self):
        capData = {'domain':'*', 'actions':['DELETE']}
        capID = self.add_capability(capData)
        r = self.wtc.delete(self.CAP_URI + str(capID))
        eq_(r.status_code, 200)

    def test_delete_capability_not_exists(self):
        r = self.wtc.delete(self.CAP_URI + str(2))
        eq_(r.status_code, 404)

    def test_update_capability(self):
        capData = {'domain':'res1/id1/res2/*', 'actions':['READ','UPDATE']}
        capID = self.add_capability(capData)
        r = self.wtc.patch(self.CAP_URI + str(capID),
                           data=dumps({'actions':['READ']}),
                           content_type="application/json")
        eq_(r.status_code, 200)
        r = self.wtc.get(self.CAP_URI + str(capID))
        eq_(loads(r.data)['data']['actions'], ['READ'])
        r = self.wtc.patch(self.CAP_URI + str(capID),
                           data=dumps({'domain':'*'}),
                           content_type="application/json")
        eq_(r.status_code, 200)
        r = self.wtc.get(self.CAP_URI + str(capID))
        eq_(loads(r.data)['data']['domain'], '*')

    def test_update_capability_wrong_content_type(self):
        capData = {'domain':'res1/id1/res2/*', 'actions':['READ','UPDATE']}
        capID = self.add_capability(capData)
        r = self.wtc.patch(self.CAP_URI + str(capID),
                           data=dumps(capData))
        eq_(r.status_code, 415)
        r = self.wtc.patch(self.CAP_URI + str(capID),
                           data="asdasd",
                           content_type="application/json")
        eq_(r.status_code, 400)

    def test_update_capability_not_exist(self):
        capData = {'domain':'res1/id1/res2/*', 'actions':['READ','UPDATE']}
        r = self.wtc.patch(self.CAP_URI + str(50),
                           content_type="application/json",
                           data=dumps(capData))
        eq_(r.status_code, 404)

    def test_add_capability_to_group(self):
        gid = self.add_group({'name':'groupName'})
        capData = {'domain':'res1/id1/res2/*', 'actions':['READ','UPDATE']}
        capID = self.add_capability(capData)
        r = self.wtc.put(self.GRP_URI + str(gid) + '/capabilities/' + str(capID))
        eq_(r.status_code, 200)

    def test_add_capabilty_to_group_not_exist(self):
        gid = self.add_group({'name':'groupName'})
        capData = {'domain':'res1/id1/res2/*', 'actions':['READ','UPDATE']}
        capID = self.add_capability(capData)
        r = self.wtc.put(self.GRP_URI + str(123) + '/capabilities/' + str(capID))
        eq_(r.status_code, 404)
        r = self.wtc.put(self.GRP_URI + str(gid) + '/capabilities/' + str(123))
        eq_(r.status_code, 404)

    def test_get_capability_in_group(self):
        gid = self.add_group({'name':'groupName'})
        capData = {'domain':'res1/*', 'actions':['CREATE']}
        capID = self.add_capability(capData)
        r = self.wtc.put(self.GRP_URI + str(gid) + '/capabilities/' + str(capID))
        r = self.wtc.get(self.GRP_URI + str(gid) + '/capabilities/')
        eq_(r.status_code, 200)
        eq_(loads(r.data)['data'][0]['id'], capID)

    def test_get_capabilities_of_group_not_exist(self):
        r = self.wtc.get(self.GRP_URI + str(1233) + '/capabilities/')
        eq_(r.status_code, 404)

    def test_get_groups_with_capability(self):
        gid = self.add_group({'name':'groupName'})
        capData = {'domain':'res1/*', 'actions':['CREATE']}
        capID = self.add_capability(capData)
        r = self.wtc.put(self.GRP_URI + str(gid) + '/capabilities/' + str(capID))
        r = self.wtc.get(self.CAP_URI + str(capID) + '/groups/')
        eq_(r.status_code, 200)
        eq_(loads(r.data)['data'][0]['id'], gid)

    def test_get_groups_with_capability_not_exist(self):
        r = self.wtc.get(self.CAP_URI + str(1233) + '/groups/')
        eq_(r.status_code, 404)

    def test_remove_capabilty_from_group(self):
        gid = self.add_group({'name':'groupName'})
        capData = {'domain':'res1/*', 'actions':['CREATE']}
        capID = self.add_capability(capData)
        r = self.wtc.put(self.GRP_URI + str(gid) + '/capabilities/' + str(capID))
        r = self.wtc.delete(self.GRP_URI + str(gid) + '/capabilities/' + str(capID))
        eq_(r.status_code, 200)

    def test_remove_capability_from_group_not_exist(self):
        gid = self.add_group({'name':'groupName'})
        capData = {'domain':'res1/*', 'actions':['CREATE']}
        capID = self.add_capability(capData)
        r = self.wtc.put(self.GRP_URI + str(gid) + '/capabilities/' + str(capID))
        r = self.wtc.delete(self.GRP_URI + str(gid) + '/capabilities/' + str(3214))
        eq_(r.status_code, 404)
        r = self.wtc.delete(self.GRP_URI + str(3123) + '/capabilities/' + str(capID))
        eq_(r.status_code, 404)
