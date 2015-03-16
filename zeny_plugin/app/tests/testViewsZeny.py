from django.conf import settings
from django.test.utils import override_settings
from zeny_plugin.app.models import User, Char

from zeny_plugin.app.tests.testcases import MyTestCase


class MoveZeny(MyTestCase):
    fixtures = ['user.json']

    def test_empty(self):
        self.login()
        response = self.client.put('/char/150000/', None, "json")
        self.assertEqual(response.status_code, 400)

    def test_no_mine(self):
        self.login()
        response = self.client.put('/char/150001/', None, "json")
        self.assertEqual(response.status_code, 403)

    def test_no_authentication(self):
        response = self.client.put('/char/150000/', None, "json")
        self.assertEqual(response.status_code, 401)

    def test_no_char(self):
        self.login()
        response = self.client.put('/char/150009/', None, "json")
        self.assertEqual(response.status_code, 404)

    def test_no_zeny_char(self):
        zeny = {
            "zeny": -100000
        }
        self.login()
        response = self.client.put('/char/150000/', zeny, "json")
        self.assertEqual(response.status_code, 409)

    def test_no_zeny_user(self):
        zeny = {
            "zeny": 100000
        }
        self.login()
        response = self.client.put('/char/150000/', zeny, "json")
        self.assertEqual(response.status_code, 409)

    def test_no_zeny_user_first(self):
        zeny = {
            "zeny": 100000
        }
        self.login("s2")
        response = self.client.put('/char/150002/', zeny, "json")
        self.assertEqual(response.status_code, 409)

    def test_no_zero(self):
        zeny = {
            "zeny": 0
        }
        self.login()
        response = self.client.put('/char/150000/', zeny, "json")
        self.assertEqual(response.status_code, 400)

    def test_limit_zeny_positive(self):
        zeny = {
            "zeny": settings.MAX_ZENY + 1
        }
        self.login()
        response = self.client.put('/char/150000/', zeny, "json")
        self.assertEqual(response.status_code, 400)

    def test_limit_zeny_negative(self):
        zeny = {
            "zeny": -(settings.MAX_ZENY + 1)
        }
        self.login()
        response = self.client.put('/char/150000/', zeny, "json")
        self.assertEqual(response.status_code, 400)

    @override_settings(MAX_ZENY=11000)
    def test_limit_zeny_char(self):
        zeny = {
            "zeny": 2000
        }
        self.login()
        response = self.client.put('/char/150000/', zeny, "json")
        self.assertEqual(response.status_code, 409)

    @override_settings(MAX_ZENY=11000)
    def test_limit_zeny_user(self):
        zeny = {
            "zeny": -2000
        }
        self.login()
        response = self.client.put('/char/150000/', zeny, "json")
        self.assertEqual(response.status_code, 409)

    def test_char_online(self):
        zeny = {
            "zeny": -2000
        }
        self.login("s2")
        response = self.client.put('/char/150001/', zeny, "json")
        self.assertEqual(response.status_code, 409)

    def test_zeny_char(self):
        zeny = {
            "zeny": 2000
        }
        self.login()
        response = self.client.put('/char/150000/', zeny, "json")
        self.assertEqual(response.status_code, 204)
        user = User.objects.get(name="s1")
        self.assertEqual(user.zeny, 8000)

        char = Char.objects.get(pk=150000)
        self.assertEqual(char.zeny, 12000)

    def test_zeny_user(self):
        zeny = {
            "zeny": -2000
        }
        self.login()
        response = self.client.put('/char/150000/', zeny, "json")
        self.assertEqual(response.status_code, 204)
        user = User.objects.get(name="s1")
        self.assertEqual(user.zeny, 12000)

        char = Char.objects.get(pk=150000)
        self.assertEqual(char.zeny, 8000)

    def test_zeny_user_first(self):
        zeny = {
            "zeny": -2000
        }
        self.login("s2")
        response = self.client.put('/char/150002/', zeny, "json")
        self.assertEqual(response.status_code, 204)
        user = User.objects.get(name="s2")
        self.assertEqual(user.zeny, 2000)

        char = Char.objects.get(pk=150002)
        self.assertEqual(char.zeny, 8000)
