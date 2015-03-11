from rest_framework.test import APITransactionTestCase, APITestCase

from ..models import User


class AuthenticationMixin(object):
    def login(self, userid="s1"):
        self.client.force_authenticate(User.objects.get(userid=userid))

    def logout(self):
        self.client.force_authenticate(None)


class MyTransactionTestCase(AuthenticationMixin, APITransactionTestCase):
    def _fixture_teardown(self):
        super(MyTransactionTestCase, self)._fixture_teardown()
        for db_name in self._databases_names(include_mirrors=False):
            from django.db import connections

            connections[db_name].cursor().execute("""
            SET FOREIGN_KEY_CHECKS = 0;
            TRUNCATE `login`;
            TRUNCATE `char`;
            TRUNCATE `storage`;
            TRUNCATE `storage_vending`;
            SET FOREIGN_KEY_CHECKS = 1;
            """)


class MyTestCase(AuthenticationMixin, APITestCase):
    pass
