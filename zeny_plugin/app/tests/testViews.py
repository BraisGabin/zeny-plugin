import json
import unittest

from ddt import ddt, data
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.test import APITestCase

from ..models import User
from .. import views
from .testcases import MyTransactionTestCase


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


def login(client, userid="s1"):
    client.force_authenticate(User.objects.get(userid=userid))


def logout(client):
    client.force_authenticate(None)


@ddt
class UserSecurityAccess(APITestCase):
    fixtures = ['user.json']

    @data('', 'storage/', 'vending/', )
    def test_get_200_me(self, value):
        login(self.client)
        response = self.client.get('/user/me/' + value)
        self.assertEqual(response.status_code, 200)

    @data('', 'storage/', 'vending/', )
    def test_get_200_pk(self, value):
        login(self.client)
        response = self.client.get('/user/1/' + value)
        self.assertEqual(response.status_code, 200)

    @data('', 'storage/', 'vending/', )
    def test_get_403(self, value):
        login(self.client)
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
        login(self.client)
        response = self.client.post('/user/me/' + value)
        self.assertEqual(response.status_code, 400)

    @data('vending/', )
    def test_post_400_pk(self, value):
        login(self.client)
        response = self.client.post('/user/1/' + value)
        self.assertEqual(response.status_code, 400)

    @data('vending/', )
    def test_post_403(self, value):
        login(self.client)
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


class VendingNoLock(APITestCase):
    fixtures = ['user.json', 'items.json']

    def test_post_empty(self):
        login(self.client)
        response = self.client.post('/user/me/vending/', None, "json")
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
        login(self.client)
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 400)

    def test_post_dont_have(self):
        items = [
            {
                "nameid": 506,
                "amount": 1,
                "refine": 0,
                "attribute": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        login(self.client)
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 400)

    def test_post_dont_have_so_much(self):
        items = [
            {
                "nameid": 501,
                "amount": 6,
                "refine": 0,
                "attribute": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        login(self.client)
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 400)

    def test_post_zero_amount(self):
        items = [
            {
                "nameid": 501,
                "amount": 0,
                "refine": 0,
                "attribute": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        login(self.client)
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 400)

    def test_post_negative_amount(self):
        items = [
            {
                "nameid": 501,
                "amount": -1,
                "refine": 0,
                "attribute": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        login(self.client)
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 400)

    def test_post_no_identified_item(self):
        """
        s1 have two 1101: one identified and other not.
        """
        items = [
            {
                "nameid": 1101,
                "amount": 2,
                "refine": 0,
                "attribute": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        login(self.client)
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 400)

    def test_post_bounded_item(self):
        items = [
            {
                "nameid": 2301,
                "amount": 1,
                "refine": 0,
                "attribute": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        login(self.client)
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 400)

    def test_post_expire_item(self):
        items = [
            {
                "nameid": 1373,
                "amount": 1,
                "refine": 0,
                "attribute": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        login(self.client)
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 400)

    def test_post_online(self):
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
        login(self.client, "s2")
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 409)


class Vending(MyTransactionTestCase):
    fixtures = ['user.json', 'items.json']

    def test_move_first_not_all(self):
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
        login(self.client)
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        storage = user.storage.get(nameid=501)
        self.assertEqual(storage.amount, 4)

        vending = user.vending.get(nameid=501)
        self.assertEqual(vending.amount, 1)
        self.assertEqual(vending.zeny, 0)

    def test_move_first_all(self):
        items = [
            {
                "nameid": 501,
                "amount": 5,
                "refine": 0,
                "attribute": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        login(self.client)
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        with self.assertRaises(ObjectDoesNotExist):
            user.storage.get(nameid=501)

        vending = user.vending.get(nameid=501)
        self.assertEqual(vending.amount, 5)
        self.assertEqual(vending.zeny, 0)

    def test_move_not_first_not_all(self):
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
        login(self.client)
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        storage = user.storage.get(nameid=502)
        self.assertEqual(storage.amount, 4)

        vending = user.vending.get(nameid=502)
        self.assertEqual(vending.amount, 6)
        self.assertEqual(vending.zeny, 0)

    def test_move_not_first_all(self):
        items = [
            {
                "nameid": 502,
                "amount": 5,
                "refine": 0,
                "attribute": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        login(self.client)
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        with self.assertRaises(ObjectDoesNotExist):
            user.storage.get(nameid=502)

        vending = user.vending.get(nameid=502)
        self.assertEqual(vending.amount, 10)
        self.assertEqual(vending.zeny, 0)

    def test_move_not_first_not_all_zeny(self):
        items = [
            {
                "nameid": 503,
                "amount": 1,
                "refine": 0,
                "attribute": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        login(self.client)
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        storage = user.storage.get(nameid=503)
        self.assertEqual(storage.amount, 4)

        vending = user.vending.get(nameid=503)
        self.assertEqual(vending.amount, 6)
        self.assertEqual(vending.zeny, 1000)

    def test_move_not_first_all_zeny(self):
        items = [
            {
                "nameid": 503,
                "amount": 5,
                "refine": 0,
                "attribute": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        login(self.client)
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        with self.assertRaises(ObjectDoesNotExist):
            user.storage.get(nameid=503)

        vending = user.vending.get(nameid=503)
        self.assertEqual(vending.amount, 10)
        self.assertEqual(vending.zeny, 1000)


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
