from django.core.exceptions import ObjectDoesNotExist

from .testcases import MyTestCase
from ..models import User


class Storage(MyTestCase):
    fixtures = ['user.json', 'items2.json']

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
        response = self.client.post('/user/me/storage/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        vending = user.vending.get(nameid=501)
        self.assertEqual(vending.amount, 4)

        storage = user.storage.get(nameid=501)
        self.assertEqual(storage.amount, 1)

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
        response = self.client.post('/user/me/storage/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        with self.assertRaises(ObjectDoesNotExist):
            user.vending.get(nameid=501)

        storage = user.storage.get(nameid=501)
        self.assertEqual(storage.amount, 5)

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
        response = self.client.post('/user/me/storage/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        vending = user.vending.get(nameid=502)
        self.assertEqual(vending.amount, 4)

        storage = user.storage.get(nameid=502)
        self.assertEqual(storage.amount, 6)

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
        response = self.client.post('/user/me/storage/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        with self.assertRaises(ObjectDoesNotExist):
            user.vending.get(nameid=502)

        storage = user.storage.get(nameid=502)
        self.assertEqual(storage.amount, 10)


class StorageNoStackable(MyTestCase):
    fixtures = ['user.json', 'items2.json']

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
        response = self.client.post('/user/me/storage/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        self.assertEqual(user.vending.filter(nameid=1201).count(), 2)
        for vending in user.vending.filter(nameid=1201):
            self.assertEqual(vending.amount, 1)

        self.assertEqual(user.storage.filter(nameid=1201).count(), 1)
        for storage in user.storage.filter(nameid=1201):
            self.assertEqual(storage.amount, 1)

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
        response = self.client.post('/user/me/storage/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        self.assertEqual(user.vending.filter(nameid=1201).count(), 0)

        self.assertEqual(user.storage.filter(nameid=1201).count(), 3)
        for storage in user.storage.filter(nameid=1201):
            self.assertEqual(storage.amount, 1)

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
        response = self.client.post('/user/me/storage/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        self.assertEqual(user.vending.filter(nameid=1202).count(), 2)
        for vending in user.vending.filter(nameid=1202):
            self.assertEqual(vending.amount, 1)

        self.assertEqual(user.storage.filter(nameid=1202).count(), 2)
        for storage in user.storage.filter(nameid=1202):
            self.assertEqual(storage.amount, 1)

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
        response = self.client.post('/user/me/storage/', items, "json")
        self.assertEqual(response.status_code, 204, response.data)
        user = User.objects.get(userid="s1")

        self.assertEqual(user.vending.filter(nameid=1202).count(), 0)

        self.assertEqual(user.storage.filter(nameid=1202).count(), 4)
        for storage in user.storage.filter(nameid=1202):
            self.assertEqual(storage.amount, 1)
