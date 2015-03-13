from zeny_plugin.app.models import User
from zeny_plugin.app.tests.testcases import MyTestCase


class UserSecurityAccess(MyTestCase):
    fixtures = ['user.json']

    def test_user_zeny(self):
        user = User.objects.get(name="s1")
        self.assertEqual(user.zeny, 10000)

    def test_user_no_zeny(self):
        user = User.objects.get(name="s2")
        self.assertEqual(user.zeny, 0)
