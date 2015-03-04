from django.db import models
from rest_framework.exceptions import ValidationError


class StorageManager(models.Manager):
    def get_queryset(self):
        return super(StorageManager, self).get_queryset().filter(bound='0', expire_time='0', ).exclude(identify='0')

    def check_items(self, user, items):
        from django.db import connection

        cursor = connection.cursor()
        cursor.execute(*self.check_items_sql(user, items))
        if cursor.rowcount != len(items):
            raise ValidationError("You doesn't have this items.")  # TODO Verbose error. 409?

    @staticmethod
    def check_items_sql(user, items):
        where = []
        having = []
        param_where = []
        param_having = []
        for item in items:
            where.append(
                '(nameid = %s AND refine = %s AND attribute = %s AND card0 = %s AND card1 = %s AND card2 = %s AND card3 = %s)')
            having.append(
                '(nameid = %s AND refine = %s AND attribute = %s AND card0 = %s AND card1 = %s AND card2 = %s AND card3 = %s AND total_amount >= %s)')
            params = [item['nameid'], item['refine'], item['attribute'], item['card0'], item['card1'], item['card2'],
                      item['card3']]
            param_where.extend(params)
            param_having.extend(params)
            param_having.append(item['amount'])

        where = ' OR '.join(where)
        having = ' OR '.join(having)
        sql = """
            SELECT nameid, refine, attribute, card0, card1, card2, card3, SUM(amount) as total_amount, COUNT(id) as rows
            FROM storage
            WHERE bound = 0 AND expire_time = 0 AND identify != 0
            AND account_id = %s AND (""" + where + """)
            GROUP BY nameid, refine, attribute, card0, card1, card2, card3
            HAVING (""" + having + ")"

        parameters = [user.pk]
        parameters.extend(param_where)
        parameters.extend(param_having)

        return [sql, parameters]