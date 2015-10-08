from webant.test import WebantTestCase
from flask.json import loads, dumps


class WebantTestApiCase(WebantTestCase):

    API_PREFIX = '/api/v1'

    GRP_URI = API_PREFIX + '/groups/'
    USR_URI = API_PREFIX + '/users/'

    def add_user(self, userData):
        res = self.wtc.post(self.API_PREFIX + '/users/',
                          data=dumps(userData),
                          content_type="application/json")
        if not res.status_code == 201:
            raise ApiClientError(res)
        return loads(res.data)['data']['id']

    def add_group(self, groupData):
        res = self.wtc.post(self.GRP_URI,
                          data=dumps(groupData),
                          content_type="application/json")
        if not res.status_code == 201:
            raise ApiClientError(res)
        return loads(res.data)['data']['id']


class ApiClientError(Exception):

    def __init__(self, res):
        super(ApiClientError, self).__init__(loads(res.data))
        self.res = res
