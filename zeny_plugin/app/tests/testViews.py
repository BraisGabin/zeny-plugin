import json
from ddt import ddt, data
from ..models import User
from django.test import TestCase
from oauth2_provider.models import Application


def create_oauth2_header(test, username, password, client_id):
    get_token_data = {
        'client_id': client_id,
        'grant_type': 'password',
        'username': username,
        'password': password,
    }

    resp = test.client.post('/oauth/token/', get_token_data)
    token_type = json.loads(resp.content)['token_type']
    token = json.loads(resp.content)['access_token']

    return '%s %s' % (token_type, token)


def login(test, username, password, oauth2_client):
    header = create_oauth2_header(test, username, password, oauth2_client.client_id)
    test.client.defaults['HTTP_AUTHORIZATION'] = header


def logout(test):
    test.client.defaults.pop()
    test.client.credentials('HTTP_AUTHORIZATION')


@ddt
class UserSecurityAccess(TestCase):
    fixtures = ['user.json']

    def setUp(self):
        self.oauth2_client = Application.objects.create(client_id="foo", user=User.objects.get(pk=1), name="test",
                                                        client_type="public", authorization_grant_type="password",
                                                        client_secret="bar")

    @data('', 'storage/',)
    def test_get_200_me(self, value):
        login(self, "s1", "p1", self.oauth2_client)
        response = self.client.get('/user/me/' + value)
        self.assertEqual(response.status_code, 200)

    @data('', 'storage/',)
    def test_get_200_pk(self, value):
        login(self, "s1", "p1", self.oauth2_client)
        response = self.client.get('/user/1/' + value)
        self.assertEqual(response.status_code, 200)

    @data('', 'storage/',)
    def test_get_403(self, value):
        login(self, "s1", "p1", self.oauth2_client)
        response = self.client.get('/user/2/' + value)
        self.assertEqual(response.status_code, 403)

    @data('', 'storage/',)
    def test_get_401_me(self, value):
        response = self.client.get('/user/me/' + value)
        self.assertEqual(response.status_code, 401)

    @data('', 'storage/',)
    def test_get_401_pk(self, value):
        response = self.client.get('/user/1/' + value)
        self.assertEqual(response.status_code, 401)

