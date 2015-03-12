from django.core.exceptions import ObjectDoesNotExist

from .testcases import MyTestCase
from ..models import User


class Vending(MyTestCase):
    fixtures = ['user.json', 'items.json']

    def test_move_first_no_all(self):
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
        self.login()
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
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        with self.assertRaises(ObjectDoesNotExist):
            user.storage.get(nameid=501)

        vending = user.vending.get(nameid=501)
        self.assertEqual(vending.amount, 5)
        self.assertEqual(vending.zeny, 0)

    def test_move_no_first_no_all(self):
        items = [
            {
                "nameid": 502,
                "amount": 1,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        storage = user.storage.get(nameid=502)
        self.assertEqual(storage.amount, 4)

        vending = user.vending.get(nameid=502)
        self.assertEqual(vending.amount, 6)
        self.assertEqual(vending.zeny, 0)

    def test_move_no_first_all(self):
        items = [
            {
                "nameid": 502,
                "amount": 5,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        with self.assertRaises(ObjectDoesNotExist):
            user.storage.get(nameid=502)

        vending = user.vending.get(nameid=502)
        self.assertEqual(vending.amount, 10)
        self.assertEqual(vending.zeny, 0)

    def test_move_no_first_no_all_zeny(self):
        items = [
            {
                "nameid": 503,
                "amount": 1,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        storage = user.storage.get(nameid=503)
        self.assertEqual(storage.amount, 4)

        vending = user.vending.get(nameid=503)
        self.assertEqual(vending.amount, 6)
        self.assertEqual(vending.zeny, 1000)

    def test_move_no_first_all_zeny(self):
        items = [
            {
                "nameid": 503,
                "amount": 5,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        with self.assertRaises(ObjectDoesNotExist):
            user.storage.get(nameid=503)

        vending = user.vending.get(nameid=503)
        self.assertEqual(vending.amount, 10)
        self.assertEqual(vending.zeny, 1000)


class VendingNoStackable(MyTestCase):
    fixtures = ['user.json', 'items.json']

    def test_move_first_no_all(self):
        items = [
            {
                "nameid": 1201,
                "amount": 1,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        self.assertEqual(user.storage.filter(nameid=1201).count(), 2)
        for storage in user.storage.filter(nameid=1201):
            self.assertEqual(storage.amount, 1)

        self.assertEqual(user.vending.filter(nameid=1201).count(), 1)
        for vending in user.vending.filter(nameid=1201):
            self.assertEqual(vending.amount, 1)
            self.assertEqual(vending.zeny, 0)

    def test_move_first_all(self):
        items = [
            {
                "nameid": 1201,
                "amount": 3,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        self.assertEqual(user.storage.filter(nameid=1201).count(), 0)

        self.assertEqual(user.vending.filter(nameid=1201).count(), 3)
        for vending in user.vending.filter(nameid=1201):
            self.assertEqual(vending.amount, 1)
            self.assertEqual(vending.zeny, 0)

    def test_move_no_first_no_all(self):
        items = [
            {
                "nameid": 1202,
                "amount": 1,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        self.assertEqual(user.storage.filter(nameid=1202).count(), 2)
        for storage in user.storage.filter(nameid=1202):
            self.assertEqual(storage.amount, 1)

        self.assertEqual(user.vending.filter(nameid=1202).count(), 2)
        for vending in user.vending.filter(nameid=1202):
            self.assertEqual(vending.amount, 1)
            self.assertEqual(vending.zeny, 0)

    def test_move_no_first_all(self):
        items = [
            {
                "nameid": 1202,
                "amount": 3,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        self.assertEqual(user.storage.filter(nameid=1202).count(), 0)

        self.assertEqual(user.vending.filter(nameid=1202).count(), 4)
        for vending in user.vending.filter(nameid=1202):
            self.assertEqual(vending.amount, 1)
            self.assertEqual(vending.zeny, 0)

    def test_move_no_first_no_all_zeny(self):
        items = [
            {
                "nameid": 1203,
                "amount": 1,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        self.assertEqual(user.storage.filter(nameid=1203).count(), 2)
        for storage in user.storage.filter(nameid=1203):
            self.assertEqual(storage.amount, 1)

        self.assertEqual(user.vending.filter(nameid=1203).count(), 3)
        for vending in user.vending.filter(nameid=1203):
            self.assertEqual(vending.amount, 1)
            self.assertEqual(vending.zeny, 1000)

    def test_move_no_first_all_zeny(self):
        items = [
            {
                "nameid": 1203,
                "amount": 3,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
            }, ]
        self.login()
        response = self.client.post('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        self.assertEqual(user.storage.filter(nameid=1203).count(), 0)

        self.assertEqual(user.vending.filter(nameid=1203).count(), 5)
        for vending in user.vending.filter(nameid=1203):
            self.assertEqual(vending.amount, 1)
            self.assertEqual(vending.zeny, 1000)


class VendingZeny(MyTestCase):
    fixtures = ['user.json', 'items.json']

    def test_post_empty(self):
        self.login()
        response = self.client.put('/user/me/vending/', None, "json")
        self.assertEqual(response.status_code, 400, response.data)

    def test_post_empty_list(self):
        items = []
        self.login()
        response = self.client.put('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 400, response.data)

    def test_post_repeat_item(self):
        items = [
            {
                "nameid": 502,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
                "zeny": 1000,
            }, {
                "nameid": 502,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
                "zeny": 500,
            }, ]
        self.login()
        response = self.client.put('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 400, response.data)

    def test_post_negative_zeny(self):
        items = [
            {
                "nameid": 502,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
                "zeny": -1000,
            }, ]
        self.login()
        response = self.client.put('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 400, response.data)

    def test_post_ok_online(self):
        items = [
            {
                "nameid": 502,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
                "zeny": 1000,
            }, ]
        self.login("s2")
        response = self.client.put('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s2")

        item = user.vending.get(nameid=502)
        self.assertEqual(item.zeny, 1000)

    def test_post_ok(self):
        items = [
            {
                "nameid": 502,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
                "zeny": 1000,
            },
            {
                "nameid": 503,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
                "zeny": 1500,
            },
            {
                "nameid": 1203,
                "refine": 0,
                "card0": 0,
                "card1": 0,
                "card2": 0,
                "card3": 0,
                "zeny": 2000,
            }, ]
        self.login()
        response = self.client.put('/user/me/vending/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        item = user.vending.get(nameid=502)
        self.assertEqual(item.zeny, 1000)
        item = user.vending.get(nameid=503)
        self.assertEqual(item.zeny, 1500)
        items = user.vending.filter(nameid=1203)
        for item in items:
            self.assertEqual(item.zeny, 2000)

