import json
import unittest
from ddt import ddt, data
from rest_framework import serializers
from ..models import User
from .. import views
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

    @data('', 'storage/', 'vending/', )
    def test_get_200_me(self, value):
        login(self, "s1", "p1", self.oauth2_client)
        response = self.client.get('/user/me/' + value)
        self.assertEqual(response.status_code, 200)

    @data('', 'storage/', 'vending/', )
    def test_get_200_pk(self, value):
        login(self, "s1", "p1", self.oauth2_client)
        response = self.client.get('/user/1/' + value)
        self.assertEqual(response.status_code, 200)

    @data('', 'storage/', 'vending/', )
    def test_get_403(self, value):
        login(self, "s1", "p1", self.oauth2_client)
        response = self.client.get('/user/2/' + value)
        self.assertEqual(response.status_code, 403)

    @data('', 'storage/', 'vending/', )
    def test_get_401_me(self, value):
        response = self.client.get('/user/me/' + value)
        self.assertEqual(response.status_code, 401)

    @data('', 'storage/', 'vending/', )
    def test_get_401_pk(self, value):
        response = self.client.get('/user/1/' + value)
        self.assertEqual(response.status_code, 401)

    @data('vending/', )
    def test_post_400_me(self, value):
        login(self, "s1", "p1", self.oauth2_client)
        response = self.client.post('/user/me/' + value)
        self.assertEqual(response.status_code, 400)

    @data('vending/', )
    def test_post_400_pk(self, value):
        login(self, "s1", "p1", self.oauth2_client)
        response = self.client.post('/user/1/' + value)
        self.assertEqual(response.status_code, 400)

    @data('vending/', )
    def test_post_403(self, value):
        login(self, "s1", "p1", self.oauth2_client)
        response = self.client.post('/user/2/' + value)
        self.assertEqual(response.status_code, 403)

    @data('vending/', )
    def test_post_401_me(self, value):
        response = self.client.post('/user/me/' + value)
        self.assertEqual(response.status_code, 401)

    @data('vending/', )
    def test_post_401_pk(self, value):
        response = self.client.post('/user/1/' + value)
        self.assertEqual(response.status_code, 401)


class Vending(TestCase):
    fixtures = ['user.json', 'items.json']

    def setUp(self):
        self.oauth2_client = Application.objects.create(client_id="foo", user=User.objects.get(pk=1), name="test",
                                                        client_type="public", authorization_grant_type="password",
                                                        client_secret="bar")

    def test_post_empty(self):
        login(self, "s1", "p1", self.oauth2_client)
        response = self.client.post('/user/me/vending/', '', "application/json")
        self.assertEqual(response.status_code, 400)

    def test_post_repeat_item(self):
        items = [
            {
                "nameid": 501,
                "amount": 1,
                "refine": 0,
                "attribute": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, {
                "nameid": 501,
                "amount": 1,
                "refine": 0,
                "attribute": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        login(self, "s1", "p1", self.oauth2_client)
        response = self.client.post('/user/me/vending/', json.dumps(items), "application/json")
        self.assertEqual(response.status_code, 400)

    def test_post_dont_have(self):
        items = [
            {
                "nameid": 502,
                "amount": 1,
                "refine": 0,
                "attribute": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        login(self, "s1", "p1", self.oauth2_client)
        response = self.client.post('/user/me/vending/', json.dumps(items), "application/json")
        self.assertEqual(response.status_code, 400)

    def test_post_ok(self):
        items = [
            {
                "nameid": 501,
                "amount": 1,
                "refine": 0,
                "attribute": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        login(self, "s1", "p1", self.oauth2_client)
        response = self.client.post('/user/me/vending/', json.dumps(items), "application/json")
        self.assertEqual(response.status_code, 204)


class ViewsMethods(unittest.TestCase):
    def test_check_no_repeated_item_ok(self):
        items = [
            {'nameid': 501, 'amount': 3, 'refine': 0, 'attribute': 0, 'card0': 0, 'card1': 0, 'card2': 0, 'card3': 0},
            {'nameid': 502, 'amount': 3, 'refine': 0, 'attribute': 0, 'card0': 0, 'card1': 0, 'card2': 0, 'card3': 0},
        ]
        views.check_no_repeated_items(items)

    def test_check_no_repeated_item_exception(self):
        items = [
            {'nameid': 501, 'amount': 3, 'refine': 0, 'attribute': 0, 'card0': 0, 'card1': 0, 'card2': 0, 'card3': 0},
            {'nameid': 501, 'amount': 4, 'refine': 0, 'attribute': 0, 'card0': 0, 'card1': 0, 'card2': 0, 'card3': 0},
        ]
        with self.assertRaises(serializers.ValidationError):
            views.check_no_repeated_items(items)
