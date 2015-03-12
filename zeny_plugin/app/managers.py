from django.db import models

from .exceptions import ConflictError


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


def check_no_char_online(cursor, user):
    cursor.execute("SELECT name FROM `char` WHERE account_id = %s AND online != 0", [user.pk])
    if cursor.rowcount > 0:
        name = cursor.fetchone()[0]
        raise ConflictError("You're connected to the server with the PJ %s, please disconnect and retry." % name)


class BaseStorageManager(models.Manager):
    def _add_item_to_destination_insert(self, cursor, user, item):
        cursor.execute("""INSERT INTO """ + self.destination_table + """
                (account_id, nameid, amount, equip, identify, refine, attribute, card0, card1, card2, card3, expire_time, bound, unique_id)
                (SELECT account_id, nameid, %s, equip, identify, refine, attribute, card0, card1, card2, card3, expire_time, bound, unique_id
                FROM """ + self.table + """ AS source
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

    def _add_item_to_destination_update(self, cursor, user, item):
        cursor.execute("""UPDATE """ + self.destination_table + """ AS destination
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
        raise NotImplementedError("Please, implement this method")

    def _remove_item_to_source_delete(self, cursor, user, item):
        cursor.execute("""DELETE FROM """ + self.table + """
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

    def _remove_item_to_source_update(self, cursor, user, item):
        cursor.execute("""UPDATE """ + self.table + """ AS source
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
        cursor.execute("""DELETE FROM """ + self.table + """
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

    def _check_user_have_items(self, cursor, user, items):
        where, having, param_where, param_having = self._where_items_amount(items)

        sql = """
            SELECT
                source.nameid,
                source.refine,
                source.card0,
                source.card1,
                source.card2,
                source.card3,
                SUM(source.amount) AS total_amount
            FROM """ + self.table + """ AS source
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
            raise ConflictError("You doesn't have this items.")  # TODO Verbose error.

    def _get_user_items(self, cursor, user, items):
        where, having, param_where, param_having = self._where_items_amount(items)

        sql = """
            SELECT
                source.nameid,
                source.refine,
                source.card0,
                source.card1,
                source.card2,
                source.card3,
                SUM(source.amount) AS total_amount,
                item.type,
                destination.amount
            FROM """ + self.table + """ AS source
            INNER JOIN item_db_re AS item ON
                source.nameid = item.id
            LEFT JOIN """ + self.destination_table + """ AS destination ON
                item.type NOT IN (4, 5, 7, 8, 12) AND
                %s = destination.account_id AND
                source.nameid = destination.nameid AND
                source.refine = destination.refine AND
                source.card0 = destination.card0 AND
                source.card1 = destination.card1 AND
                source.card2 = destination.card2 AND
                source.card3 = destination.card3
            WHERE
                source.bound = 0 AND
                source.expire_time = 0 AND
                source.identify != 0 AND
                source.account_id = %s AND
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
                source.nameid = %s AND
                source.refine = %s AND
                source.card0 = %s AND
                source.card1 = %s AND
                source.card2 = %s AND
                source.card3 = %s)
            """)
            having.append("""(
                source.nameid = %s AND
                source.refine = %s AND
                source.card0 = %s AND
                source.card1 = %s AND
                source.card2 = %s AND
                source.card3 = %s AND
                SUM(source.amount) >= %s)
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
                    `""" + self.table + """` AS source LOW_PRIORITY WRITE,
                    `""" + self.table + """` LOW_PRIORITY WRITE,
                    `item_db_re` AS item LOW_PRIORITY WRITE,
                    `""" + self.destination_table + """` AS destination LOW_PRIORITY WRITE,
                    `""" + self.destination_table + """` LOW_PRIORITY WRITE""")
            check_no_char_online(cursor, user)
            self._get_user_items(cursor, user, items)
            if cursor.rowcount != len(items):
                raise ConflictError("You doesn't have this items.")  # TODO Verbose error.
            for row in cursor.fetchall():
                item = find_item(row, items)
                if int(row[7]) in [4, 5, 7, 8, 12]:
                    self._add_no_stackable_item_vending_storage(cursor, user, item)
                    self._remove_no_stackable_item_storage(cursor, user, item)
                else:
                    # Add to source
                    if row[8] is None:
                        self._add_item_to_destination_insert(cursor, user, item)
                    else:
                        self._add_item_to_destination_update(cursor, user, item)
                    # Remove to destination
                    if int(row[6]) == item['amount']:
                        self._remove_item_to_source_delete(cursor, user, item)
                    else:
                        self._remove_item_to_source_update(cursor, user, item)
        finally:
            cursor.execute("UNLOCK TABLES")

    @property
    def table(self):
        raise NotImplementedError("Please, implement this method")

    @property
    def destination_table(self):
        raise NotImplementedError("Please, implement this method")


class StorageManager(BaseStorageManager):
    def get_queryset(self):
        return super(StorageManager, self).get_queryset().filter(bound='0', expire_time='0', attribute='0')\
            .exclude(identify='0')

    def _add_no_stackable_item_vending_storage(self, cursor, user, item):
        cursor.execute("""SELECT zeny FROM """ + self.destination_table + """ AS destination
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

        cursor.execute("""INSERT INTO """ + self.destination_table + """
                (account_id, nameid, amount, equip, identify, refine, attribute, card0, card1, card2, card3, expire_time, bound, unique_id, zeny)
                (SELECT account_id, nameid, amount, equip, identify, refine, attribute, card0, card1, card2, card3, expire_time, bound, unique_id, %s
                FROM """ + self.table + """ AS source
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

    @property
    def table(self):
        return 'storage'

    @property
    def destination_table(self):
        return 'storage_vending'


class VendingManager(BaseStorageManager):
    @property
    def table(self):
        return 'storage_vending'

    @property
    def destination_table(self):
        return 'storage'

    def _add_no_stackable_item_vending_storage(self, cursor, user, item):
        cursor.execute("""INSERT INTO """ + self.destination_table + """
                (account_id, nameid, amount, equip, identify, refine, attribute, card0, card1, card2, card3, expire_time, bound, unique_id)
                (SELECT account_id, nameid, amount, equip, identify, refine, attribute, card0, card1, card2, card3, expire_time, bound, unique_id
                FROM """ + self.table + """ AS source
                WHERE
                bound = 0 AND expire_time = 0 AND identify != 0 AND attribute = 0 AND
                account_id = %s AND
                nameid = %s AND refine = %s AND card0 = %s AND card1 = %s AND card2 = %s AND card3 = %s
                LIMIT %s
                )
        """, [
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
