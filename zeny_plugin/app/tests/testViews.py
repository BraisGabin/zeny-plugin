import unittest
import json

from ddt import ddt, data
from django.conf import settings
from rest_framework import serializers

from .testcases import MyTestCase
from .. import views


@ddt
class UserSecurityAccess(MyTestCase):
    fixtures = ['user.json']

    @data('storage/', 'vending/', )
    def test_get_200_me(self, value):
        self.login()
        response = self.client.get('/user/me/' + value)
        self.assertEqual(response.status_code, 200)

    @data('storage/', 'vending/', )
    def test_get_200_pk(self, value):
        self.login()
        response = self.client.get('/user/1/' + value)
        self.assertEqual(response.status_code, 200)

    @data('storage/', 'vending/', )
    def test_get_403(self, value):
        self.login()
        response = self.client.get('/user/2/' + value)
        self.assertEqual(response.status_code, 403)

    @data('storage/', 'vending/', )
    def test_get_401_me(self, value):
        response = self.client.get('/user/me/' + value)
        self.assertEqual(response.status_code, 401)

    @data('storage/', 'vending/', )
    def test_get_401_pk(self, value):
        response = self.client.get('/user/1/' + value)
        self.assertEqual(response.status_code, 401)

    @data('storage/', 'vending/', )
    def test_post_400_me(self, value):
        self.login()
        response = self.client.post('/user/me/' + value)
        self.assertEqual(response.status_code, 400)

    @data('storage/', 'vending/', )
    def test_post_400_pk(self, value):
        self.login()
        response = self.client.post('/user/1/' + value)
        self.assertEqual(response.status_code, 400)

    @data('storage/', 'vending/', )
    def test_post_403(self, value):
        self.login()
        response = self.client.post('/user/2/' + value)
        self.assertEqual(response.status_code, 403)

    @data('storage/', 'vending/', )
    def test_post_401_me(self, value):
        response = self.client.post('/user/me/' + value)
        self.assertEqual(response.status_code, 401)

    @data('storage/', 'vending/', )
    def test_post_401_pk(self, value):
        response = self.client.post('/user/1/' + value)
        self.assertEqual(response.status_code, 401)

    @data('vending/', )
    def test_put_400_me(self, value):
        self.login()
        response = self.client.put('/user/me/' + value)
        self.assertEqual(response.status_code, 400)

    @data('vending/', )
    def test_put_400_pk(self, value):
        self.login()
        response = self.client.put('/user/1/' + value)
        self.assertEqual(response.status_code, 400)

    @data('vending/', )
    def test_put_403(self, value):
        self.login()
        response = self.client.put('/user/2/' + value)
        self.assertEqual(response.status_code, 403)

    @data('vending/', )
    def test_put_401_me(self, value):
        response = self.client.put('/user/me/' + value)
        self.assertEqual(response.status_code, 401)

    @data('vending/', )
    def test_put_401_pk(self, value):
        response = self.client.put('/user/1/' + value)
        self.assertEqual(response.status_code, 401)


class UserTest(MyTestCase):
    fixtures = ['user.json']

    def test_get_200_me(self):
        self.login()
        response = self.client.get('/user/me/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content, {
            "id": 1,
            "name": 's1',
            "zeny": 10000,
            "chars": [
                {
                    "id": 150000,
                    "name": 'spam',
                    "zeny": 10000,
                }
            ],
        })

    def test_get_200_pk(self):
        self.login()
        response = self.client.get('/user/1/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content, {
            "id": 1,
            "name": 's1',
            "zeny": 10000,
            "chars": [
                {
                    "id": 150000,
                    "name": 'spam',
                    "zeny": 10000,
                }
            ],
        })

    def test_get_403(self):
        self.login()
        response = self.client.get('/user/2/')
        self.assertEqual(response.status_code, 403)

    def test_get_401_me(self):
        response = self.client.get('/user/me/')
        self.assertEqual(response.status_code, 401)

    def test_get_401_pk(self):
        response = self.client.get('/user/1/')
        self.assertEqual(response.status_code, 401)


class CharTest(MyTestCase):
    fixtures = ['user.json']

    def test_get_200_no_login(self):
        response = self.client.get('/char/150000/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content, {
            "id": 150000,
            "name": 'spam',
        })

    def test_get_200_login(self):
        self.login()
        response = self.client.get('/char/150000/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content, {
            "id": 150000,
            "name": 'spam',
            "zeny": 10000,
        })

    def test_get_200_login_other(self):
        response = self.client.get('/char/150001/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content, {
            "id": 150001,
            "name": 'spam2',
        })

    def test_get_404(self):
        response = self.client.get('/char/150009/')
        self.assertEqual(response.status_code, 404)


