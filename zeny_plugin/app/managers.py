from django.conf import settings
from django.core.cache import cache
from django.db import models

from .exceptions import ConflictError
from zeny_plugin.app import processes


def relate_items_rows(rows, items):
    l = []
    items = list(items)
    for row in rows:
        the_item = None
        for index, item in enumerate(items):
            if int(row[0]) == item['nameid'] and int(row[1]) == item['refine'] and int(row[2]) == item['card0'] and \
                    int(row[3]) == item['card1'] and int(row[4]) == item['card2'] and int(row[5]) == item['card3']:
                items.pop(index)
                item['type'] = int(row[6])
                item['source_amount'] = row[7]
                item['destination_amount'] = int(row[8]) if row[8] is not None else 0
                the_item = item
                break

        if the_item is None:
            raise TypeError("Unknown item")
        l.append(the_item)
    return l


def get_no_merchantable_item_ids():
    no_merchantable = cache.get("no_merchantable")
    if no_merchantable is None:
        # TODO multiple threads can enter here
        no_merchantable = processes.get_no_merchantable_item_ids()
        cache.set("no_merchantable", no_merchantable, 5 * 60)
    return no_merchantable


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

    def _get_user_items(self, cursor, user, items):
        where, having, param_where, param_having = self._where_items_amount(items)

        no_merchantable = get_no_merchantable_item_ids()

        sql = """
            SELECT
                source.nameid,
                source.refine,
                source.card0,
                source.card1,
                source.card2,
                source.card3,
                item.type,
                SUM(source.amount) AS total_amount,
                destination.amount
            FROM """ + self.table + """ AS source
            INNER JOIN """ + self.item_table + """ AS item ON
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
                source.attribute = 0 AND
                source.account_id = %s AND
                source.nameid NOT IN (""" + ','.join(['%s'] * len(no_merchantable)) + """) AND
                (""" + where + """)
            GROUP BY nameid, refine, card0, card1, card2, card3
            HAVING (""" + having + ")"

        parameters = [user.pk, user.pk]
        parameters.extend(no_merchantable)
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
            params = [
                item['nameid'],
                item['refine'],
                item['card0'],
                item['card1'],
                item['card2'],
                item['card3']
            ]
            param_where.extend(params)
            param_having.extend(params)
            param_having.append(item['amount'])

        where = ' OR '.join(where)
        having = ' OR '.join(having)
        return where, having, param_where, param_having

    def _get_destination_size(self, cursor, user):
        cursor.execute("""SELECT COUNT(*)
                FROM """ + self.destination_table + """ AS destination
                WHERE
                    account_id = %s
        """, [
            user.pk
        ])
        return int(cursor.fetchone()[0])

    def _get_items(self, cursor, user, items):
        self._get_user_items(cursor, user, items)
        if cursor.rowcount != len(items):
            raise ConflictError("You don't have those items.")  # TODO Verbose error.
        try:
            items = relate_items_rows(cursor.fetchall(), items)
        except TypeError:
            raise ConflictError("You don't have those items.")  # TODO Verbose error.
        self._check_conditions(items, self._get_destination_size(cursor, user))
        return items

    def _check_conditions(self, items, destination_size):
        required_size = 0

        for item in items:
            if item['type'] not in [4, 5, 7, 8, 12]:
                if item['destination_amount'] + item['amount'] > self.max_stack:
                    raise ConflictError("Stack limit. You can't stack more than %d items." % self.max_stack)
                if item['destination_amount'] <= 0:
                    required_size += 1
            else:
                required_size += item['amount']

        if required_size + destination_size > self.max_rows:
            raise ConflictError("Storage limit. You can't store more than %s items." % self.max_rows)

    def check_items(self, user, items):
        from django.db import connection

        cursor = connection.cursor()
        self._get_items(cursor, user, items)

    def move_items(self, user, items):
        from django.db import connection

        cursor = connection.cursor()
        try:
            cursor.execute("""
                    LOCK TABLES
                    `char` LOW_PRIORITY WRITE,
                    `""" + self.table + """` AS source LOW_PRIORITY WRITE,
                    `""" + self.table + """` LOW_PRIORITY WRITE,
                    `""" + self.item_table + """` AS item LOW_PRIORITY WRITE,
                    `""" + self.destination_table + """` AS destination LOW_PRIORITY WRITE,
                    `""" + self.destination_table + """` LOW_PRIORITY WRITE""")
            check_no_char_online(cursor, user)

            for item in self._get_items(cursor, user, items):
                if item['type'] in [4, 5, 7, 8, 12]:
                    self._add_no_stackable_item_vending_storage(cursor, user, item)
                    self._remove_no_stackable_item_storage(cursor, user, item)
                else:
                    # Add to source
                    if item['destination_amount'] is 0:
                        self._add_item_to_destination_insert(cursor, user, item)
                    else:
                        self._add_item_to_destination_update(cursor, user, item)
                    # Remove to destination
                    if item['source_amount'] == item['amount']:
                        self._remove_item_to_source_delete(cursor, user, item)
                    else:
                        self._remove_item_to_source_update(cursor, user, item)
        finally:
            cursor.execute("UNLOCK TABLES")

    @property
    def max_rows(self):
        return settings.MAX_STORAGE

    @property
    def max_stack(self):
        return settings.MAX_AMOUNT

    @property
    def item_table(self):
        return settings.ITEM_TABLE_NAME

    @property
    def table(self):
        raise NotImplementedError("Please, implement this method")

    @property
    def destination_table(self):
        raise NotImplementedError("Please, implement this method")


class StorageManager(BaseStorageManager):
    def get_queryset(self):
        return super(StorageManager, self).get_queryset().filter(bound='0', expire_time='0', attribute='0') \
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

    def get_storage(self, user_id):
        from django.db import connection
        cursor = connection.cursor()

        no_merchantable = get_no_merchantable_item_ids()

        sql = """
            SELECT
                source.nameid,
                source.refine,
                source.card0,
                source.card1,
                source.card2,
                source.card3,
                SUM(source.amount) AS total_amount
            FROM storage AS source
            WHERE
                source.bound = 0 AND
                source.expire_time = 0 AND
                source.identify != 0 AND
                source.attribute = 0 AND
                source.account_id = %s AND
                source.nameid NOT IN (""" + ','.join(['%s'] * len(no_merchantable)) + """)
            GROUP BY nameid, refine, card0, card1, card2, card3
            """

        parameters = [user_id]
        parameters.extend(no_merchantable)

        cursor.execute(sql, parameters)
        result_list = []
        for row in cursor.fetchall():
            result_list.append({
                "nameid": row[0],
                "refine": row[1],
                "card0": row[2],
                "card1": row[3],
                "card2": row[4],
                "card3": row[5],
                "amount": row[6],
            })
        return result_list


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


class CharManager(models.Manager):
    blacksmith_jobs = [10, 4011, 4033, 4058, 4064, 4100]
    alchemist_jobs = [18, 4019, 4041, 4071, 4078, 4107]

    def blacksmith_fame(self):
        return self.fame(self.blacksmith_jobs)

    def alchemist_fame(self):
        return self.fame(self.alchemist_jobs)

    def fame(self, jobs):
        return self.get_queryset().filter(job__in=jobs, fame__gt=0).order_by('-fame')[:settings.MAX_FAME_LIST]
