from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.test.utils import override_settings

from .testcases import MyTestCase
from ..models import User


class BuyTest(MyTestCase):
    fixtures = ['user2.json', 'items3.json']

    def test_empty(self):
        self.login()
        response = self.client.put('/user/2/', None, "json")
        self.assertEqual(response.status_code, 400)

    def test_no_authentication(self):
        response = self.client.put('/user/2/', None, "json")
        self.assertEqual(response.status_code, 401)

    def test_404(self):
        self.login()
        response = self.client.put('/user/9/', None, "json")
        self.assertEqual(response.status_code, 404)

    def test_no_items(self):
        buy = {
            "nameid": 501,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 400)

    def test_no_zenies(self):
        buy = {
            "nameid": 501,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 1,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 400)

    def test_too_many_items(self):
        buy = {
            "nameid": 501,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": settings.MAX_AMOUNT + 1,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 400)

    def test_too_many_zenies(self):
        buy = {
            "nameid": 501,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 1,
            "zeny": settings.MAX_ZENY + 1,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 400)

    def test_too_many_zenies_x_amount(self):
        buy = {
            "nameid": 501,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 2,
            "zeny": settings.MAX_ZENY,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 400)

    def test_zero_items(self):
        buy = {
            "nameid": 501,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 0,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 400)

    def test_zero_zenies(self):
        buy = {
            "nameid": 501,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 1,
            "zeny": 0,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 400)

    def test_negative_items(self):
        buy = {
            "nameid": 501,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": -1,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 400)

    def test_negative_zenies(self):
        buy = {
            "nameid": 501,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 1,
            "zeny": -1,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 400)

    def test_wrong_zenies(self):
        buy = {
            "nameid": 501,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 1,
            "zeny": 999,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 400)

    def test_by_me(self):
        buy = {
            "nameid": 501,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 1,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/me/', buy, "json")
        self.assertEqual(response.status_code, 403)

    def test_buy_me_id(self):
        buy = {
            "nameid": 501,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 1,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/1/', buy, "json")
        self.assertEqual(response.status_code, 403)

    def test_dont_have_zeny(self):
        buy = {
            "nameid": 1202,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 1,
            "zeny": 100000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 409, response.data)

    def test_dont_have_zeny_first(self):
        buy = {
            "nameid": 502,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 4,
            "zeny": 2000,
        }
        self.login("s2")
        response = self.client.put('/user/1/', buy, "json")
        self.assertEqual(response.status_code, 409)

    def test_dont_have_item(self):
        buy = {
            "nameid": 506,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 6,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 400)

    def test_dont_exist_item(self):
        buy = {
            "nameid": 1,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 6,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 400)

    def test_too_much_amount(self):
        buy = {
            "nameid": 501,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 6,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 400)

    def test_too_much_amount_no_stackable(self):
        buy = {
            "nameid": 1101,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 6,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 400)

    @override_settings(MAX_STORAGE=4)
    def test_limit_storage(self):
        buy = {
            "nameid": 501,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 1,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 409)

    @override_settings(MAX_STORAGE=6)
    def test_limit_storage_no_stackable(self):
        buy = {
            "nameid": 1101,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 3,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 409)

    @override_settings(MAX_AMOUNT=7)
    def test_limit_amount(self):
        buy = {
            "nameid": 502,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 5,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 409)

    @override_settings(MAX_ZENY=12000)
    def test_limit_zeny(self):
        buy = {
            "nameid": 501,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 5,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/3/', buy, "json")
        self.assertEqual(response.status_code, 409)

    @override_settings(MAX_ZENY=12000)
    def test_limit_zeny(self):
        buy = {
            "nameid": 501,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 5,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/3/', buy, "json")
        self.assertEqual(response.status_code, 409)

    def test_buy_no_all_no_have(self):
        buy = {
            "nameid": 501,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 3,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 204)

        buyer = User.objects.get(name="s1")
        item = buyer.vending.get(nameid=501)
        self.assertEqual(item.amount, 3)
        self.assertEqual(item.zeny, 0)
        self.assertEqual(buyer.zeny, 7000)

        seller = User.objects.get(name="s2")
        item = seller.vending.get(nameid=501)
        self.assertEqual(item.amount, 2)
        self.assertEqual(seller.zeny, 3000)

    @override_settings(MAX_ZENY=13000)
    def test_buy_no_all_no_have_first(self):
        buy = {
            "nameid": 501,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 3,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/3/', buy, "json")
        self.assertEqual(response.status_code, 204)

        buyer = User.objects.get(name="s1")
        item = buyer.vending.get(nameid=501)
        self.assertEqual(item.amount, 3)
        self.assertEqual(item.zeny, 0)
        self.assertEqual(buyer.zeny, 7000)

        seller = User.objects.get(name="s3")
        item = seller.vending.get(nameid=501)
        self.assertEqual(item.amount, 2)
        self.assertEqual(seller.zeny, 13000)

    def test_buy_all_no_have(self):
        buy = {
            "nameid": 501,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 5,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 204)

        buyer = User.objects.get(name="s1")
        item = buyer.vending.get(nameid=501)
        self.assertEqual(item.amount, 5)
        self.assertEqual(item.zeny, 0)
        self.assertEqual(buyer.zeny, 5000)

        seller = User.objects.get(name="s2")

        with self.assertRaises(ObjectDoesNotExist):
            seller.vending.get(nameid=501)
        self.assertEqual(seller.zeny, 5000)

    def test_buy_no_all_have(self):
        buy = {
            "nameid": 502,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 3,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 204)

        buyer = User.objects.get(name="s1")
        item = buyer.vending.get(nameid=502)
        self.assertEqual(item.amount, 8)
        self.assertEqual(item.zeny, 2000)
        self.assertEqual(buyer.zeny, 7000)

        seller = User.objects.get(name="s2")
        item = seller.vending.get(nameid=502)
        self.assertEqual(item.amount, 2)
        self.assertEqual(seller.zeny, 3000)

    @override_settings(MAX_STORAGE=4)
    def test_buy_all_have(self):
        buy = {
            "nameid": 502,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 5,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 204)

        buyer = User.objects.get(name="s1")
        item = buyer.vending.get(nameid=502)
        self.assertEqual(item.amount, 10)
        self.assertEqual(item.zeny, 2000)
        self.assertEqual(buyer.zeny, 5000)

        seller = User.objects.get(name="s2")

        with self.assertRaises(ObjectDoesNotExist):
            seller.vending.get(nameid=502)
        self.assertEqual(seller.zeny, 5000)

    def test_buy_no_all_no_have_no_stack(self):
        buy = {
            "nameid": 1101,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 2,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 204)

        buyer = User.objects.get(name="s1")
        items = buyer.vending.filter(nameid=1101)
        self.assertEqual(items.count(), 2)
        for item in items:
            self.assertEqual(item.amount, 1)
            self.assertEqual(item.zeny, 0)
        self.assertEqual(buyer.zeny, 8000)

        seller = User.objects.get(name="s2")
        items = seller.vending.filter(nameid=1101)
        self.assertEqual(items.count(), 1)
        for item in items:
            self.assertEqual(item.amount, 1)
        self.assertEqual(seller.zeny, 2000)

    def test_buy_all_no_have_no_stack(self):
        buy = {
            "nameid": 1101,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 3,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 204)

        buyer = User.objects.get(name="s1")
        items = buyer.vending.filter(nameid=1101)
        self.assertEqual(items.count(), 3)
        for item in items:
            self.assertEqual(item.amount, 1)
            self.assertEqual(item.zeny, 0)
        self.assertEqual(buyer.zeny, 7000)

        seller = User.objects.get(name="s2")
        items = seller.vending.filter(nameid=1101)
        self.assertEqual(items.count(), 0)
        self.assertEqual(seller.zeny, 3000)

    def test_buy_no_all_have_no_stack(self):
        buy = {
            "nameid": 1201,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 2,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 204)

        buyer = User.objects.get(name="s1")
        items = buyer.vending.filter(nameid=1201)
        self.assertEqual(items.count(), 5)
        for item in items:
            self.assertEqual(item.amount, 1)
            self.assertEqual(item.zeny, 2000)
        self.assertEqual(buyer.zeny, 8000)

        seller = User.objects.get(name="s2")
        items = seller.vending.filter(nameid=1201)
        self.assertEqual(items.count(), 1)
        for item in items:
            self.assertEqual(item.amount, 1)
        self.assertEqual(seller.zeny, 2000)

    def test_buy_all_have_no_stack(self):
        buy = {
            "nameid": 1201,
            "refine": 0,
            "card0": 0,
            "card1": 0,
            "card2": 0,
            "card3": 0,
            "amount": 3,
            "zeny": 1000,
        }
        self.login()
        response = self.client.put('/user/2/', buy, "json")
        self.assertEqual(response.status_code, 204)

        buyer = User.objects.get(name="s1")
        items = buyer.vending.filter(nameid=1201)
        self.assertEqual(items.count(), 6)
        for item in items:
            self.assertEqual(item.amount, 1)
            self.assertEqual(item.zeny, 2000)
        self.assertEqual(buyer.zeny, 7000)

        seller = User.objects.get(name="s2")
        items = seller.vending.filter(nameid=1201)
        self.assertEqual(items.count(), 0)
        self.assertEqual(seller.zeny, 3000)