@ddt
class VendingNoLock(MyTestCase):
    fixtures = ['user.json', 'items.json']

    @data('storage/', 'vending/', )
    def test_post_empty(self, value):
        self.login()
        response = self.client.post('/user/me/' + value, None, "json")
        self.assertEqual(response.status_code, 400)

    @data('storage/', 'vending/', )
    def test_post_empty_list(self, value):
        items = []
        self.login()
        response = self.client.post('/user/me/' + value, items, "json")
        self.assertEqual(response.status_code, 400, response.data)

    @data('storage/', 'vending/', )
    def test_post_repeat_item(self, value):
        items = [
            {
                "nameid": 501,
                "amount": 1,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, {
                "nameid": 501,
                "amount": 1,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/' + value, items, "json")
        self.assertEqual(response.status_code, 400)

    @data('storage/', 'vending/', )
    def test_post_dont_have(self, value):
        items = [
            {
                "nameid": 506,
                "amount": 1,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/' + value, items, "json")
        self.assertEqual(response.status_code, 409)

    @data('storage/', 'vending/', )
    def test_post_dont_have_so_much(self, value):
        items = [
            {
                "nameid": 501,
                "amount": settings.MAX_AMOUNT,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/' + value, items, "json")
        self.assertEqual(response.status_code, 409)

    @data('storage/', 'vending/', )
    def test_post_zero_amount(self, value):
        items = [
            {
                "nameid": 501,
                "amount": 0,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/' + value, items, "json")
        self.assertEqual(response.status_code, 400)

    @data('storage/', 'vending/', )
    def test_post_negative_amount(self, value):
        items = [
            {
                "nameid": 501,
                "amount": -1,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/' + value, items, "json")
        self.assertEqual(response.status_code, 400)

    @data('vending/', )
    def test_post_no_identified_item(self, value):
        """
        s1 have two 1101: one identified and other not.
        """
        items = [
            {
                "nameid": 1101,
                "amount": 2,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/' + value, items, "json")
        self.assertEqual(response.status_code, 409)

    @data('vending/', )
    def test_post_bounded_item(self, value):
        items = [
            {
                "nameid": 2301,
                "amount": 1,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/' + value, items, "json")
        self.assertEqual(response.status_code, 409)

    @data('vending/', )
    def test_post_expire_item(self, value):
        items = [
            {
                "nameid": 1373,
                "amount": 1,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/' + value, items, "json")
        self.assertEqual(response.status_code, 409)

    @data('vending/', )
    def test_post_broken_item(self, value):
        items = [
            {
                "nameid": 2302,
                "amount": 1,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/' + value, items, "json")
        self.assertEqual(response.status_code, 409)

    @data('vending/', )
    def test_post_no_merchantable_item(self, value):
        items = [
            {
                "nameid": 7556,
                "amount": 1,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/' + value, items, "json")
        self.assertEqual(response.status_code, 409)

    @data('storage/', 'vending/', )
    def test_post_online(self, value):
        items = [
            {
                "nameid": 501,
                "amount": 1,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login("s2")
        response = self.client.post('/user/me/' + value, items, "json")
        self.assertEqual(response.status_code, 409)


class ViewsMethods(unittest.TestCase):
    def test_check_no_repeated_item_ok(self):
        items = [
            {'nameid': 501, 'amount': 3, 'refine': 0, 'card0': 0, 'card1': 0, 'card2': 0, 'card3': 0},
            {'nameid': 502, 'amount': 3, 'refine': 0, 'card0': 0, 'card1': 0, 'card2': 0, 'card3': 0},
        ]
        views.check_no_repeated_items(items)

    def test_check_no_repeated_item_ok_empty(self):
        items = []
        views.check_no_repeated_items(items)

    def test_check_no_repeated_item_ok_one_item(self):
        items = [
            {'nameid': 502, 'amount': 3, 'refine': 0, 'card0': 0, 'card1': 0, 'card2': 0, 'card3': 0},
        ]
        views.check_no_repeated_items(items)

    def test_check_no_repeated_item_exception(self):
        items = [
            {'nameid': 501, 'amount': 3, 'refine': 0, 'card0': 0, 'card1': 0, 'card2': 0, 'card3': 0},
            {'nameid': 501, 'amount': 4, 'refine': 0, 'card0': 0, 'card1': 0, 'card2': 0, 'card3': 0},
        ]
        with self.assertRaises(serializers.ValidationError):
            views.check_no_repeated_items(items)
