from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator
from django.db import models
from django.contrib.auth.models import BaseUserManager, update_last_login
from django.utils.crypto import salted_hmac
from rest_framework.exceptions import ValidationError

from zeny_plugin.app.exceptions import ConflictError
from zeny_plugin.app.managers import StorageManager, VendingManager


# FIXME This is really ugly
user_logged_in.disconnect(update_last_login)


def strictly_positive(value):
    if value <= 0:
        raise ValidationError('%s is not strictly positive' % value)


class User(models.Model):
    id = models.PositiveIntegerField(primary_key=True, db_column="account_id")
    name = models.CharField(max_length=23, unique=True, db_column="userid")
    user_pass = models.CharField(max_length=32)
    sex = models.CharField(max_length=1)
    email = models.CharField(max_length=39)
    group_id = models.IntegerField()
    state = models.IntegerField()
    unban_time = models.IntegerField()
    expiration_time = models.IntegerField()
    logincount = models.IntegerField()
    lastlogin = models.DateTimeField()
    last_ip = models.CharField(max_length=100)
    birthdate = models.DateField()
    character_slots = models.IntegerField()
    pincode = models.CharField(max_length=4)
    pincode_change = models.IntegerField()
    bank_vault = models.IntegerField()
    vip_time = models.IntegerField()
    old_group = models.IntegerField()

    last_login = None
    is_active = True

    objects = BaseUserManager()

    USERNAME_FIELD = 'name'

    class Meta:
        managed = False
        db_table = 'login'

    def set_password(self, raw_password):
        self.user_pass = raw_password

    def check_password(self, raw_password):
        return self.user_pass == raw_password

    REQUIRED_FIELDS = []

    def get_username(self):
        """Return the identifying username for this User"""
        return self.name

    def __str__(self):
        return self.get_username()

    def natural_key(self):
        return (self.get_username(),)

    def is_anonymous(self):
        """
        Always returns False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    def set_unusable_password(self):
        raise NotImplementedError('Not supported')

    def has_usable_password(self):
        raise NotImplementedError('Not supported')

    def get_full_name(self):
        raise NotImplementedError('Not supported')

    def get_short_name(self):
        raise NotImplementedError('Not supported')

    def get_session_auth_hash(self):
        """
        Returns an HMAC of the password field.
        """
        key_salt = "django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash"
        return salted_hmac(key_salt, self.user_pass).hexdigest()

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @staticmethod
    def add_zeny(cursor, user_id, zeny):
        cursor.execute("""INSERT INTO `zeny` (id, zeny) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE zeny = zeny + %s
        """, [
            user_id,
            zeny,
            zeny,
        ])

    @staticmethod
    def remove_zeny(cursor, user_id, zeny):
        cursor.execute("""UPDATE `zeny` SET zeny = zeny - %s WHERE id = %s""", [
            zeny,
            user_id,
        ])

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: No, always
        return False

    @property
    def online(self):
        return self.chars.exclude(online=0).exists()

    @property
    def zeny(self):
        try:
            zeny = self.zeny_vending.zeny
        except ObjectDoesNotExist:
            zeny = 0
        return zeny

    def buy(self, data, seller):
        from django.db import connection

        try:
            stackable = Item.objects.get(id=data['nameid']).stackable
        except ObjectDoesNotExist:
            raise ValidationError("The item doesn't exist.")

        cursor = connection.cursor()

        try:
            cursor.execute("""
                    LOCK TABLES
                    `storage_vending` WRITE,
                    `storage_vending` AS source WRITE,
                    `zeny` WRITE""")
            seller_current, buyer_current = self.current_item_state(cursor, seller, data)

            if seller_current is None:
                raise ValidationError("The seller doesn't have this item.")
            if seller_current['amount'] < data['amount']:
                raise ValidationError("The seller doesn't have enough items.")
            if seller_current['zeny'] != data['zeny']:
                raise ValidationError("The seller sells the item %s zeny." % seller_current['zeny'])

            if stackable:
                if buyer_current['amount'] == 0:
                    self.can_add(cursor, 1)
                elif buyer_current['amount'] + data['amount'] > settings.MAX_AMOUNT:
                    raise ConflictError("Stack limit. You can't stack more than %d items." % settings.MAX_AMOUNT)
            else:
                self.can_add(cursor, data['amount'])

            cursor.execute("SELECT id, zeny FROM `zeny` WHERE id = %s OR id = %s", [self.pk, seller.pk])
            buyer_zeny = 0
            seller_zeny = 0
            for item in cursor.fetchall():
                if int(item[0]) == self.pk:
                    buyer_zeny = int(item[1])
                else:
                    seller_zeny = int(item[1])
            bill_zeny = data['amount'] * data['zeny']
            if buyer_zeny < bill_zeny:
                raise ConflictError("You don't have so much money.")
            if seller_zeny + bill_zeny > settings.MAX_ZENY:
                raise ConflictError("Seller can't have so much money. Limit %d." % settings.MAX_ZENY)

            if stackable:
                if buyer_current['amount'] > 0:
                    Vending.update_amount_stackable_item(cursor, self.pk, data['amount'], data)
                    if seller_current['amount'] == data['amount']:
                        Vending.delete_stackable_item(cursor, seller.pk, data)
                    else:
                        Vending.update_amount_stackable_item(cursor, seller.pk, -data['amount'], data)
                else:
                    if seller_current['amount'] == data['amount']:
                        Vending.change_owner_stakable_items(cursor, self.pk, seller.pk, data)
                    else:
                        Vending.copy_stackable_item(cursor, self.pk, seller.pk, data['amount'], data)
                        Vending.update_amount_stackable_item(cursor, seller.pk, -data['amount'], data)
            else:
                Vending.change_owner_no_stakable_items(cursor, self.pk, seller.pk, buyer_current['zeny'], data['amount'], data)
            User.remove_zeny(cursor, self.pk, bill_zeny)
            User.add_zeny(cursor, seller.pk, bill_zeny)
        finally:
            cursor.execute("UNLOCK TABLES")

        log = VendingLog(
            seller_id=seller.pk,
            buyer_id=self.pk,
            **data
        )
        log.save()

    def current_item_state(self, cursor, seller, item):
        cursor.execute("""
            SELECT account_id, SUM(amount), MAX(zeny)
            FROM storage_vending
            WHERE
                (account_id = %s OR account_id = %s) AND
                nameid = %s AND
                refine = %s AND
                card0 = %s AND
                card1 = %s AND
                card2 = %s AND
                card3 = %s
            GROUP BY account_id, nameid, refine, card0, card1, card2, card3
        """, [
            seller.pk,
            self.pk,
            item['nameid'],
            item['refine'],
            item['card0'],
            item['card1'],
            item['card2'],
            item['card3'],
        ])
        seller_current = None
        buyer_current = None
        for item in cursor.fetchall():
            d = {
                'amount': int(item[1]),
                'zeny': int(item[2]),
            }
            if int(item[0]) == seller.pk:
                seller_current = d
            else:
                buyer_current = d
        if buyer_current is None:
            buyer_current = {
                'amount': 0,
                'zeny': 0,
            }

        return seller_current, buyer_current

    def can_add(self, cursor, amount):
        cursor.execute("""
            SELECT COUNT(*)
            FROM storage_vending
            WHERE account_id = %s
        """, [
            self.pk
        ])
        if int(cursor.fetchone()[0]) + amount > settings.MAX_STORAGE:
            raise ConflictError("Storage limit. You can't store more than %s items." % settings.MAX_STORAGE)


class Char(models.Model):
    id = models.PositiveIntegerField(primary_key=True, db_column="char_id")
    account = models.ForeignKey(User, related_name="chars", db_column="account_id")
    char_num = models.IntegerField()
    name = models.CharField(unique=True, max_length=30)
    class_field = models.IntegerField(db_column='class')  # Field renamed because it was a Python reserved word.
    base_level = models.IntegerField()
    job_level = models.IntegerField()
    base_exp = models.BigIntegerField()
    job_exp = models.BigIntegerField()
    zeny = models.IntegerField()
    str = models.IntegerField()
    agi = models.IntegerField()
    vit = models.IntegerField()
    int = models.IntegerField()
    dex = models.IntegerField()
    luk = models.IntegerField()
    max_hp = models.IntegerField()
    hp = models.IntegerField()
    max_sp = models.IntegerField()
    sp = models.IntegerField()
    status_point = models.IntegerField()
    skill_point = models.IntegerField()
    option = models.IntegerField()
    karma = models.IntegerField()
    manner = models.IntegerField()
    party_id = models.IntegerField()
    guild_id = models.IntegerField()
    pet_id = models.IntegerField()
    homun_id = models.IntegerField()
    elemental_id = models.IntegerField()
    hair = models.IntegerField()
    hair_color = models.IntegerField()
    clothes_color = models.IntegerField()
    weapon = models.IntegerField()
    shield = models.IntegerField()
    head_top = models.IntegerField()
    head_mid = models.IntegerField()
    head_bottom = models.IntegerField()
    robe = models.IntegerField()
    last_map = models.CharField(max_length=11)
    last_x = models.IntegerField()
    last_y = models.IntegerField()
    save_map = models.CharField(max_length=11)
    save_x = models.IntegerField()
    save_y = models.IntegerField()
    partner_id = models.IntegerField()
    online = models.IntegerField()
    father = models.IntegerField()
    mother = models.IntegerField()
    child = models.IntegerField()
    fame = models.IntegerField()
    rename = models.IntegerField()
    delete_date = models.IntegerField()
    moves = models.IntegerField()
    unban_time = models.IntegerField()
    font = models.IntegerField()
    uniqueitem_counter = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'char'

    def move_zeny(self, zeny):
        Char.check_zeny(zeny, self.zeny, self.account.zeny, self.name)

        user_id = self.account_id

        from django.db import connection

        cursor = connection.cursor()
        try:
            cursor.execute("""
                    LOCK TABLES
                    `char` LOW_PRIORITY WRITE,
                    `zeny` LOW_PRIORITY WRITE""")

            cursor.execute("SELECT zeny FROM `char` WHERE char_id = %s AND online = 0", [self.id])
            if cursor.rowcount == 0:
                raise ConflictError("You're connected to the server with the PJ %s, please disconnect and retry."
                                    % self.name)
            char_zeny = cursor.fetchone()[0]
            cursor.execute("SELECT zeny FROM `zeny` WHERE id = %s", [user_id])
            if cursor.rowcount == 0:
                user_zeny = 0
            else:
                user_zeny = int(cursor.fetchone()[0])
            Char.check_zeny(zeny, char_zeny, user_zeny, self.name)
            if zeny < 0:
                User.add_zeny(cursor, user_id, -zeny)
                self._remove_zeny(cursor, -zeny)
            else:
                self._add_zeny(cursor, zeny)
                User.remove_zeny(cursor, user_id, zeny)
        finally:
            cursor.execute("UNLOCK TABLES")

    def _add_zeny(self, cursor, zeny):
        Char.add_zeny(cursor, self.pk, zeny)

    @staticmethod
    def add_zeny(cursor, char_id, zeny):
        cursor.execute("""UPDATE `char` SET zeny = zeny + %s WHERE char_id = %s""", [
            zeny,
            char_id,
        ])

    def _remove_zeny(self, cursor, zeny):
        Char.remove_zeny(cursor, self.pk, zeny)

    @staticmethod
    def remove_zeny(cursor, char_id, zeny):
        cursor.execute("""UPDATE `char` SET zeny = zeny - %s WHERE char_id = %s""", [
            zeny,
            char_id,
        ])

    @staticmethod
    def check_zeny(zeny, char_zeny, user_zeny, char_name):
        if zeny < 0:
            if char_zeny < -zeny:
                raise ConflictError("%s doesn't have so much money." % char_name)
            if user_zeny + -zeny > settings.MAX_ZENY:
                raise ConflictError("You can't have so much money. Limit %d." % settings.MAX_ZENY)
        else:
            if char_zeny < zeny:
                raise ConflictError("You don't have so much money.")
            if user_zeny + zeny > settings.MAX_ZENY:
                raise ConflictError("%s can't have so much money. Limit %d." % (char_name, settings.MAX_ZENY))


class Storage(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    account = models.ForeignKey(User, related_name="storage", db_column="account_id")
    nameid = models.IntegerField()
    amount = models.PositiveIntegerField(validators=[strictly_positive, MaxValueValidator(settings.MAX_AMOUNT)])
    equip = models.IntegerField()
    identify = models.IntegerField()
    refine = models.IntegerField()
    attribute = models.IntegerField()
    card0 = models.IntegerField()
    card1 = models.IntegerField()
    card2 = models.IntegerField()
    card3 = models.IntegerField()
    expire_time = models.IntegerField()
    bound = models.IntegerField()
    unique_id = models.BigIntegerField()

    objects = StorageManager()

    class Meta:
        managed = False
        db_table = 'storage'


class Vending(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    account = models.ForeignKey(User, related_name="vending", db_column="account_id")
    nameid = models.IntegerField()
    amount = models.PositiveIntegerField(validators=[strictly_positive, MaxValueValidator(settings.MAX_AMOUNT)])
    equip = models.IntegerField()
    identify = models.IntegerField()
    refine = models.IntegerField()
    attribute = models.IntegerField()
    card0 = models.IntegerField()
    card1 = models.IntegerField()
    card2 = models.IntegerField()
    card3 = models.IntegerField()
    expire_time = models.IntegerField()
    bound = models.IntegerField()
    unique_id = models.BigIntegerField()
    zeny = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(settings.MAX_ZENY)])

    objects = VendingManager()

    class Meta:
        managed = False
        db_table = 'storage_vending'

    @staticmethod
    def copy_stackable_item(cursor, new_owner_id, old_owner_id, amount, item):
        cursor.execute("""INSERT INTO storage_vending
                (account_id, nameid, amount, equip, identify, refine, attribute, card0, card1, card2, card3, expire_time, bound, unique_id, zeny)
                (
                    SELECT %s, nameid, %s, equip, identify, refine, attribute, card0, card1, card2, card3, expire_time, bound, unique_id, 0
                    FROM storage_vending AS source
                    WHERE
                    account_id = %s AND
                    nameid = %s AND
                    refine = %s AND
                    card0 = %s AND
                    card1 = %s AND
                    card2 = %s AND
                    card3 = %s
                )""", [
            new_owner_id,
            amount,
            old_owner_id,
            item['nameid'],
            item['refine'],
            item['card0'],
            item['card1'],
            item['card2'],
            item['card3']
        ])

    @staticmethod
    def update_amount_stackable_item(cursor, user_id, amount, item):
        cursor.execute("""UPDATE storage_vending SET amount = amount + %s
            WHERE
                account_id = %s AND
                nameid = %s AND
                refine = %s AND
                card0 = %s AND
                card1 = %s AND
                card2 = %s AND
                card3 = %s
            """, [
            amount,
            user_id,
            item['nameid'],
            item['refine'],
            item['card0'],
            item['card1'],
            item['card2'],
            item['card3'],
        ])

    @staticmethod
    def change_owner_stakable_items(cursor, new_owner_id, old_owner_id, item):
        cursor.execute("""UPDATE storage_vending SET account_id = %s, zeny = 0
            WHERE
                account_id = %s AND
                nameid = %s AND
                refine = %s AND
                card0 = %s AND
                card1 = %s AND
                card2 = %s AND
                card3 = %s
            """, [
            new_owner_id,
            old_owner_id,
            item['nameid'],
            item['refine'],
            item['card0'],
            item['card1'],
            item['card2'],
            item['card3'],
        ])

    @staticmethod
    def delete_stackable_item(cursor, user_id, item):
        cursor.execute("""DELETE FROM storage_vending
            WHERE
                account_id = %s AND
                nameid = %s AND
                refine = %s AND
                card0 = %s AND
                card1 = %s AND
                card2 = %s AND
                card3 = %s
            """, [
            user_id,
            item['nameid'],
            item['refine'],
            item['card0'],
            item['card1'],
            item['card2'],
            item['card3'],
        ])

    @staticmethod
    def change_owner_no_stakable_items(cursor, new_owner_id, old_owner_id, new_zeny, amount, item):
        cursor.execute("""UPDATE storage_vending SET account_id = %s, zeny = %s
            WHERE
                account_id = %s AND
                nameid = %s AND
                refine = %s AND
                card0 = %s AND
                card1 = %s AND
                card2 = %s AND
                card3 = %s
            LIMIT %s""", [
            new_owner_id,
            new_zeny,
            old_owner_id,
            item['nameid'],
            item['refine'],
            item['card0'],
            item['card1'],
            item['card2'],
            item['card3'],
            amount,
        ])


class Zeny(models.Model):
    id = models.OneToOneField(User, related_name="zeny_vending", primary_key=True, db_column="id")
    zeny = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(settings.MAX_ZENY)])

    class Meta:
        managed = False
        db_table = 'zeny'


class Item(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    type = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = settings.ITEM_TABLE_NAME

    @property
    def stackable(self):
        return self.type not in [4, 5, 7, 8, 12]


class VendingLog(models.Model):
    id = models.AutoField(primary_key=True)
    seller = models.ForeignKey(User, related_name="sales", db_column="seller_account_id")
    buyer = models.ForeignKey(User, related_name="shopping", db_column="buyer_account_id")
    nameid = models.IntegerField()
    refine = models.IntegerField()
    card0 = models.IntegerField()
    card1 = models.IntegerField()
    card2 = models.IntegerField()
    card3 = models.IntegerField()
    amount = models.PositiveIntegerField(validators=[strictly_positive, MaxValueValidator(settings.MAX_AMOUNT)])
    zeny = models.PositiveIntegerField(validators=[strictly_positive, MaxValueValidator(settings.MAX_ZENY)])
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'vending_log'
