from rest_framework.test import APITransactionTestCase


class MyTransactionTestCase(APITransactionTestCase):
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
