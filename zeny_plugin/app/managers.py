from django.db import models
from rest_framework.exceptions import ValidationError

from zeny_plugin.app.exceptions import ConflictError


def find_item(row, items):
    for item in items:
        if int(row[0]) == item['nameid'] and int(row[1]) == item['refine'] and int(row[2]) == item['card0'] and \
                int(row[3]) == item['card1'] and int(row[4]) == item['card2'] and int(row[5]) == item['card3']:
            return item
    raise TypeError("Unknown item")


def get_params_item(item):
    return [
        item['nameid'],
        item['refine'],
        item['card0'],
        item['card1'],
        item['card2'],
        item['card3']
    ]


class BaseStorageManager(models.Manager):
    def _add_item_vending_storage(self, cursor, user, item):
        cursor.execute("""INSERT INTO storage_vending
                (account_id, nameid, amount, equip, identify, refine, attribute, card0, card1, card2, card3, expire_time, bound, unique_id, zeny)
                (SELECT account_id, nameid, %s, equip, identify, refine, attribute, card0, card1, card2, card3, expire_time, bound, unique_id, 0
                FROM storage
                WHERE
                bound = 0 AND expire_time = 0 AND identify != 0 AND attribute = 0 AND
                account_id = %s AND
                nameid = %s AND refine = %s AND card0 = %s AND card1 = %s AND card2 = %s AND card3 = %s
                )
        """, [
            item['amount'],
            user.pk,
            item['nameid'],
            item['refine'],
            item['card0'],
            item['card1'],
            item['card2'],
            item['card3']
        ])
        if cursor.rowcount != 1:
            raise TypeError("Critical error, possible dupe")

    def _update_item_vending_storage(self, cursor, user, item):
        cursor.execute("""UPDATE storage_vending
                SET amount = amount + %s
                WHERE
                bound = 0 AND expire_time = 0 AND identify != 0 AND attribute = 0 AND
                account_id = %s AND
                nameid = %s AND refine = %s AND card0 = %s AND card1 = %s AND card2 = %s AND card3 = %s
        """, [
            item['amount'],
            user.pk,
            item['nameid'],
            item['refine'],
            item['card0'],
            item['card1'],
            item['card2'],
            item['card3']
        ])
        if cursor.rowcount != 1:
            raise TypeError("Critical error, possible dupe")

    def _add_no_stackable_item_vending_storage(self, cursor, user, item):
        cursor.execute("""SELECT zeny FROM storage_vending
                WHERE
                bound = 0 AND expire_time = 0 AND identify != 0 AND attribute = 0 AND
                account_id = %s AND
                nameid = %s AND refine = %s AND card0 = %s AND card1 = %s AND card2 = %s AND card3 = %s
                LIMIT 1
        """, [
            user.pk,
            item['nameid'],
            item['refine'],
            item['card0'],
            item['card1'],
            item['card2'],
            item['card3']
        ])

        zeny = cursor.fetchone()[0] if cursor.rowcount > 0 else 0

        cursor.execute("""INSERT INTO storage_vending
                (account_id, nameid, amount, equip, identify, refine, attribute, card0, card1, card2, card3, expire_time, bound, unique_id, zeny)
                (SELECT account_id, nameid, amount, equip, identify, refine, attribute, card0, card1, card2, card3, expire_time, bound, unique_id, %s
                FROM storage
                WHERE
                bound = 0 AND expire_time = 0 AND identify != 0 AND attribute = 0 AND
                account_id = %s AND
                nameid = %s AND refine = %s AND card0 = %s AND card1 = %s AND card2 = %s AND card3 = %s
                LIMIT %s
                )
        """, [
            zeny,
            user.pk,
            item['nameid'],
            item['refine'],
            item['card0'],
            item['card1'],
            item['card2'],
            item['card3'],
            item['amount'],
        ])
        if cursor.rowcount != item['amount']:
            raise TypeError("Critical error, possible dupe")

    def _remove_item_storage(self, cursor, user, item):
        cursor.execute("""DELETE FROM storage
                WHERE
                bound = 0 AND expire_time = 0 AND identify != 0 AND attribute = 0 AND
                account_id = %s AND
                nameid = %s AND refine = %s AND card0 = %s AND card1 = %s AND card2 = %s AND card3 = %s
        """, [
            user.pk,
            item['nameid'],
            item['refine'],
            item['card0'],
            item['card1'],
            item['card2'],
            item['card3']
        ])
        if cursor.rowcount != 1:
            raise TypeError("Critical error, possible dupe")

    def _update_item_storage(self, cursor, user, item):
        cursor.execute("""UPDATE storage
                SET amount = amount - %s
                WHERE
                bound = 0 AND expire_time = 0 AND identify != 0 AND attribute = 0 AND
                account_id = %s AND
                nameid = %s AND refine = %s AND card0 = %s AND card1 = %s AND card2 = %s AND card3 = %s
        """, [
            item['amount'],
            user.pk,
            item['nameid'],
            item['refine'],
            item['card0'],
            item['card1'],
            item['card2'],
            item['card3']
        ])
        if cursor.rowcount != 1:
            raise TypeError("Critical error, possible dupe")

    def _remove_no_stackable_item_storage(self, cursor, user, item):
        cursor.execute("""DELETE FROM storage
                WHERE
                bound = 0 AND expire_time = 0 AND identify != 0 AND attribute = 0 AND
                account_id = %s AND
                nameid = %s AND refine = %s AND card0 = %s AND card1 = %s AND card2 = %s AND card3 = %s
                LIMIT %s
        """, [
            user.pk,
            item['nameid'],
            item['refine'],
            item['card0'],
            item['card1'],
            item['card2'],
            item['card3'],
            item['amount']
        ])
        if cursor.rowcount != item['amount']:
            raise TypeError("Critical error, possible dupe")

    def _check_no_char_online(self, cursor, user):
        cursor.execute("SELECT name FROM `char` WHERE account_id = %s AND online != 0", [user.pk])
        if cursor.rowcount > 0:
            name = cursor.fetchone()[0]
            raise ConflictError("You're connected to the server with the PJ %s, please disconnect and retry." % name)

    def _check_user_have_items(self, cursor, user, items):
        where, having, param_where, param_having = self._where_items_amount(items)

        sql = """
            SELECT
                storage.nameid,
                storage.refine,
                storage.card0,
                storage.card1,
                storage.card2,
                storage.card3,
                SUM(storage.amount) as total_amount
            FROM storage
            WHERE
            bound = 0 AND
            expire_time = 0 AND
            identify != 0 AND
            account_id = %s AND
            (""" + where + """)
            GROUP BY nameid, refine, card0, card1, card2, card3
            HAVING (""" + having + ")"

        parameters = [user.pk]
        parameters.extend(param_where)
        parameters.extend(param_having)

        cursor.execute(sql, parameters)
        if cursor.rowcount != len(items):
            raise ValidationError("You doesn't have this items.")  # TODO Verbose error. 409?

    def _get_user_items(self, cursor, user, items):
        where, having, param_where, param_having = self._where_items_amount(items)

        sql = """
            SELECT
                storage.nameid,
                storage.refine,
                storage.card0,
                storage.card1,
                storage.card2,
                storage.card3,
                SUM(storage.amount) as total_amount,
                item.type,
                storage_vending.amount
            FROM storage
            INNER JOIN item_db_re AS item ON
                storage.nameid = item.id
            LEFT JOIN storage_vending ON
                item.type NOT IN (4, 5, 7, 8, 12) AND
                %s = storage_vending.account_id AND
                storage.nameid = storage_vending.nameid AND
                storage.refine = storage_vending.refine AND
                storage.card0 = storage_vending.card0 AND
                storage.card1 = storage_vending.card1 AND
                storage.card2 = storage_vending.card2 AND
                storage.card3 = storage_vending.card3
            WHERE
                storage.bound = 0 AND
                storage.expire_time = 0 AND
                storage.identify != 0 AND
                storage.account_id = %s AND
                (""" + where + """)
            GROUP BY nameid, refine, card0, card1, card2, card3
            HAVING (""" + having + ")"

        parameters = [user.pk, user.pk]
        parameters.extend(param_where)
        parameters.extend(param_having)

        cursor.execute(sql, parameters)

    @staticmethod
    def _where_items_amount(items):
        where = []
        having = []
        param_where = []
        param_having = []
        for item in items:
            where.append("""(
                storage.nameid = %s AND
                storage.refine = %s AND
                storage.card0 = %s AND
                storage.card1 = %s AND
                storage.card2 = %s AND
                storage.card3 = %s)
            """)
            having.append("""(
                storage.nameid = %s AND
                storage.refine = %s AND
                storage.card0 = %s AND
                storage.card1 = %s AND
                storage.card2 = %s AND
                storage.card3 = %s AND
                SUM(storage.amount) >= %s)
            """)
            params = get_params_item(item)
            param_where.extend(params)
            param_having.extend(params)
            param_having.append(item['amount'])

        where = ' OR '.join(where)
        having = ' OR '.join(having)
        return where, having, param_where, param_having

    def check_items(self, user, items):
        from django.db import connection

        cursor = connection.cursor()
        self._check_user_have_items(cursor, user, items)

    def move_items(self, user, items):
        from django.db import connection

        cursor = connection.cursor()
        try:
            cursor.execute("""
                    LOCK TABLES
                    `char` LOW_PRIORITY WRITE,
                    `storage` LOW_PRIORITY WRITE,
                    `item_db_re` AS item LOW_PRIORITY WRITE,
                    `storage_vending` LOW_PRIORITY WRITE""")
            self._check_no_char_online(cursor, user)
            self._get_user_items(cursor, user, items)
            if cursor.rowcount != len(items):
                raise ValidationError("You doesn't have this items.")  # TODO Verbose error. 409?
            for row in cursor.fetchall():
                item = find_item(row, items)
                if int(row[7]) in [4, 5, 7, 8, 12]:
                    self._add_no_stackable_item_vending_storage(cursor, user, item)
                    self._remove_no_stackable_item_storage(cursor, user, item)
                else:
                    # Add to storage_vending
                    if row[8] is None:
                        self._add_item_vending_storage(cursor, user, item)
                    else:
                        self._update_item_vending_storage(cursor, user, item)
                    # Remove to storage
                    if int(row[6]) == item['amount']:
                        self._remove_item_storage(cursor, user, item)
                    else:
                        self._update_item_storage(cursor, user, item)
        finally:
            cursor.execute("UNLOCK TABLES")


class StorageManager(BaseStorageManager):
    def get_queryset(self):
        return super(StorageManager, self).get_queryset().filter(bound='0', expire_time='0', ).exclude(identify='0')


class VendingManager(BaseStorageManager):
    pass
