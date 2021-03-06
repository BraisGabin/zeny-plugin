from rest_framework.test import APITestCase

from ..models import User


class AuthenticationMixin(object):
    def login(self, account="s1"):
        self.client.force_authenticate(User.objects.get(name=account))

    def logout(self):
        self.client.force_authenticate(None)


class MyTestCase(AuthenticationMixin, APITestCase):
    def tearDown(self):
        for db_name in self._databases_names(include_mirrors=False):
            from django.db import connections

            connections[db_name].cursor().execute("""
            SET FOREIGN_KEY_CHECKS = 0;
            TRUNCATE `login`;
            TRUNCATE `char`;
            TRUNCATE `storage`;
            TRUNCATE `storage_vending`;
            TRUNCATE `zeny`;
            TRUNCATE `vending_log`;
            SET FOREIGN_KEY_CHECKS = 1;
            """)
        super(MyTestCase, self).tearDown()
